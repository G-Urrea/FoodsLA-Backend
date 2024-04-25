# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.gis.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class CategoricalIndicators(models.Model):
    id = models.BigAutoField(primary_key=True)
    indicator = models.ForeignKey('Indicators', models.DO_NOTHING)
    category = models.TextField()
    tract = models.ForeignKey('CensusTracts', models.DO_NOTHING, to_field='geoid')
    order_value = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'categorical_indicators'


class CensusTracts(models.Model):

    affgeoid = models.TextField(blank=True, null=True)
    geoid = models.TextField(unique=True)
    name = models.TextField(blank=True, null=True)
    namelsad = models.TextField(blank=True, null=True)
    lsad = models.TextField(blank=True, null=True)
    geo_type = models.TextField()
    geometry = models.GeometryField()

    class Meta:
        managed = False
        db_table = 'census_tracts'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Facilities(models.Model):
    id = models.BigAutoField(primary_key=True)
    restaurant = models.ForeignKey('Restaurants', models.DO_NOTHING, to_field='establishment_id')
    tract_id = models.TextField(blank=True, null=True)
    location = models.GeometryField(srid=4326, blank=True, null=True)
    facility_name = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'facilities'


class Indicators(models.Model):
    id = models.BigIntegerField(primary_key=True)
    indicator_short = models.TextField(unique=True)
    description = models.TextField()
    indicator = models.TextField()
    category = models.TextField()
    type = models.TextField()
    data_value_type = models.TextField()
    measure = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'indicators'


class Menus(models.Model):
    menu_id = models.BigAutoField(primary_key=True)
    establishment_id = models.TextField()
    menu = models.TextField(blank=True, null=True)
    rrr = models.FloatField()
    rrr_upper_ci = models.FloatField(blank=True, null=True)
    rrr_lower_ci = models.FloatField(blank=True, null=True)
    category = models.TextField(blank=True, null = True)

    class Meta:
        managed = False
        db_table = 'menus'


class NumericalIndicators(models.Model):
    id = models.BigAutoField(primary_key=True)
    indicator = models.ForeignKey(Indicators, models.DO_NOTHING)
    value = models.FloatField(blank=True, null=True)
    tract = models.ForeignKey(CensusTracts, models.DO_NOTHING, to_field='geoid')

    class Meta:
        managed = False
        db_table = 'numerical_indicators'


class Restaurants(models.Model):
    establishment_id = models.TextField(unique=True)
    rnd = models.FloatField(blank=True, null=True)
    rrr_max = models.FloatField(blank=True, null=True)
    rrr_min = models.FloatField(blank=True, null=True)
    rrr_std = models.FloatField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    chain = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'restaurants'
