"""
Tests Tag API
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag
from recipe.serializers import TagSerializer


URL_TAGS = reverse('recipe:tag-list')


def create_user():
    """Create and return a default user"""
    return get_user_model().objects.create_user(
        email="Test@example.com",
        password="Testpassword123",
    )


def detail_url(tag_id):
    """Create a tag detail url"""
    return reverse('recipe:tag-detail', args=[tag_id])


class PublicAPITagTest(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_authenticate_is_required(self):
        """Test authentication is required for retriving tags"""
        res = self.client.get(URL_TAGS)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAPITagTest(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retriev tag list"""
        Tag.objects.create(user=self.user, name="ABC")
        Tag.objects.create(user=self.user, name="XYZ")

        res = self.client.get(URL_TAGS)

        # Get tag from db
        tags = Tag.objects.all().order_by('name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tag_limited_to_user(self):
        """Test list tag is limited to authentitcated user"""
        user_unauthen = get_user_model().objects.create_user(
            email="Unauthen@example.com",
            password="Unauthenpassword123",
        )
        Tag.objects.create(user=user_unauthen, name='ABC')
        tag = Tag.objects.create(user=self.user, name='XYZ')

        res = self.client.get(URL_TAGS)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_tag_update(self):
        """Test update a tag"""
        tag = Tag.objects.create(user=self.user, name='ABC')

        sample_update = {'name': 'XYZ'}
        url = detail_url(tag_id=tag.id)

        res = self.client.patch(url, sample_update)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, sample_update['name'])

    def test_tag_delete(self):
        """Test delete a tag"""
        tag = Tag.objects.create(user=self.user, name='ABC')

        url = detail_url(tag_id=tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
