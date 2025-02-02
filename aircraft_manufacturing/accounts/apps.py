"""Configuration for accounts app."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.conf import settings
from aircraft_manufacturing.logger import django_logger

def create_initial_team_types(sender, **kwargs):
    """Create default team types if they don't exist."""
    from .models import TeamType
    from .constants import TeamTypes

    default_team_types = TeamTypes().__dict__.values()
    for name in default_team_types:
        team_type, created = TeamType.objects.get_or_create(name=name)
        if created:
            django_logger.info(f"TeamType {name} created successfully.")

def create_initial_teams(sender, **kwargs):
    """Create default teams if they don't exist."""
    from .models import Team, TeamType

    # Create a default team for each team type
    for team_type in TeamType.objects.all():
        team, created = Team.objects.get_or_create(
            team_type=team_type,
            name=f"{team_type.name} Team",
            defaults={'description': f'Team for {team_type.name}'}
        )
        if created:
            django_logger.info(f"Team {team.name} created successfully.")

def create_initial_team_users(sender, **kwargs):
    """Create default users for each team if they don't exist."""
    from django.contrib.auth import get_user_model
    from .models import Team, TeamMember
    from .constants import DEFAULT_TEAM_USERS, TeamTypes
            
    User = get_user_model()
    
    for team_type_name, users in DEFAULT_TEAM_USERS.items():
        try:
            team = Team.objects.get(name=f"{team_type_name} Team")
            if team_type_name == TeamTypes.ADMIN:
                for username, first_name, last_name, password in users:
                    if not User.objects.filter(username=username).exists():
                        admin_user = User.objects.create_superuser(
                            username=username,
                            password=password,
                            first_name=first_name,
                            last_name=last_name
                        )
                        TeamMember.objects.create(user=admin_user, team=team)
                        django_logger.info(f"Admin user {username} created successfully.")
                continue
            
            for username, first_name, last_name, password in users:
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(
                        username=username,
                        password=password,
                        first_name=first_name,
                        last_name=last_name
                    )
                    TeamMember.objects.create(user=user, team=team)
                    django_logger.info(f"User {username} created successfully.")
        except Team.DoesNotExist:
            django_logger.error(f"Team {team_type_name} Team does not exist.")


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'User & Team Management'

    def ready(self):
        """
        Connect signals when the app is ready.
        This method is called once when Django starts.
        """
        # Skip automatic creation during tests or when explicitly disabled
        if getattr(settings, 'SKIP_INITIAL_DATA', False):
            return
            
        post_migrate.connect(create_initial_team_types, sender=self)
        post_migrate.connect(create_initial_teams, sender=self)
        post_migrate.connect(create_initial_team_users, sender=self)
