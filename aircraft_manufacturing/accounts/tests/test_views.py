from django.test import  TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import TeamType, Team, TeamMember
from accounts.constants import TeamTypes
from accounts.serializers import TeamSerializer, TeamMemberSerializer

class TeamViewSetTests(APITestCase, TransactionTestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        # Create team types
        cls.assembly_type = TeamType.objects.create(name=f"{TeamTypes.ASSEMBLY}_teamviewset")
        cls.admin_type = TeamType.objects.create(name=f"{TeamTypes.ADMIN}_teamviewset")

    def setUp(self):
        """Set up data for each test method"""
        # Create users with different roles
        self.admin_user = User.objects.create_superuser(
            username='test_admin',
            email='test_admin@example.com',
            password='admin123'
        )
        self.regular_user = User.objects.create_user(
            username='test_user',
            password='user123'
        )
        
        # Create a test team
        self.team = Team.objects.create(
            team_type=self.assembly_type,
            name="Test Assembly Team",
            description="Test Description"
        )

    def get_api_url(self, viewname, **kwargs):
        """Helper method to generate versioned API URLs"""
        version = 'v1'
        kwargs['version'] = version
        return reverse(viewname, kwargs=kwargs)

    def test_list_teams_authentication(self):
        """Test team listing with different authentication states"""
        url = self.get_api_url('accounts:teams-list')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Regular user should be able to list teams
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['recordsTotal'], 1)

    def test_create_team_permissions(self):
        """Test team creation with different user permissions"""
        url = self.get_api_url('accounts:teams-list')
        team_data = {
            'team_type': self.assembly_type.id,
            'name': 'New Team',
            'description': 'New Team Description'
        }

        # Regular user should not be able to create team
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(url, team_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Admin should be able to create team
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(url, team_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Team.objects.count(), 2)

    def test_team_detail_operations(self):
        """Test team detail view operations (retrieve, update, delete)"""
        url = self.get_api_url('accounts:teams-detail', pk=self.team.id)

        # Test retrieve
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.team.name)

        # Test update (should be admin only)
        update_data = {'name': 'Updated Team Name'}
        
        # Regular user cannot update
        response = self.client.patch(url, update_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Admin can update
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.team.refresh_from_db()
        self.assertEqual(self.team.name, 'Updated Team Name')

        # Test delete (should be admin only)
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Team.objects.count(), 0)

class TeamMemberViewSetTests(APITestCase, TransactionTestCase):
    # No need to test, it is not Public API
    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        cls.team_type = TeamType.objects.create(name=f"{TeamTypes.ASSEMBLY}_teammemberviewset")
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
        # Create users
        self.admin_user = User.objects.create_superuser(
            username='test_admin',
            email='test_admin@example.com',
            password='admin123'
        )
        self.team_member_user = User.objects.create_user(
            username='test_team_member',
            password='member123'
        )
        self.unassigned_user = User.objects.create_user(
            username='test_unassigned',
            password='user123'
        )

        # Create team membership
        self.team_member = TeamMember.objects.create(
            user=self.team_member_user,
            team=self.team
        )

    # def test_list_team_members(self):
    #     """Test listing team members with different permissions"""
    #     url = reverse('team-member-list')

    #     # Unauthenticated request should be denied
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    #     # Authenticated user can list team members
    #     self.client.force_authenticate(user=self.team_member_user)
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data['results']), 1)

    # def test_create_team_member(self):
    #     """Test team member creation with different scenarios"""
    #     url = reverse('team-member-list')
        
    #     member_data = {
    #         'user': self.unassigned_user.id,
    #         'team': self.team.id
    #     }

    #     # Regular user cannot create team member
    #     self.client.force_authenticate(user=self.unassigned_user)
    #     response = self.client.post(url, member_data)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    #     # Admin can create team member
    #     self.client.force_authenticate(user=self.admin_user)
    #     response = self.client.post(url, member_data)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #     # Cannot assign user to multiple teams
    #     member_data['team'] = self.another_team.id
    #     response = self.client.post(url, member_data)
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_team_member_detail_operations(self):
    #     """Test team member detail operations (retrieve, update, delete)"""
    #     url = reverse('team-member-detail', args=[self.team_member.id])

    #     # Test retrieve
    #     self.client.force_authenticate(user=self.team_member_user)
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['user'], self.team_member_user.id)

    #     # Test update (admin only)
    #     update_data = {'team': self.another_team.id}
        
    #     # Regular user cannot update
    #     response = self.client.patch(url, update_data)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    #     # Admin can update
    #     self.client.force_authenticate(user=self.admin_user)
    #     response = self.client.patch(url, update_data)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.team_member.refresh_from_db()
    #     self.assertEqual(self.team_member.team, self.another_team)

    #     # Test delete
    #     response = self.client.delete(url)
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #     self.assertEqual(TeamMember.objects.count(), 0)
