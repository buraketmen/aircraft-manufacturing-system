from django_filters import rest_framework as django_filters
from django.contrib.auth.models import User
from accounts.models import Team, TeamMember, TeamType


class TeamTypeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    created_at_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = TeamType
        fields = ['name', 'description', 'created_at_after', 'created_at_before']


class TeamFilter(django_filters.FilterSet):
    team_type = django_filters.ModelChoiceFilter(queryset=TeamType.objects.all())
    team_type_name = django_filters.CharFilter(field_name='team_type__name', lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    created_at_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Team
        fields = ['team_type', 'team_type_name', 'name', 'description', 'created_at_after', 'created_at_before']


class TeamMemberFilter(django_filters.FilterSet):
    team = django_filters.ModelChoiceFilter(queryset=Team.objects.all())
    team_type = django_filters.ModelChoiceFilter(field_name='team__team_type', queryset=TeamType.objects.all())
    team_name = django_filters.CharFilter(field_name='team__name', lookup_expr='icontains')
    team_type_name = django_filters.CharFilter(field_name='team__team_type__name', lookup_expr='icontains')
    user_email = django_filters.CharFilter(field_name='user__email', lookup_expr='icontains')
    user_username = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')

    class Meta:
        model = TeamMember
        fields = ['team', 'team_type', 'team_name', 'team_type_name', 'user_email', 'user_username']


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    is_staff = django_filters.BooleanFilter()
    team_type = django_filters.ModelChoiceFilter(field_name='teammember__team__team_type', queryset=TeamType.objects.all())
    team_type_name = django_filters.CharFilter(field_name='teammember__team__team_type__name', lookup_expr='icontains')
    team_name = django_filters.CharFilter(field_name='teammember__team__name', lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['username', 'email', 'is_active', 'is_staff', 'team_type', 'team_type_name', 'team_name']