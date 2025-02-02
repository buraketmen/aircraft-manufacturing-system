from django.contrib import admin
from .models import Part, PartType, TeamPartPermission


@admin.register(PartType)
class PartTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    date_hierarchy = 'created_at'


@admin.register(TeamPartPermission)
class TeamPartPermissionAdmin(admin.ModelAdmin):
    list_display = ['team_type', 'part_type', 'can_create', 'created_at']
    list_filter = ['team_type', 'part_type', 'can_create', 'created_at']
    search_fields = ['team_type__name', 'part_type__name']
    date_hierarchy = 'created_at'


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ['part_type', 'aircraft_type', 'owner', 'is_used', 'created_at']
    list_filter = ['part_type', 'aircraft_type', 'owner__team', 'is_used', 'created_at']
    search_fields = ['part_type__name', 'aircraft_type__name', 'owner__user__username']
    date_hierarchy = 'created_at'
    raw_id_fields = ['owner']
    readonly_fields = ['is_used']
