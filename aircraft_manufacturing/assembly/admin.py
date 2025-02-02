from django.contrib import admin
from .models import Aircraft, AircraftPart, AircraftType, AircraftPartRequirement


@admin.register(AircraftType)
class AircraftTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    date_hierarchy = 'created_at'


class AircraftPartInline(admin.TabularInline):
    model = AircraftPart
    extra = 0
    raw_id_fields = ['part']


@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ['aircraft_type', 'serial_number',  'created_at']
    list_filter = ['aircraft_type',  'created_at']
    search_fields = ['aircraft_type__name', 'serial_number']
    date_hierarchy = 'created_at'
    inlines = [AircraftPartInline]


@admin.register(AircraftPart)
class AircraftPartAdmin(admin.ModelAdmin):
    list_display = ['aircraft', 'part', 'created_at']
    list_filter = ['aircraft__aircraft_type', 'part__part_type', 'created_at']
    search_fields = ['aircraft__aircraft_type__name', 'part__part_type__name']
    date_hierarchy = 'created_at'
    raw_id_fields = ['aircraft', 'part']


@admin.register(AircraftPartRequirement)
class AircraftPartRequirementAdmin(admin.ModelAdmin):
    list_display = ['aircraft_type', 'part_type', 'quantity', 'created_at']
    list_filter = ['aircraft_type', 'part_type', 'created_at']
    search_fields = ['aircraft_type__name', 'part_type__name']
    date_hierarchy = 'created_at'