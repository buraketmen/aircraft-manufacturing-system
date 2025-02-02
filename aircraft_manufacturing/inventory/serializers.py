from typing import Optional
from rest_framework import serializers
from accounts.models import TeamMember
from accounts.serializers import TeamTypeSerializer
from .models import Part, PartType, TeamPartPermission
from accounts.utils import get_user_display_name


class PartTypeSerializer(serializers.ModelSerializer):
    """Serializer for PartType model"""
    class Meta:
        model = PartType
        fields = ('id', 'name', 'description', 'created_at', 'updated_at')
        ordering = ['name']


class TeamPartPermissionSerializer(serializers.ModelSerializer):
    """Serializer for TeamPartPermission model"""
    team_type_details = TeamTypeSerializer(source='team_type', read_only=True)
    part_type_details = PartTypeSerializer(source='part_type', read_only=True)

    class Meta:
        model = TeamPartPermission
        fields = ('id', 'team_type', 'team_type_details', 'part_type', 'part_type_details', 
                 'can_create', 'created_at', 'updated_at')
        ordering = ['team_type', 'part_type']


class PartSerializer(serializers.ModelSerializer):
    """Serializer for Part model"""
    part_type_name = serializers.CharField(source='part_type.name', read_only=True)
    aircraft_type_name = serializers.CharField(source='aircraft_type.name', read_only=True)
    aircraft_type_details = serializers.SerializerMethodField()
    owner_name = serializers.SerializerMethodField()
    owner_team = serializers.CharField(source='owner.team.name', read_only=True)

    class Meta:
        model = Part
        fields = [
            'id',
            'serial_number',
            'part_type',
            'part_type_name',
            'aircraft_type',
            'aircraft_type_name',
            'aircraft_type_details',
            'owner',
            'owner_name',
            'owner_team',
            'is_used',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['serial_number', 'owner', 'created_at', 'updated_at']
        extra_kwargs = {
            'part_type': {'required': False} # Avoid required validation error
        }

    def get_owner_name(self, obj: Part) -> Optional[str]:
        """Get the owner's display name"""
        if obj.owner and obj.owner.user:
            return get_user_display_name(obj.owner.user)
        return None

    def get_aircraft_type_details(self, obj: Part) -> Optional[dict]:
        """Get the aircraft type details"""
        if obj.aircraft_type:
            from assembly.serializers import AircraftTypeSerializer
            return AircraftTypeSerializer(obj.aircraft_type).data
        return None

    def validate(self, data):
        """
        Validate that the part can only be produced by team members with proper permissions
        """
        team_member: Optional[TeamMember] = getattr(self.context['request'].user, 'teammember', None)
        if not team_member:
            raise serializers.ValidationError("You are not a member of any team")

        # Check if team has permission to create this type of part
        has_permission = TeamPartPermission.objects.filter(
            team_type=team_member.team.team_type,
            part_type=data['part_type'],
            can_create=True
        ).exists()

        if not has_permission:
            raise serializers.ValidationError(
                f"Your team does not have permission to create parts of type {data['part_type'].name}"
            )

        return data

    def create(self, validated_data):
        # Set the owner to the current team member
        team_member = getattr(self.context['request'].user, 'teammember', None)
        validated_data['owner'] = team_member
        
        return super().create(validated_data)