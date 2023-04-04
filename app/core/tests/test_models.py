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

    def test_create_user_with_email_successful(self):
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
