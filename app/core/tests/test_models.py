"""
Test cases for models
"""
# Tool use for mock things => can replace
# some behavior for purpose
from unittest.mock import patch
# Import base class for tests
from django.test import TestCase

# Import helper function to get default user model
# Now can reference model directly define model
# Use get_user_model when change the model
# will be automatically updated everywhere in code
from django.contrib.auth import get_user_model

from core.models import Recipe, Tag, Ingredient, recipe_image_file_path
from decimal import Decimal


# Helper function return new user
def create_user():
    """Create and return a test user"""
    return get_user_model().objects.create_user(
        email='TestUser@example.com',
        password='Testpassword123'
    )


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
            user = get_user_model().objects.create_user(
                email=email,
                password='test',
            )
            self.assertEqual(user.email, expected_email)

    def test_create_new_user_without_email_must_raise_error(self):
        """Test create user without email must raises an Error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', password='test123')

    def test_create_superuser(self):
        """Test create superuser"""
        sample_test = get_user_model().objects.create_superuser(
            email='test@example.com',
            password='testpassword',
        )

        # Field is_superuser provided by
        # PermissionMixin
        self.assertTrue(sample_test.is_superuser)

        # Check if a staff
        self.assertTrue(sample_test.is_staff)

    def test_create_recipe(self):
        """Test create a recipe assign with user successful"""

        # Create user that recipe object assigned to
        sample_user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',
        )

        recipe = Recipe.objects.create(
            user=sample_user,  # User that recipe belonged to
            title="Sample recipe title",
            minute_to_make_recipe=5,
            price=Decimal('5.50'),
            description='Sample recipe description',
        )

        # Check the string representation of recipe
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test create a tag successfully"""
        user = create_user()
        tag = Tag.objects.create(user=user, name='tag1')

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test create ingredient"""
        user = create_user()
        ingredient = Ingredient.objects.create(
            user=user,
            name='Ingredient'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    # Test create a path to the file
    # in our system, uuid for unique name
    # Add decorate to patch uid function that
    # import into our model to replace behavor
    # of this uid, it will generate random string
    # everytime generate a unique identifier
    # dont need this (real time identifier) bc it
    # will quiet hard to determine what unique identifier
    # created in out test so
    # Using Mock behavior to define a constant uuid
    # just for testing (mock_uuid.return_value)
    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generate image path"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid

        # Function recipe_image_file_path to generate
        # the path to image being uploaded
        file_path = recipe_image_file_path(None, 'example.jpg')

        # Mean that we replace the name example to uuid to store
        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
