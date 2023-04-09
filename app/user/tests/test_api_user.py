"""
Tests API user
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# Import api client test
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_PATH = reverse('user:create')

def create_user(**params):
    """Create a new user"""
    return get_user_model().objects.create_user(**params)


# Public: unauthen requests, request
# dont require for authen sucha as: register
# new user (becau new user not registered)
class PublicAPIUserTest(TestCase):
    """Test API user for public features"""

    # Create client for testing
    def setUp(self):
        self.client = APIClient()

    def test_create_user(self):
        """Test create user"""

        # Content for post method to
        # create user
        sample_test = {
            'name': 'User test',
            'email': 'test@example.com',
            'password': 'test123456',
        }

        # Using post method to create user
        res = self.client.post(CREATE_USER_PATH, sample_test)

        # Check if status code of
        # response (of post method)
        # is successs (http 201 created)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Get user by email
        # If user created success it
        # should return a user
        user = get_user_model().objects.get(email=sample_test['email'])

        # Check corect user password
        # created
        self.assertTrue(user.check_password(sample_test['password']))

        # In case that password not in
        # response
        self.assertNotIn('password', res.data)


    # Check if try to create user with email
    # address already doesnt work
    # This is an edge case that user not be generated
    # or not added
    def test_user_error_email(self):
        """Test error returned if user with email exist"""
        sample_test = {
            'name': 'User test',
            'email': 'test@example.com',
            'password': 'test123456',
        }
        create_user(**sample_test)
        res = self.client.post(CREATE_USER_PATH, sample_test)

        # Check status of response
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    # Test password strength
    def test_password_strength(self):
        """Test an error returned if password less than 8 characters"""
        sample_test = {
            'name': 'User test',
            'email': 'test@example.com',
            'password': 'test',
        }

        res = self.client.post(CREATE_USER_PATH, sample_test)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Expect user wont exist
        # Use .get() for return single object
        # and raise DoesNotExist
        # User .filter() for return multiple
        # objects (queryset ?)
        user = get_user_model().objects.filter(email=sample_test['email'])

        # Confirm that user doesnt exist
        # in database
        self.assertFalse(user)
