from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsSuperUserOrReadOnly
from accounts.models import TeamType

class MockViewSet(ModelViewSet):
    """Mock viewset for testing permissions"""
    permission_classes = [IsAuthenticated, IsSuperUserOrReadOnly]
    queryset = TeamType.objects.all()

class IsSuperUserOrReadOnlyTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = MockViewSet()
        self.permission = IsSuperUserOrReadOnly()
        
        # Create users
        self.superuser = User.objects.create_superuser(
            username='admin_permission_test',
            email='admin_permission@example.com',
            password='admin123'
        )
        self.regular_user = User.objects.create_user(
            username='user_permission_test',
            password='user123'
        )

    def test_safe_methods_allowed_for_authenticated_users(self):
        """Test that any authenticated user can perform safe methods (GET, HEAD, OPTIONS)"""
        safe_methods = ['get', 'head', 'options']
        
        for method in safe_methods:
            with self.subTest(f"Testing {method} method"):
                request = getattr(self.factory, method)('/')
                request.user = self.regular_user
                
                self.assertTrue(
                    self.permission.has_permission(request, self.view),
                    f"{method.upper()} should be allowed for regular users"
                )

    def test_unsafe_methods_superuser_only(self):
        """Test that only superusers can perform unsafe methods (POST, PUT, PATCH, DELETE)"""
        unsafe_methods = ['post', 'put', 'patch', 'delete']
        
        # Test with regular user
        for method in unsafe_methods:
            with self.subTest(f"Testing {method} method with regular user"):
                request = getattr(self.factory, method)('/')
                request.user = self.regular_user
                
                self.assertFalse(
                    self.permission.has_permission(request, self.view),
                    f"{method.upper()} should not be allowed for regular users"
                )

        # Test with superuser
        for method in unsafe_methods:
            with self.subTest(f"Testing {method} method with superuser"):
                request = getattr(self.factory, method)('/')
                request.user = self.superuser
                
                self.assertTrue(
                    self.permission.has_permission(request, self.view),
                    f"{method.upper()} should be allowed for superusers"
                )

    def test_unauthenticated_user(self):
        """Test that unauthenticated users have no permissions"""
        methods = ['get', 'post', 'put', 'patch', 'delete']
        
        for method in methods:
            with self.subTest(f"Testing {method} method with unauthenticated user"):
                request = getattr(self.factory, method)('/')
                request.user = None
                
                self.assertFalse(
                    self.permission.has_permission(request, self.view),
                    f"{method.upper()} should not be allowed for unauthenticated users"
                )
