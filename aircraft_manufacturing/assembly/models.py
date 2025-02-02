from __future__ import annotations
from typing import TYPE_CHECKING
from django.db import models
from django.db import transaction
import uuid
if TYPE_CHECKING:
    from accounts.models import TeamMember

class AircraftType(models.Model):
    """Model to store aircraft types"""
    name = models.CharField(max_length=64, unique=True, help_text="Name of the aircraft type")
    description = models.TextField(blank=True, help_text="Description of the aircraft type")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time of creation")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time of last update")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class AircraftPart(models.Model):
    """Model to track parts used in aircraft assembly"""
    aircraft = models.ForeignKey(
        'Aircraft',
        on_delete=models.CASCADE,
        related_name='used_parts',
        help_text="Aircraft model"
    )
    part = models.OneToOneField(
        'inventory.Part',
        on_delete=models.PROTECT,
        related_name='used_in',
        help_text="Part of the aircraft"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time of creation")

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Aircraft Part'
        verbose_name_plural = 'Aircraft Parts'

    def __str__(self):
        return f"{self.part.part_type.name} for {self.aircraft.aircraft_type.name} - {self.aircraft.serial_number}"

class Aircraft(models.Model):
    """Aircraft model representing assembled aircrafts"""
    aircraft_type = models.ForeignKey(AircraftType, on_delete=models.PROTECT, help_text="Type of the aircraft")
    serial_number = models.CharField(max_length=64, unique=True, help_text="Serial number of the aircraft")
    parts = models.ManyToManyField('inventory.Part', through=AircraftPart, related_name='used_in_aircraft', help_text="Parts used in the aircraft")
    owner = models.ForeignKey('accounts.TeamMember', on_delete=models.PROTECT, help_text="Team member who created the aircraft")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time of creation")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time of last update")

    def __str__(self):
        return f"{self.aircraft_type.name} - {self.serial_number}"

    def check_create_perm(self) -> None:
        if not self.owner:
            raise PermissionError("Aircraft owner is required to assemble an aircraft")
        self.owner: TeamMember
        if not self.owner.team.can_create_aircraft():
            raise PermissionError("Have no permission to assemble aircraft")

    def create_serial_number(self) -> str:
        self.serial_number = f"A-{uuid.uuid4().hex[:8].upper()}"
        if Aircraft.objects.filter(serial_number=self.serial_number).exists():
            self.create_serial_number()

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.check_create_perm()
        if not self.serial_number:
            self.create_serial_number()
        super().save(*args, **kwargs)

class AircraftPartRequirement(models.Model):
    """Model to store required parts for each aircraft type"""
    aircraft_type = models.ForeignKey(AircraftType, on_delete=models.CASCADE, help_text="Type of the aircraft")
    part_type = models.ForeignKey('inventory.PartType', on_delete=models.PROTECT, help_text="Type of the part")
    quantity = models.PositiveIntegerField(help_text="Number of parts required")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time of creation")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time of last update")

    class Meta:
        unique_together = ['aircraft_type', 'part_type']
        ordering = ['aircraft_type', 'part_type']

    def __str__(self):
        return f"{self.aircraft_type.name} - {self.part_type.name} ({self.quantity})"
