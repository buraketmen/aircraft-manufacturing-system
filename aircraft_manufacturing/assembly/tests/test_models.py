from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from assembly.models import AircraftType, Aircraft, AircraftPart, AircraftPartRequirement
from inventory.models import Part, PartType
from accounts.models import TeamType, Team, TeamMember
from accounts.constants import TeamTypes

class AircraftTypeTests(TestCase):
    def test_aircraft_type_creation(self):
        """Test that an aircraft type can be created with valid data"""
        aircraft_type = AircraftType.objects.create(
            name="Test Aircraft",
            description="Test Description"
        )
        self.assertEqual(aircraft_type.name, "Test Aircraft")
        self.assertEqual(aircraft_type.description, "Test Description")

    def test_aircraft_type_unique_name(self):
        """Test that aircraft type names must be unique"""
        AircraftType.objects.create(name="Test Aircraft")
        with self.assertRaises(IntegrityError):
            AircraftType.objects.create(name="Test Aircraft")

    def test_aircraft_type_str(self):
        """Test the string representation of an aircraft type"""
        aircraft_type = AircraftType.objects.create(name="Test Aircraft")
        self.assertEqual(str(aircraft_type), "Test Aircraft")

class AircraftTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        # Create necessary team structure
        cls.team_type = TeamType.objects.create(name=TeamTypes.ASSEMBLY)
        cls.team = Team.objects.create(
            team_type=cls.team_type,
            name="Test Assembly Team"
        )
        cls.user = User.objects.create_user(username="testuser", password="testpass")
        cls.team_member = TeamMember.objects.create(user=cls.user, team=cls.team)
        
        # Create aircraft type and parts
        cls.aircraft_type = AircraftType.objects.create(name="Test Aircraft Type")
        cls.part_type = PartType.objects.create(name="Test Part Type")
        cls.part = Part.objects.create(
            part_type=cls.part_type,
            aircraft_type=cls.aircraft_type,
            serial_number="PART001"
        )

    def test_aircraft_creation(self):
        """Test that an aircraft can be created with valid data"""
        aircraft = Aircraft.objects.create(
            aircraft_type=self.aircraft_type,
            serial_number="TEST001",
            owner=self.team_member
        )
        self.assertEqual(aircraft.aircraft_type, self.aircraft_type)
        self.assertEqual(aircraft.serial_number, "TEST001")

    def test_aircraft_unique_serial(self):
        """Test that aircraft serial numbers must be unique"""
        Aircraft.objects.create(
            aircraft_type=self.aircraft_type,
            serial_number="TEST001",
            owner=self.team_member
        )
        with self.assertRaises(IntegrityError):
            Aircraft.objects.create(
                aircraft_type=self.aircraft_type,
                serial_number="TEST001",
                owner=self.team_member
            )

    def test_aircraft_auto_serial(self):
        """Test that aircraft gets auto-generated serial if none provided"""
        aircraft = Aircraft.objects.create(
            aircraft_type=self.aircraft_type,
            owner=self.team_member
        )
        self.assertRegex(aircraft.serial_number, r'^A-[A-F0-9]{8}$')

    def test_aircraft_str(self):
        """Test the string representation of an aircraft"""
        aircraft = Aircraft.objects.create(
            aircraft_type=self.aircraft_type,
            serial_number="TEST001",
            owner=self.team_member
        )
        expected = f"{self.aircraft_type.name} - TEST001"
        self.assertEqual(str(aircraft), expected)

class AircraftPartTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        # Create team structure
        cls.team_type = TeamType.objects.create(name=TeamTypes.ASSEMBLY)
        cls.team = Team.objects.create(team_type=cls.team_type, name="Test Team")
        cls.user = User.objects.create_user(username="testuser", password="testpass")
        cls.team_member = TeamMember.objects.create(user=cls.user, team=cls.team)
        
        # Create aircraft and parts
        cls.aircraft_type = AircraftType.objects.create(name="Test Aircraft")
        cls.part_type = PartType.objects.create(name="Test Part")
        cls.aircraft = Aircraft.objects.create(
            aircraft_type=cls.aircraft_type,
            serial_number="TEST001",
            owner=cls.team_member
        )
        cls.part = Part.objects.create(
            part_type=cls.part_type,
            aircraft_type=cls.aircraft_type,
            serial_number="PART001"
        )

    def test_aircraft_part_creation(self):
        """Test that an aircraft part relationship can be created"""
        aircraft_part = AircraftPart.objects.create(
            aircraft=self.aircraft,
            part=self.part
        )
        self.assertEqual(aircraft_part.aircraft, self.aircraft)
        self.assertEqual(aircraft_part.part, self.part)

    def test_part_unique_use(self):
        """Test that a part can only be used in one aircraft"""
        AircraftPart.objects.create(aircraft=self.aircraft, part=self.part)
        
        another_aircraft = Aircraft.objects.create(
            aircraft_type=self.aircraft_type,
            serial_number="TEST002",
            owner=self.team_member
        )
        
        with self.assertRaises(IntegrityError):
            AircraftPart.objects.create(aircraft=another_aircraft, part=self.part)

class AircraftPartRequirementTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        cls.aircraft_type = AircraftType.objects.create(name="Test Aircraft")
        cls.part_type = PartType.objects.create(name="Test Part")

    def test_requirement_creation(self):
        """Test that a part requirement can be created"""
        requirement = AircraftPartRequirement.objects.create(
            aircraft_type=self.aircraft_type,
            part_type=self.part_type,
            quantity=2
        )
        self.assertEqual(requirement.quantity, 2)

    def test_unique_requirement(self):
        """Test that requirements must be unique per aircraft type and part type"""
        AircraftPartRequirement.objects.create(
            aircraft_type=self.aircraft_type,
            part_type=self.part_type,
            quantity=2
        )
        with self.assertRaises(IntegrityError):
            AircraftPartRequirement.objects.create(
                aircraft_type=self.aircraft_type,
                part_type=self.part_type,
                quantity=3
            )

    def test_requirement_str(self):
        """Test the string representation of a requirement"""
        requirement = AircraftPartRequirement.objects.create(
            aircraft_type=self.aircraft_type,
            part_type=self.part_type,
            quantity=2
        )
        expected = f"{self.aircraft_type.name} - {self.part_type.name} (2)"
        self.assertEqual(str(requirement), expected)
