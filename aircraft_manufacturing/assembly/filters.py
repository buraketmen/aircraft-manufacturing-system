from django_filters import rest_framework as django_filters
from accounts.models import Team
from .models import Aircraft, AircraftType


class AircraftTypeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    created_at_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = AircraftType
        fields = ['name', 'description', 'created_at_after', 'created_at_before']


class AircraftFilter(django_filters.FilterSet):
    aircraft_type = django_filters.ModelChoiceFilter(queryset=AircraftType.objects.all())
    aircraft_type_name = django_filters.CharFilter(field_name='aircraft_type__name', lookup_expr='icontains')
    serial_number = django_filters.CharFilter(lookup_expr='icontains')
    assembled_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    assembled_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Aircraft
        fields = ['aircraft_type', 'aircraft_type_name', 'serial_number', 
                 'assembled_after', 'assembled_before']