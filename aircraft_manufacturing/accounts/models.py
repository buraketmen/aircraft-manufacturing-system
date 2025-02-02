from __future__ import annotations
from typing import TYPE_CHECKING
from django.db import models
from django.contrib.auth.models import User
from .constants import TeamTypes
if TYPE_CHECKING:
    from inventory.models import PartType


class TeamType(models.Model):
    """Model to store team types"""
    name = models.CharField(max_length=64, unique=True, help_text="Name of the team type")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time of creation")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Team(models.Model):
    """Team model representing different manufacturing teams"""
    team_type = models.ForeignKey(TeamType, on_delete=models.PROTECT, help_text="Type of the team")
    name = models.CharField(max_length=64, help_text="Name of the team", unique=True)
    description = models.TextField(blank=True, help_text="Description of the team")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time of creation")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time of last update")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        unique_together = ['team_type', 'name']
        ordering = ['team_type', 'name']

    def get_name_display(self):
        return self.name.capitalize()

    def is_assembly_team(self) -> bool:
        """Check if the team is assembly team"""
        return self.team_type.name == TeamTypes.ASSEMBLY
    
    def is_admin_team(self) -> bool:
        """Check if the team is admin team"""
        return self.team_type.name == TeamTypes.ADMIN
    
    def can_create_aircraft(self) -> bool:
        """Check if the team is allowed to create aircrafts"""
        return self.is_assembly_team()

    def can_create_part(self, part_type: PartType) -> bool:
        """Check if the team is allowed to create a specific part type"""
        from inventory.models import TeamPartPermission
        return TeamPartPermission.objects.filter(
                team_type=self.team_type,
                part_type=part_type,
                can_create=True
            ).exists()

    def has_create_perm(self) -> bool:
        """Check if the team is allowed to create parts"""
        from inventory.models import TeamPartPermission
        return TeamPartPermission.objects.filter(
                team_type=self.team_type,
                can_create=True
            ).exists()


class TeamMember(models.Model):
    """Team member model representing personnel assigned to teams"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teammember', help_text="User profile")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members', help_text="Team name")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time of creation")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time of last update")

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.team}"