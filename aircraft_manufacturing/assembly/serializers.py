from rest_framework import serializers
from .models import Aircraft, AircraftPart, AircraftType
from accounts.utils import get_user_display_name
from typing import Optional


class AircraftTypeSerializer(serializers.ModelSerializer):
    """Serializer for AircraftType model"""
    class Meta:
        model = AircraftType
        fields = ('id', 'name', 'description', 'created_at', 'updated_at')
        ordering = ['name']


class AircraftPartSerializer(serializers.ModelSerializer):
    """Serializer for AircraftPart model"""
    part_details = serializers.SerializerMethodField()
    
    class Meta:
        model = AircraftPart
        fields = ['id', 'part', 'part_details', 'created_at']
        read_only_fields = ['created_at']

    def get_part_details(self, obj):
        from inventory.serializers import PartSerializer
        return PartSerializer(obj.part).data


class AircraftSerializer(serializers.ModelSerializer):
    """Serializer for Aircraft model"""
    aircraft_type_name = serializers.CharField(source='aircraft_type.name', read_only=True)
    used_parts = AircraftPartSerializer(many=True, read_only=True)
    owner_name = serializers.SerializerMethodField()
    owner_team = serializers.CharField(source='owner.team.name', read_only=True)
    
    class Meta:
        model = Aircraft
        fields = [
            'id',
            'serial_number', 
            'aircraft_type', 
            'aircraft_type_name', 
            'serial_number',
            'owner',
            'owner_name',
            'owner_team',
            'used_parts',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['serial_number','owner', 'created_at', 'updated_at', 'serial_number']

    def get_owner_name(self, obj: Aircraft) -> Optional[str]:
        """Get the owner's display name"""
        if obj.owner and obj.owner.user:
            return get_user_display_name(obj.owner.user)
        return None

    def create(self, validated_data):
        request = self.context.get('request')
        team_member = getattr(request.user, 'teammember', None)
        validated_data['owner'] = team_member
        return super().create(validated_data)