from rest_framework import serializers
from .models import Restaurants, Menus, Indicators, NumericalIndicators, CategoricalIndicators, CensusTracts
from django.db import models

class NutrientRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NumericalIndicators
        fields = '__all__'

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurants
        fields = '__all__'
        
class MenusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menus
        fields = '__all__'
    
class IndicatorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicators
        fields = '__all__'