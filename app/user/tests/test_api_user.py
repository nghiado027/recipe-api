"""
Tests API user
"""

from django.test import TestCase
from django.contrib.auth import get_user_model  # noqa
from django.urls import reverse

# Import api client test
from rest_framework.test import APIClient
from rest_framework import status

from core.models import User

# URL endpoint create user
URL_CREATE_USER = reverse('user:create')

# URL endpoint to create
# token in API
URL_TOKEN = reverse('user:token')

# URL endpoint manage user (like my profile page)
ME_URL = reverse('user:me')


# Helper function to create user for testing
def create_user(**params):
    """Create a new user"""
    return User.objects.create_user(**params)


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
        # create user (creadential)
        sample_test = {
            'email': 'test@example.com',
            'password': 'test123456',
            'name': 'User test',
        }

        # Using post method to create user
        res = self.client.post(URL_CREATE_USER, sample_test)

        # Check if status code of
        # response (of post method)
        # is successs (http 201 created)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Get user by email
        # If user created success it
        # should return a user
        user = User.objects.get(email=sample_test['email'])

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
            'email': 'test@example.com',
            'password': 'test123456',
            'name': 'User test',
        }

        # This edge case is user created first
        # in db with email and then use post to
        # create that user, Must return the error
        create_user(**sample_test)
        res = self.client.post(URL_CREATE_USER, sample_test)

        # Check status of response
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Test password strength
    def test_password_strength(self):
        """Test an error returned if password less than 8 characters"""
        sample_test = {
            'email': 'test@example.com',
            'password': 'test',
            'name': 'User test',
        }

        res = self.client.post(URL_CREATE_USER, sample_test)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Expect user wont exist
        # Use .get() for return single object
        # and raise DoesNotExist
        # User .filter() for return multiple
        # objects (queryset ?)
        user_queryset = User.objects.filter(email=sample_test['email'])

        # Confirm that user doesnt exist
        # in database
        self.assertFalse(user_queryset)

    # Test create token, test the successful
    # case when log in or use token API to
    # create new token
    def test_create_token_of_user(self):
        """Test generates token for valid credentials"""
        sample_test = {
            'email': 'test@example.com',
            'password': 'test123456',
            'name': 'User test',
        }

        # Create user first and then create
        # token for user
        create_user(**sample_test)
        res = self.client.post(URL_TOKEN, sample_test)

        # Check 'token' field in post response
        # and status code of post
        self.assertIn('token', res.data)
        self.assertEqual(status.HTTP_200_OK, res.status_code)

    # Test must return error when create token
    # with bad credentials
    def test_create_token_with_bad_credentials(self):
        """Test return error with invalids credentials"""
        sample_test = {
            'email': 'test@example.com',
            'password': 'test123456',
        }

        # Create a token with invalid creadentials
        # in this case is different password with
        # exsisted user
        create_user(**sample_test)
        res = self.client.post(URL_TOKEN, email=sample_test['email'],
                               password='diffpassword')

        # Check token not in post response
        # and status code
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Test must return error when create token
    # with bad credentials
    def test_create_token_with_blank_password(self):
        """Test blank password returns error"""

        # This case is create user with blank
        # password
        res = self.client.post(URL_TOKEN,
                               email='test@example.com',
                               password='')

        # Check token not in post response
        # and status code
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Test authenticaation is required and enforced
    # for any endpoint
    def test_required_authorized(self):
        """Test authentication is required for users"""

        # Make an unauthenticated request
        # and check unauthorized
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# Private: authenticated test to endpoint
# Seperate two class because setup is differente
# between authen and unauthen
class PrivateAPIUserTest(TestCase):
    """Test API request require authentication"""

    def setUp(self):
        # Create test user
        self.user = create_user(
            email='test@example.com',
            password='test123456',
            name='User test',
        )

        # Create client
        self.client = APIClient()

        # Force authenticate this user, assume that
        # test user is authenticated
        self.client.force_authenticate(user=self.user)

    # Test retriving profile of authenticated user
    def test_retrieve_profile_user_success(self):
        """Test retriving user's profile for logged in user"""
        res = self.client.get(ME_URL)

        # Check response must be OK
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Data retriving must be the same (of user test)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name
        })

    def text_post_method_with_no_endpoint_not_allowed(self):
        """Test POST is not allowed for the no endpoint"""

        # Post with nothing
        res = self.client.post(ME_URL, {})

        # Must be 404
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user(self):
        """Test updating user of this authenticated user"""

        sample_test = {'password': 'Updatepassword', 'name': 'Updated user'}

        # Use patch to update partially user
        res = self.client.patch(ME_URL, sample_test)

        # Refresh to get updated database
        self.user.refresh_from_db()

        # Check status OK
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Check name and password (check_password) must be
        # the same updated in4
        self.assertEqual(self.user.name, sample_test['name'])
        self.assertTrue(self.user.check_password(sample_test['password']))
