"""
Test for Django admin
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

# Use reversed to access the views
# that provided by a site
from django.urls import reverse

# Client act as client for testing
from django.test import Client


class AdminPageTests(TestCase):
    """Tests for Django admin page"""

    # Set up before every test
    # Must be "setUp", otherwise
    # it wont work
    def setUp(self):
        """Create client, admin and normal user for testing."""

        # Create client
        self.client = Client()

        # Create admin
        self.admin = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='iloveyou<3admin',
        )

        # Login using admin account created above
        self.client.force_login(self.admin)

        # Create normal user
        self.user = get_user_model().objects.create_user(
            email='someone@example.com',
            password='testpassword',
            name='Normal User',
        )

    def test_users(self):
        """Test that users exsisted"""

        # reverse this case is admin page
        # 'admin:core_user_changelist' url generate
        # by admin, determine what url have to pull
        url = reverse('admin:core_user_changelist')

        # Make a request to url and get respone
        res = self.client.get(url)

        # Check page if it contain user and
        # email ofr normal user created above
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_page_edit(self):
        """Test editing user page work"""

        # Pull the user change url
        # with user id (full url:
        # http://127.0.0.1:8000/admin/core/user/1/change/)
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        # Check if sucess =
        # http response 200
        self.assertEqual(res.status_code, 200)
