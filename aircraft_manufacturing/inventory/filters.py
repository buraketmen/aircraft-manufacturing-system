from django_filters import rest_framework as django_filters
from accounts.models import TeamType
from assembly.models import AircraftType
from .models import Part, PartType, TeamPartPermission


class PartTypeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    created_at_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = PartType
        fields = ['name', 'description', 'created_at_after', 'created_at_before']


class TeamPartPermissionFilter(django_filters.FilterSet):
    team_type = django_filters.ModelChoiceFilter(queryset=TeamType.objects.all())
    team_type_name = django_filters.CharFilter(field_name='team_type__name', lookup_expr='icontains')
    part_type = django_filters.ModelChoiceFilter(queryset=PartType.objects.all())
    part_type_name = django_filters.CharFilter(field_name='part_type__name', lookup_expr='icontains')
    can_create = django_filters.BooleanFilter()

    class Meta:
        model = TeamPartPermission
        fields = ['team_type', 'team_type_name', 'part_type', 'part_type_name', 'can_create']


class PartFilter(django_filters.FilterSet):
    part_type = django_filters.CharFilter(field_name='part_type__name')
    part_type_name = django_filters.CharFilter(field_name='part_type__name', lookup_expr='icontains')
    aircraft_type = django_filters.ModelChoiceFilter(queryset=AircraftType.objects.all())
    aircraft_type_name = django_filters.CharFilter(field_name='aircraft_type__name', lookup_expr='icontains')
    owner_team_type_name = django_filters.CharFilter(field_name='owner__team__team_type__name', lookup_expr='icontains')
    owner_team_name = django_filters.CharFilter(field_name='owner__team__name', lookup_expr='icontains')
    is_used = django_filters.BooleanFilter()
    created_at_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Part
        fields = ['part_type', 'part_type_name', 'aircraft_type', 'aircraft_type_name',
                 'owner_team_type_name', 'owner_team_name',
                 'is_used', 'created_at_after', 'created_at_before']
