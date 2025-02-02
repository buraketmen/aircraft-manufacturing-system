"""Configuration for assembly app."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from aircraft_manufacturing.logger import django_logger
from .constants import DEFAULT_AIRCRAFT_REQUIRED_PARTS
from django.conf import settings

def create_initial_aircraft_types(sender, **kwargs):
    """Create default aircraft types if they don't exist."""
    from .models import AircraftType
    from .constants import DefaultAircraftTypes

    default_aircraft_types = DefaultAircraftTypes().__dict__.values()
    for name in default_aircraft_types:
        _, created = AircraftType.objects.get_or_create(
            name=name,
            defaults={'description': f'Default aircraft type for {name}'}
        )
        if created:
            django_logger.info(f"AircraftType {name} created successfully.")

def create_initial_part_requirements(sender, **kwargs):
    """Create default part requirements for each aircraft type if they don't exist."""
    from .models import AircraftType, AircraftPartRequirement
    from inventory.models import PartType

    # Get all aircraft types and part types
    aircraft_types = AircraftType.objects.all()
    part_types = PartType.objects.all()

    # Create part requirements based on DEFAULT_AIRCRAFT_REQUIRED_PARTS
    for aircraft_type in aircraft_types:
        for part_type in part_types:
            quantity = DEFAULT_AIRCRAFT_REQUIRED_PARTS.get(aircraft_type.name, {}).get(part_type.name, 0)
            if quantity > 0:
                AircraftPartRequirement.objects.get_or_create(
                    aircraft_type=aircraft_type,
                    part_type=part_type,
                    defaults={'quantity': quantity}
                )

class AssemblyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'assembly'
    verbose_name = 'Aircraft Assembly'

    def ready(self):
        """
        Connect signals when the app is ready.
        This method is called once when Django starts.
        """

        if getattr(settings, 'SKIP_INITIAL_DATA', False):
            return

        post_migrate.connect(create_initial_aircraft_types, sender=self)
        post_migrate.connect(create_initial_part_requirements, sender=self)
