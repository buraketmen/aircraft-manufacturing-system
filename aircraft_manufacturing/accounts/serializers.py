from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Team, TeamMember, TeamType
from accounts.utils import get_user_display_name


class UserSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'date_joined', 'display_name')

    def get_display_name(self, obj):
        # use "display_name"
        return get_user_display_name(user=obj)


class TeamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamType
        fields = ('id', 'name', 'created_at')
        ordering = ['name']


class TeamSerializer(serializers.ModelSerializer):
    team_type_name = serializers.CharField(source='team_type.name', read_only=True)

    class Meta:
        model = Team
        fields = ('id', 'team_type', 'team_type_name', 'name', 'description', 'created_at', 'updated_at')
        ordering = ['team_type', 'name']


class TeamMemberSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    team_name = serializers.CharField(source='team.name', read_only=True)
    team_type_name = serializers.CharField(source='team.team_type.name', read_only=True)

    class Meta:
        model = TeamMember
        fields = ('id', 'user', 'team', 'team_name', 'team_type_name', 'created_at', 'updated_at')
        ordering = ['-created_at']