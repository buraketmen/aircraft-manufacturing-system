from django.test import TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import TeamType, Team, TeamMember
from accounts.constants import TeamTypes
from assembly.models import Aircraft, AircraftType
from inventory.models import Part, PartType

class AircraftTypeViewSetTests(APITestCase, TransactionTestCase):
    # No need to test, as this is not public API
    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        cls.assembly_type = TeamType.objects.create(name=TeamTypes.ASSEMBLY)
        cls.assembly_team = Team.objects.create(
            team_type=cls.assembly_type,
            name="Test Assembly Team"
        )
        cls.regular_user = User.objects.create_user(username="test_user", password="password")
        cls.assembly_member = TeamMember.objects.create(
            team=cls.assembly_team,
            user=cls.regular_user
        )
    
    def get_api_url(self, viewname, **kwargs):
        """Helper method to generate versioned API URLs"""
        version = 'v1'
        kwargs['version'] = version
        return reverse(viewname, kwargs=kwargs)
        
    

class AircraftViewSetTests(APITestCase, TransactionTestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        cls.assembly_type = TeamType.objects.create(name=TeamTypes.ASSEMBLY)
        cls.assembly_team = Team.objects.create(
            team_type=cls.assembly_type,
            name="Test Assembly Team"
        )
        cls.regular_user = User.objects.create_user(username="test_user", password="password")
        cls.assembly_member = TeamMember.objects.create(
            team=cls.assembly_team,
            user=cls.regular_user
        )
        cls.aircraft_type = AircraftType.objects.create(name="Test Aircraft Type")
        cls.part_type = PartType.objects.create(name="Test Part Type")
        cls.part = Part.objects.create(part_type=cls.part_type, aircraft_type=cls.aircraft_type)
        cls.aircraft = Aircraft.objects.create(
            aircraft_type=cls.aircraft_type,
            serial_number="12345",
            owner=cls.assembly_member
        )
        cls.aircraft.parts.set([cls.part,])
    
    def get_api_url(self, viewname, **kwargs):
        """Helper method to generate versioned API URLs"""
        version = 'v1'
        kwargs['version'] = version
        return reverse(viewname, kwargs=kwargs)
    
    def test_list_aircraft_authentication(self):
        """Test aircraft listing with different authentication states"""
        url = self.get_api_url('assembly:aircraft-list')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['recordsTotal'], 1)
    
    def test_create_aircraft_permissions(self):
        """Test aircraft creation with different user permissions"""
        url = self.get_api_url('assembly:aircraft-list')
        aircraft_data = {
            'aircraft_type': self.aircraft_type.id,
            'serial_number': '54321',
            'part': self.part.id
        }
        
        response = self.client.post(url, aircraft_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(url, aircraft_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_aircraft_permissions(self):
        """Test aircraft update with different user permissions"""
        url = self.get_api_url('assembly:aircraft-detail', pk=self.aircraft.id)
        aircraft_data = {
            'serial_number': '54321'
        }
        
        response = self.client.put(url, aircraft_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.put(url, aircraft_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_aircraft_permissions(self):
        """Test aircraft deletion with different user permissions"""
        url = self.get_api_url('assembly:aircraft-detail', pk=self.aircraft.id)
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Aircraft.objects.count(), 0)

    def test_requirements_aircraft(self):
        """Test that aircraft creation requires a part"""
        url = self.get_api_url('assembly:aircraft-requirements')
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)