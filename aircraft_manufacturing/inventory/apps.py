"""Configuration for inventory app."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from aircraft_manufacturing.logger import django_logger
from .constants import DefaultPartTypes
from django.conf import settings

def create_initial_part_types(sender, **kwargs):
    """Create default part types if they don't exist."""
    from .models import PartType

    default_part_types = DefaultPartTypes().__dict__.values()
    for name in default_part_types:
        _, created = PartType.objects.get_or_create(
            name=name,
            defaults={'description': f'Default part type for {name}'}
        )
        if created:
            django_logger.info(f"PartType {name} created successfully.")

def create_initial_team_part_permissions(sender, **kwargs):
    """Create default team part permissions if they don't exist."""
    from .models import PartType, TeamPartPermission
    from accounts.models import TeamType
    from accounts.constants import TeamTypes

    # Get all team types and part types
    team_types = TeamType.objects.all()
    part_types = PartType.objects.all()

    RESPONSIBLE_TEAMS = {
        DefaultPartTypes.WING: TeamTypes.WING,
        DefaultPartTypes.BODY: TeamTypes.BODY,
        DefaultPartTypes.TAIL: TeamTypes.TAIL,
        DefaultPartTypes.AVIONICS: TeamTypes.AVIONICS,
    }

    for team_type in team_types:
        for part_type in part_types:
            can_create = RESPONSIBLE_TEAMS.get(part_type.name) == team_type.name
            _, created = TeamPartPermission.objects.get_or_create(
                team_type=team_type,
                part_type=part_type,
                defaults={'can_create': can_create}
            )
            if created:
                django_logger.info(
                    f"{team_type.name} Team"
                    f"{'can' if can_create else 'cannot'} create {part_type.name} parts"
                )

class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'
    verbose_name = 'Parts Inventory'

    def ready(self):
        """
        Connect signals when the app is ready.
        This method is called once when Django starts.
        """
        if getattr(settings, 'SKIP_INITIAL_DATA', False):
            return
        post_migrate.connect(create_initial_part_types, sender=self)
        post_migrate.connect(create_initial_team_part_permissions, sender=self)
