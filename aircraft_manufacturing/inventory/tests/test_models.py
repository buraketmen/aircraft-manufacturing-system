from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from inventory.models import PartType, TeamPartPermission, Part
from accounts.models import TeamType, Team, TeamMember
from accounts.constants import TeamTypes
from assembly.models import AircraftType

class PartTypeTests(TestCase):
    def test_part_type_creation(self):
        """Test that a part type can be created with valid data"""
        part_type = PartType.objects.create(
            name="Test Part Type",
            description="Test Description"
        )
        self.assertEqual(part_type.name, "Test Part Type")
        self.assertEqual(part_type.description, "Test Description")

    def test_part_type_unique_name(self):
        """Test that part type names must be unique"""
        PartType.objects.create(name="Test Part Type")
        with self.assertRaises(IntegrityError):
            PartType.objects.create(name="Test Part Type")

    def test_part_type_str(self):
        """Test the string representation of a part type"""
        part_type = PartType.objects.create(name="Test Part Type")
        self.assertEqual(str(part_type), "Test Part Type")

class TeamPartPermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        cls.team_type = TeamType.objects.create(name=TeamTypes.ASSEMBLY)
        cls.part_type = PartType.objects.create(name="Test Part Type")

    def test_team_part_permission_creation(self):
        """Test that a team part permission can be created"""
        permission = TeamPartPermission.objects.create(
            team_type=self.team_type,
            part_type=self.part_type,
            can_create=True
        )
        self.assertTrue(permission.can_create)

    def test_unique_team_part_permission(self):
        """Test that permissions must be unique per team type and part type"""
        TeamPartPermission.objects.create(
            team_type=self.team_type,
            part_type=self.part_type,
            can_create=True
        )
        with self.assertRaises(IntegrityError):
            TeamPartPermission.objects.create(
                team_type=self.team_type,
                part_type=self.part_type,
                can_create=False
            )

    def test_team_part_permission_str(self):
        """Test the string representation of a team part permission"""
        permission = TeamPartPermission.objects.create(
            team_type=self.team_type,
            part_type=self.part_type
        )
        expected = f"{self.team_type.name} - {self.part_type.name}"
        self.assertEqual(str(permission), expected)

class PartTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        # Create team structure
        cls.team_type = TeamType.objects.create(name=TeamTypes.ASSEMBLY)
        cls.team = Team.objects.create(
            team_type=cls.team_type,
            name="Test Team"
        )
        cls.user = User.objects.create_user(username="testuser", password="testpass")
        cls.team_member = TeamMember.objects.create(user=cls.user, team=cls.team)

        # Create necessary types
        cls.part_type = PartType.objects.create(name="Test Part Type")
        cls.aircraft_type = AircraftType.objects.create(name="Test Aircraft Type")
        
        # Create permission
        cls.permission = TeamPartPermission.objects.create(
            team_type=cls.team_type,
            part_type=cls.part_type,
            can_create=True
        )

    def test_part_creation(self):
        """Test that a part can be created with valid data"""
        part = Part.objects.create(
            part_type=self.part_type,
            aircraft_type=self.aircraft_type,
            owner=self.team_member,
            serial_number="TEST001"
        )
        self.assertEqual(part.serial_number, "TEST001")
        self.assertFalse(part.is_used)

    def test_part_auto_serial(self):
        """Test that part gets auto-generated serial if none provided"""
        part = Part.objects.create(
            part_type=self.part_type,
            aircraft_type=self.aircraft_type,
            owner=self.team_member
        )
        self.assertRegex(part.serial_number, r'^P-[A-F0-9]{8}$')

    def test_part_creation_permission(self):
        """Test that parts can only be produced by team members with permission"""
        # Create new team type without permission
        new_team_type = TeamType.objects.create(name="NO_PERMISSION")
        new_team = Team.objects.create(team_type=new_team_type, name="No Permission Team")
        new_member = TeamMember.objects.create(
            user=User.objects.create_user(username="noperm", password="testpass"),
            team=new_team
        )

        # Attempt to create part with unauthorized team member
        with self.assertRaises(ValidationError):
            Part.objects.create(
                part_type=self.part_type,
                aircraft_type=self.aircraft_type,
                owner=new_member
            )

    def test_part_unique_serial(self):
        """Test that part serial numbers must be unique"""
        Part.objects.create(
            part_type=self.part_type,
            aircraft_type=self.aircraft_type,
            owner=self.team_member,
            serial_number="TEST001"
        )
        with self.assertRaises(IntegrityError):
            Part.objects.create(
                part_type=self.part_type,
                aircraft_type=self.aircraft_type,
                owner=self.team_member,
                serial_number="TEST001"
            )

    def test_part_delete_protection(self):
        """Test that used parts cannot be deleted"""
        part = Part.objects.create(
            part_type=self.part_type,
            aircraft_type=self.aircraft_type,
            owner=self.team_member
        )
        
        # Mark part as used
        part.is_used = True
        part.save()

        # Attempt to delete used part
        with self.assertRaises(ValidationError):
            part.delete()

        # Verify part still exists
        self.assertTrue(Part.objects.filter(id=part.id).exists())

    def test_part_str(self):
        """Test the string representation of a part"""
        part = Part.objects.create(
            part_type=self.part_type,
            aircraft_type=self.aircraft_type,
            owner=self.team_member,
            serial_number="TEST001"
        )
        expected = f"{self.aircraft_type.name} - {self.part_type.name} (TEST001)"
        self.assertEqual(str(part), expected)
