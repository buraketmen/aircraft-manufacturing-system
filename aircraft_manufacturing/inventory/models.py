from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import TeamMember, TeamType
from assembly.models import AircraftType
import uuid


class PartType(models.Model):
    """Model to store part types"""
    name = models.CharField(max_length=64, unique=True, help_text="Name of the part type")
    description = models.TextField(blank=True, help_text="Description of the part type")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time of creation")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time of last update")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class TeamPartPermission(models.Model):
    """Model to store which teams can create which parts"""
    team_type = models.ForeignKey(TeamType, on_delete=models.CASCADE, help_text="Type of the team")
    part_type = models.ForeignKey(PartType, on_delete=models.CASCADE, help_text="Type of the part")
    can_create = models.BooleanField(default=False, help_text="Whether the team can create this type of part")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time of creation")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time of last update")

    def __str__(self):
        return f"{self.team_type.name} - {self.part_type.name}"

    class Meta:
        unique_together = ['team_type', 'part_type']
        ordering = ['team_type', 'part_type']


class Part(models.Model):
    """Part model representing aircraft components"""
    part_type = models.ForeignKey(PartType, on_delete=models.PROTECT, help_text="Type of the part")
    aircraft_type = models.ForeignKey(AircraftType, on_delete=models.PROTECT, help_text="Type of the aircraft this part belongs to")
    owner = models.ForeignKey(TeamMember, on_delete=models.SET_NULL, null=True, help_text="Team member who produced this part")
    is_used = models.BooleanField(default=False, help_text="Whether this part is used in an aircraft")
    serial_number = models.CharField(max_length=64, unique=True, help_text="Serial number of the part", null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time of creation")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time of last update")

    def __str__(self):
        return f"{self.aircraft_type.name} - {self.part_type.name} ({self.serial_number})"

    def clean(self):
        """Validate that the part can only be produced by team members of the corresponding team"""
        if self.owner:
            permission = TeamPartPermission.objects.filter(
                team_type=self.owner.team.team_type,
                part_type=self.part_type,
                can_create=True
            ).exists()
            
            if not permission:
                raise ValidationError(
                    f"Team member from {self.owner.team.team_type.name} "
                    f"cannot create {self.part_type.name} parts"
                )

    def check_create_perm(self) -> None:
        """Check if the team member has permission to create this part"""
        if not self.owner:
            raise PermissionError("Part owner is required to create a part")
        self.owner: TeamMember
        if not self.owner.team.can_create_part(part_type=self.part_type):
            raise PermissionError("Have no permission to create parts")

    def create_serial_number(self):
        """Create a unique serial number for the part"""
        self.serial_number = f"P-{uuid.uuid4().hex[:8].upper()}"
        if Part.objects.filter(serial_number=self.serial_number).exists():
            self.create_serial_number()

    def save(self, *args, **kwargs):
        self.check_create_perm()
        if not self.serial_number:
            self.create_serial_number()
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_used:
            raise ValidationError("Cannot delete a part that is used in an aircraft")
        super().delete(*args, **kwargs)
