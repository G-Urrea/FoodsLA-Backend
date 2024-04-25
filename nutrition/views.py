from rest_framework import generics
from django.db.models import F, OuterRef, FloatField, Subquery, Func, Max, Min
from django.db.models.functions import Cast
from .models import  Menus, NumericalIndicators, CategoricalIndicators, Facilities, Indicators, CensusTracts, Restaurants
from .serializers import MenusSerializer, IndicatorsSerializer
from django.contrib.gis.db.models.functions import AsGeoJSON
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.

class RestaurantListCreateView(APIView):

    def get_queryset(self):
        # Solución parcial: Obtener solamente en condado de Los Angeles

        queryset = Facilities.objects.all()
        queryset= queryset.prefetch_related('restaurant')
        

        limit = self.request.query_params.get('limit')
        tract_id = self.request.query_params.get('tract_id')

        if tract_id is None:
            geo_la = CensusTracts.objects.get(geoid= '06037').geometry
            queryset = queryset.filter(location__within= geo_la)

        if tract_id is not None:
            tract_geometry = CensusTracts.objects.get(geoid = tract_id).geometry
            queryset = queryset.filter(location__within = tract_geometry)

        if limit is not None:
            queryset = queryset[:int(limit)]

        return queryset   
    
    def get(self, request, format=None):
         
         queryset = self.get_queryset()
         # No se utiliza serializer para mejorar performance, se debe serializar en Frontend
         related_fields =['rnd', 'rrr_max', 'rrr_min', 'rrr_std', "name",
                "chain"]
         fields = ['facility_name', 'establishment_id']
         geojson = queryset.annotate(
             rnd = F('restaurant__rnd'),
             rrr_max = F('restaurant__rrr_max'),
             rrr_min = F('restaurant__rrr_min'),
             rrr_std = F('restaurant__rrr_std'),
             chain = F('restaurant__chain'),
             name = F('restaurant__name'),
             establishment_id = F('restaurant')
         )
         if request.query_params.get('gis') is not None:
             geojson = geojson.annotate(geometry=AsGeoJSON('location'))
             fields +=['geometry']
         else:
            geojson = geojson.annotate(
                lat=Func('location',function='ST_Y', output_field=FloatField()),
                long =Func('location',function='ST_X', output_field=FloatField())
                )
            fields +=['lat', 'long']
        
         geojson = geojson.values(*(fields+related_fields))
         data = list(geojson)
         return Response(data = data)
                
class CensusTractDensityListCreateView(APIView):

    def get_queryset(self):

        geo_la = CensusTracts.objects.get(geoid= '06037').geometry
        county_filter = CensusTracts.objects.filter(geometry__within=geo_la)
        county_tracts = county_filter.values_list('geoid', flat=True)

        county_numind = NumericalIndicators.objects.filter(tract_id__in=county_tracts)

        # NumericalIndicators.objects
        subquery_min = county_numind.filter(indicator_id=44)
        subquery_min = subquery_min.annotate(rnd_min=F('value'))

        subquery_fend = county_numind.filter(tract = OuterRef('tract')).filter(indicator_id=0)
        subquery_fend = subquery_fend.annotate(fend=F('value'))

        subquery_std = county_numind.filter(tract = OuterRef('tract')).filter(indicator_id=50)
        subquery_std = subquery_std.annotate(rnd_std=F('value'))

        # Combinar las subconsultas
        subquery_max = county_numind.filter(tract = OuterRef('tract')).filter(indicator_id=45)
        subquery_max = subquery_max.annotate(rnd_max=F('value'))


        combined_qs = subquery_min.annotate(
            rnd_max = Cast(Subquery(subquery_max.values('rnd_max')[:1]), output_field=FloatField() ),
            rnd_std = Cast(Subquery(subquery_std.values('rnd_std')[:1]), output_field=FloatField() ),
            fend = Cast(Subquery(subquery_fend.values('fend')[:1]), output_field=FloatField() )
        ).select_related('tract')
        
        queryset = combined_qs

        geo_type = self.request.query_params.get('geo_type')
        if geo_type is not None:
            queryset = queryset.filter(tract__geo_type=geo_type)

        limit = self.request.query_params.get('limit')
        if limit is not None:
            queryset = queryset[:int(limit)]
        return queryset
    
    def get(self, request):
         queryset = self.get_queryset()
         # No se utiliza serializer para mejorar performance, se debe serializar en Frontend
         related_fields = ["namelsad", 'geo_type']
         fields = ['rnd_min', 'rnd_max', 'rnd_std', 'fend', 'tract']
         geojson = queryset.annotate(
             namelsad = F('tract__namelsad'),
             geo_type = F('tract__geo_type')
         )
         if request.query_params.get('gis') is not None:
             geojson = geojson.annotate(geometry=AsGeoJSON('tract__geometry'))
             fields +=['geometry']

         geojson = geojson.values(*(fields+related_fields))
         data = list(geojson)
         return Response(data = data)


class MenusList(generics.ListCreateAPIView):
    
    serializer_class = MenusSerializer


    def get_queryset(self):
        queryset = Menus.objects.all()
        distribution = self.request.query_params.get('distribution')
        

        establishment_ids = self.request.query_params.getlist('establishment_id', [])
        
        if len(establishment_ids) > 0:
            queryset = queryset.filter(establishment_id__in = establishment_ids)

        geoid = self.request.query_params.get('geoid')

        if geoid is None:
            geo_la = CensusTracts.objects.get(geoid= '06037').geometry
            facilities = Facilities.objects.filter(location__within= geo_la).values_list('restaurant', flat=True)
            queryset = queryset.filter(establishment_id__in=facilities)

        if geoid is not None:
            tract_geometry = CensusTracts.objects.get(geoid = geoid).geometry
            facilities = Facilities.objects.filter(location__within = tract_geometry).values_list('restaurant_id', flat=True).distinct()
            queryset = queryset.filter(establishment_id__in=facilities)
        
        if distribution is not None:
            geo_la = CensusTracts.objects.get(geoid= '06037').geometry
            facilities = Facilities.objects.filter(location__within= geo_la).values_list('restaurant', flat=True)
            queryset = Restaurants.objects.filter(establishment_id__in=facilities)
            
            min_rrr = queryset.aggregate(Min('rrr_min'))
            queryset = queryset.aggregate(Max('rrr_max'))
            
            queryset['rrr__max'] = queryset['rrr_max__max']
            queryset['rrr__min'] = min_rrr['rrr_min__min']

        return queryset
    
    def get(self, request):
        
        if self.request.query_params.get('distribution') is not None:
             data = self.get_queryset()
             return Response(data = data)
             
        
        return super().get(request)

         
class IndicatorsList(generics.ListCreateAPIView):

    serializer_class = IndicatorsSerializer

    def get_queryset(self):
        queryset = Indicators.objects.all()
        

        if self.request.query_params.get('available') is not None:
            numerical_query_set = NumericalIndicators.objects.all()
            categoric_query_set = CategoricalIndicators.objects.all()
            geo_type = self.request.query_params.get('geo_type')
            if self.request.query_params.get('geo_type') is not None:
                numerical_query_set = numerical_query_set.select_related('tract').filter(tract__geo_type=geo_type)
                categoric_query_set = categoric_query_set.select_related('tract').filter(tract__geo_type=geo_type)
            numeric_ids = numerical_query_set.values_list('indicator_id', flat=True).distinct()
            cat_ids = categoric_query_set.values_list('indicator_id', flat=True).distinct()
            available_ids = list(cat_ids)+ list(numeric_ids)
            available_ids.sort()
            queryset = queryset.filter(id__in=available_ids)

        return queryset

class NumericalIndicatorsPlotList(generics.ListCreateAPIView):
    #serializer_class = NumIndSerializer

    def get_queryset(self):


        queryset = NumericalIndicators.objects.select_related()

        geo_la = CensusTracts.objects.get(geoid= '06037').geometry
        county_filter = CensusTracts.objects.filter(geometry__within=geo_la)
        county_tracts = county_filter.values_list('geoid', flat=True)

        queryset = queryset.filter(tract_id__in=county_tracts)

        indicator_id = self.request.query_params.get('indicator_id')
        if indicator_id is not None:
            queryset = queryset.filter(indicator__id=indicator_id)

        geo_type = self.request.query_params.get('geo_type')
        if geo_type is not None:
            queryset = queryset.filter(tract__geo_type = geo_type)
        return queryset
    
    def get(self, request):
         queryset = self.get_queryset()
         # No se utiliza serializer por errores con este
         related_fields = ["namelsad", 'geo_type', 'id', 'indicator_short', 'description', 'indicator',
                            'indicator_name','indicator_category', 'type', 'measure', 'data_value_type']
        
         fields = ['value', 'indicator', 'tract']
         json = queryset.annotate(
            namelsad = F('tract__namelsad'),
            geo_type = F('tract__geo_type'),
            indicator_short = F('indicator__indicator_short'),
            description = F('indicator__description'),
            indicator_name = F('indicator__indicator'),
            indicator_category = F('indicator__category'),
            data_value_type = F('indicator__data_value_type'),
            type = F('indicator__type'),
            measure = F('indicator__measure')
         )

        
         json = json.values(*(fields+related_fields))
         data = list(json)
        
         return Response(data = data)
        
    
    
class CategoricalIndicatorsPlotList(generics.ListCreateAPIView):
   # serializer_class = CatIndSerializer

    def get_queryset(self):
        queryset = CategoricalIndicators.objects.select_related()

        geo_la = CensusTracts.objects.get(geoid= '06037').geometry
        county_filter = CensusTracts.objects.filter(geometry__within=geo_la)
        county_tracts = county_filter.values_list('geoid', flat=True)

        queryset = queryset.filter(tract_id__in=county_tracts)

        indicator_id = self.request.query_params.get('indicator_id')
        if indicator_id is not None:
            queryset = queryset.filter(indicator__id=indicator_id)

        geo_type = self.request.query_params.get('geo_type')
        if geo_type is not None:
            queryset = queryset.filter(tract__geo_type = geo_type)
            
        return queryset

    
    def get(self, request):
         queryset = self.get_queryset()
         # No se utiliza serializer por errores con este
         related_fields = ["namelsad", 'geo_type', 'id', 'indicator_short', 'description', 'indicator',
                            'indicator_name', 'indicator_category', 'type', 'measure', 'data_value_type']
        
         fields = ['value', 'indicator', 'tract', 'order_value']
         json = queryset.annotate(
            value = F('category'),
            namelsad = F('tract__namelsad'),
            geo_type = F('tract__geo_type'),
            indicator_short = F('indicator__indicator_short'),
            description = F('indicator__description'),
            indicator_name = F('indicator__indicator'),
            indicator_category = F('indicator__category'),
            data_value_type = F('indicator__data_value_type'),
            type = F('indicator__type'),
            measure = F('indicator__measure')
         )

        
         json = json.values(*(fields+related_fields))
         data = list(json)
        
         return Response(data = data)