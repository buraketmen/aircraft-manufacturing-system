from django.test import TestCase
from django.contrib.auth.models import User
from accounts.utils import get_user_display_name

class UserDisplayNameTests(TestCase):
    def test_display_name_priority(self):
        """Test that display name follows the correct priority order:
        1. Full name (first_name + last_name)
        2. First name only
        3. Last name only
        4. Email username
        5. Username
        """
        test_cases = [
            {
                'create_data': {
                    'username': 'user1',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': 'john@example.com'
                },
                'expected': 'John Doe',
                'description': 'Should use full name when available'
            },
            {
                'create_data': {
                    'username': 'user2',
                    'first_name': 'Jane',
                    'email': 'jane@example.com'
                },
                'expected': 'Jane',
                'description': 'Should use first name when last name is not available'
            },
            {
                'create_data': {
                    'username': 'user3',
                    'last_name': 'Smith',
                    'email': 'smith@example.com'
                },
                'expected': 'Smith',
                'description': 'Should use last name when first name is not available'
            },
            {
                'create_data': {
                    'username': 'user4',
                    'email': 'robert@example.com'
                },
                'expected': 'robert',
                'description': 'Should use email username when no names are available'
            },
            {
                'create_data': {
                    'username': 'user5'
                },
                'expected': 'user5',
                'description': 'Should fallback to username when no other options are available'
            }
        ]

        for case in test_cases:
            with self.subTest(case['description']):
                user = User.objects.create_user(**case['create_data'])
                self.assertEqual(get_user_display_name(user), case['expected'])

    def test_empty_values_handling(self):
        """Test that the function handles empty or whitespace values correctly"""
        test_cases = [
            {
                'create_data': {
                    'username': 'user6',
                    'first_name': '',
                    'last_name': '',
                    'email': 'test@example.com'
                },
                'expected': 'test',
                'description': 'Should handle empty strings in names'
            },
            {
                'create_data': {
                    'username': 'user7',
                    'first_name': '   ',
                    'last_name': '   ',
                    'email': ''
                },
                'expected': 'user7',
                'description': 'Should handle whitespace-only strings'
            }
        ]

        for case in test_cases:
            with self.subTest(case['description']):
                user = User.objects.create_user(**case['create_data'])
                display_name = get_user_display_name(user)
                self.assertEqual(display_name.strip(), case['expected'])
