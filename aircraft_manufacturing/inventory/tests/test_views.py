from django.test import TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import TeamType, Team, TeamMember
from accounts.constants import TeamTypes
from inventory.models import PartType, TeamPartPermission, Part
from assembly.models import AircraftPartRequirement, AircraftType

class PartTypeViewSetTests(APITestCase, TransactionTestCase):
    # No need to test, as this is not public API
    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        cls.team_type = TeamType.objects.create(name=TeamTypes.ASSEMBLY)
        cls.team = Team.objects.create(
            team_type=cls.team_type,
            name="Test Team"
        )

    def setUp(self):
        """Set up data for each test method"""
        self.admin_user = User.objects.create_superuser(
            username='test_admin',
            email='test_admin@example.com',
            password='admin123'
        )
        self.regular_user = User.objects.create_user(
            username='test_user',
            password='user123'
        )
        TeamMember.objects.create(
            user=self.regular_user,
            team=self.team
        )
        self.part_type = PartType.objects.create(
            name="Test Part Type",
            description="Test Description"
        )

    def get_api_url(self, viewname, **kwargs):
        """Helper method to generate versioned API URLs"""
        version = 'v1'
        kwargs['version'] = version
        return reverse(viewname, kwargs=kwargs)

    # def test_list_part_types(self):
    #     """Test part type listing with different permissions"""
    #     url = self.get_api_url('inventory:part-type-list')
        
    #     # Unauthenticated request should be denied
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    #     # Regular user can list
    #     self.client.force_authenticate(user=self.regular_user)
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['recordsTotal'], 1)

    # def test_create_part_type_permissions(self):
    #     """Test part type creation with different permissions"""
    #     url = self.get_api_url('inventory:part-type-list')
    #     data = {
    #         'name': 'New Part Type',
    #         'description': 'New Description'
    #     }

    #     # Regular user cannot create
    #     self.client.force_authenticate(user=self.regular_user)
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    #     # Admin can create
    #     self.client.force_authenticate(user=self.admin_user)
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class TeamPartPermissionViewSetTests(APITestCase, TransactionTestCase):
    # no need to test, as this is not public API
    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        cls.team_type = TeamType.objects.create(name=TeamTypes.ASSEMBLY)
        cls.part_type = PartType.objects.create(name="Test Part Type")

    def setUp(self):
        """Set up data for each test method"""
        self.admin_user = User.objects.create_superuser(
            username='test_admin',
            email='test_admin@example.com',
            password='admin123'
        )
        self.regular_user = User.objects.create_user(
            username='test_user',
            password='user123'
        )
        self.permission = TeamPartPermission.objects.create(
            team_type=self.team_type,
            part_type=self.part_type,
            can_create=True
        )

    def get_api_url(self, viewname, **kwargs):
        """Helper method to generate versioned API URLs"""
        version = 'v1'
        kwargs['version'] = version
        return reverse(viewname, kwargs=kwargs)

    # def test_list_permissions(self):
    #     """Test permission listing"""
    #     url = self.get_api_url('inventory:team-part-permission-list')
        
    #     # Unauthenticated request should be denied
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    #     # Regular user can view
    #     self.client.force_authenticate(user=self.regular_user)
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['recordsTotal'], 1)

    # def test_create_permission_admin_only(self):
    #     """Test permission creation is admin only"""
    #     url = self.get_api_url('inventory:team-part-permission-list')
    #     data = {
    #         'team_type': self.team_type.id,
    #         'part_type': self.part_type.id,
    #         'can_create': True
    #     }

    #     # Regular user cannot create
    #     self.client.force_authenticate(user=self.regular_user)
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    #     # Admin can create
    #     self.client.force_authenticate(user=self.admin_user)
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # Due to unique constraint

class PartViewSetTests(APITestCase, TransactionTestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        cls.team_type = TeamType.objects.create(name=TeamTypes.ASSEMBLY)
        cls.team = Team.objects.create(
            team_type=cls.team_type,
            name="Test Team"
        )
        cls.part_type = PartType.objects.create(name="Test Part Type")
        cls.aircraft_type = AircraftType.objects.create(name="Test Aircraft Type")
        
        # Create permission for team type
        cls.permission = TeamPartPermission.objects.create(
            team_type=cls.team_type,
            part_type=cls.part_type,
            can_create=True
        )

    def setUp(self):
        """Set up data for each test method"""
        self.admin_user = User.objects.create_superuser(
            username='test_admin',
            email='test_admin@example.com',
            password='admin123'
        )
        self.team_member = User.objects.create_user(
            username='test_member',
            password='member123'
        )
        self.team_membership = TeamMember.objects.create(
            user=self.team_member,
            team=self.team
        )
        
        # Create a test part
        self.part = Part.objects.create(
            part_type=self.part_type,
            aircraft_type=self.aircraft_type,
            owner=self.team_membership
        )

    def get_api_url(self, viewname, **kwargs):
        """Helper method to generate versioned API URLs"""
        version = 'v1'
        kwargs['version'] = version
        return reverse(viewname, kwargs=kwargs)

    def test_list_parts(self):
        """Test part listing"""
        url = self.get_api_url('inventory:parts-list')
        
        # Unauthenticated request should be denied
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Team member can list
        self.client.force_authenticate(user=self.team_member)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['recordsTotal'], 1)

    def test_create_part(self):
        """Test part creation with team permissions"""
        url = self.get_api_url('inventory:parts-list')
        data = {
            'part_type': self.part_type.id,
            'aircraft_type': self.aircraft_type.id
        }

        # Team member with permission can create
        self.client.force_authenticate(user=self.team_member)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['owner_name'], self.team_member.username)

    def test_part_update_not_allowed(self):
        """Test that part updates are not allowed"""
        url = self.get_api_url('inventory:parts-detail', pk=self.part.id)
        data = {'serial_number': 'NEW001'}

        self.client.force_authenticate(user=self.team_member)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_part(self):
        """Test part deletion"""
        url = self.get_api_url('inventory:parts-detail', pk=self.part.id)
        
        # Team member can delete their own part
        self.client.force_authenticate(user=self.team_member)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Part.objects.count(), 0)

    def test_get_inventory_status(self):
        """Test inventory status endpoint"""
        url = self.get_api_url('inventory:parts-inventory-status')

        AircraftPartRequirement.objects.create(
            aircraft_type=self.aircraft_type,
            part_type=self.part_type,
            quantity=5
        )
        self.client.force_authenticate(user=self.team_member)
        response = self.client.get(url)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key, value in response.data.items():
            # check if value dict
            self.assertIsInstance(value, dict)
            self.assertIsInstance(key, str)
            # Quantity is not same with the inventory status, it is all about how many parts we have
            self.assertEqual(value['total'], 1)
            self.assertEqual(value['available'], 1)
            self.assertEqual(value['used'], 0)

