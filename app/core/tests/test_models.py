"""
Test cases for models
"""

# Import base class for tests
from django.test import TestCase

# Import helper function to get default user model
# Now can reference model directly define model
# Use get_user_model when change the model
# will be automatically updated everywhere in code
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_success(self):
        """Test create user by email success"""
        email = 'test@example.com'
        password = 'testpassword'

        # Create a user with email
        # and password of user
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        # Check
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_with_email_normalized(self):
        """Test user email normalized"""

        # Domain must be lowercase
        sample_emails = [
            ['Test0@Example.com', 'Test0@example.com'],
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['test2@EXAMPLE.COM', 'test2@example.com'],
            ['test3@example.COM', 'test3@example.com'],
        ]

        for email, expected_email in sample_emails:
            user = get_user_model().objects.create_user(email=email,
                                                        password='test')
            self.assertEqual(user.email, expected_email)

    def test_create_new_user_without_email_must_raise_error(self):
        """Test create user without email must raises an Error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', password='test123')

    def test_create_superuser(self):
        """Test create superuser"""
        user = get_user_model().objects.create_superuser(
            email='test@example.com',
            password='testpassword',
        )

        # Field is_superuser provided by
        # PermissionMixin
        self.assertTrue(user.is_superuser)

        # Check if a staff
        self.assertTrue(user.is_staff)
