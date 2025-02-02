from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from accounts.models import TeamType, Team, TeamMember
from accounts.constants import TeamTypes

class TeamTypeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        cls.assembly_type, created = TeamType.objects.get_or_create(
            name=TeamTypes.ASSEMBLY,
        )
        cls.admin_type, created = TeamType.objects.get_or_create(
            name=TeamTypes.ADMIN,
        )

    def test_team_type_creation(self):
        """Test that a team type can be created with valid data"""
        team_type = TeamType.objects.create(
            name="Manufacturing",
        )
        self.assertEqual(team_type.name, "Manufacturing")

    def test_team_type_unique_name(self):
        """Test that team type names must be unique"""
        with self.assertRaises(IntegrityError):
            TeamType.objects.create(name=TeamTypes.ASSEMBLY)

    def test_team_type_str(self):
        """Test the string representation of a team type"""
        self.assertEqual(str(self.assembly_type), TeamTypes.ASSEMBLY)
        self.assertEqual(str(self.admin_type), TeamTypes.ADMIN)

class TeamTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        cls.assembly_type, created = TeamType.objects.get_or_create(
            name=TeamTypes.ASSEMBLY,
        )
        cls.admin_type, created = TeamType.objects.get_or_create(
            name=TeamTypes.ADMIN,
        )

    def setUp(self):
        """Set up data for each test method"""
        self.team = Team.objects.create(
            team_type=self.assembly_type,
            name="Alpha Assembly",
            description="Alpha Assembly Team"
        )

    def test_team_creation(self):
        """Test that a team can be created with valid data"""
        team = Team.objects.create(
            team_type=self.admin_type,
            name="Beta Admin",
            description="Beta Admin Team"
        )
        self.assertEqual(team.name, "Beta Admin")
        self.assertEqual(team.team_type, self.admin_type)

    def test_team_unique_name_per_type(self):
        """Test that team names must be unique"""
        with self.assertRaises(IntegrityError):
            Team.objects.create(
                team_type=self.assembly_type,
                name="Alpha Assembly"
            )

    def test_is_assembly_team(self):
        """Test assembly team type check"""
        self.assertTrue(self.team.can_create_aircraft())
        
        admin_team = Team.objects.create(
            team_type=self.admin_type,
            name="Admin Team"
        )
        self.assertFalse(admin_team.can_create_aircraft())

    def test_is_admin_team(self):
        """Test admin team type check"""
        admin_team = Team.objects.create(
            team_type=self.admin_type,
            name="Admin Team"
        )
        self.assertTrue(admin_team.is_admin_team())

    def test_get_name_display(self):
        """Test team name display formatting"""
        team = Team.objects.create(
            team_type=self.assembly_type,
            name="test team"
        )
        self.assertEqual(team.get_name_display(), "Test team")

class TeamMemberTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        cls.team_type = TeamType.objects.create(
            name=f"{TeamTypes.ASSEMBLY}_teammember_test"
        )
        cls.team = Team.objects.create(
            team_type=cls.team_type,
            name="Test Team"
        )
        cls.another_team = Team.objects.create(
            team_type=cls.team_type,
            name="Another Team"
        )

    def setUp(self):
        """Set up data for each test method"""
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            first_name="Test",
            last_name="User"
        )
        self.another_user = User.objects.create_user(
            username="another_user",
            password="testpass123"
        )

    def test_team_member_creation(self):
        """Test that a team member can be created with valid data"""
        team_member = TeamMember.objects.create(
            user=self.user,
            team=self.team
        )
        self.assertEqual(team_member.user, self.user)
        self.assertEqual(team_member.team, self.team)

    def test_one_user_one_team_constraint(self):
        """Test that a user can only be a member of one team"""
        TeamMember.objects.create(user=self.user, team=self.team)
        
        with self.assertRaises(IntegrityError):
            TeamMember.objects.create(user=self.user, team=self.another_team)

    def test_multiple_users_per_team(self):
        """Test that a team can have multiple members"""
        TeamMember.objects.create(user=self.user, team=self.team)
        TeamMember.objects.create(user=self.another_user, team=self.team)
        
        self.assertEqual(self.team.members.count(), 2)

    def test_team_member_str(self):
        """Test the string representation of a team member"""
        team_member = TeamMember.objects.create(
            user=self.user,
            team=self.team
        )
        expected = "Test User - Test Team"
        self.assertEqual(str(team_member), expected)
