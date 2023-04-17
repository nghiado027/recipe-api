"""
Tests recipe APIs
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

# List of recipe a
URL_RECIPE = reverse('recipe:recipe-list')


# Helper function to create recipe for testing
def create_recipe(user, **params):
    """Create a recipe"""
    default_recipe = {
        'title': 'Default recipe title',
        'minute_to_make_recipe': 1,
        'price': Decimal('1.0'),
        'description': 'Default recipe description',
        'link': 'https://example.com/recipe.pdf'
    }

    # For allow changing some default value
    # and add new value
    default_recipe.update(params)

    recipe = Recipe.objects.create(user=user, **default_recipe)
    return recipe


# For passing recipe ID to URL instead of
# harcode like 'URL_RECIPE' constant
def detail_url(recipe_id):
    """Create recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


# Test unauthenticate request (same as user api)
class PublicAPIRecipeTest(TestCase):
    """Test API recipe for public features"""

    def setUp(self):
        self.client = APIClient()

    # Recipe only retrived by anthenticated user
    # recipe not pulic
    def test_authentication_required(self):
        """Test authentication is required to call API"""
        res = self.client.get(URL_RECIPE)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAPIRecipeTest(TestCase):
    """Test API recipe authenticated"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='Test@example.com',
            password='testpassword123',
        )

        # Authenticate user
        self.client.force_authenticate(self.user)

    def test_retrive_recipes_from_user(self):
        """Test retriving list recipe of user"""

        # Create recipe by default
        create_recipe(user=self.user)
        create_recipe(user=self.user, **{'title': 'Default recipe title 2'})

        # Expect that returns recipes of
        # user
        res = self.client.get(URL_RECIPE)

        # Expect all recipe of user returned in order by id
        recipes = Recipe.objects.all().order_by('id')

        # Expect the result are serialized, many=True
        # to pass list of items
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Expect data dictionary of the objects passed through the serializer
        self.assertEqual(res.data, serializer.data)

    # Test return recipes for authenticated user that currently looged in
    # This case will add some recipe for another user and check that they
    # dont exist in the response
    def test_recipe_limited_to_user(self):
        """Test list of recipes is limited to authenticated user"""

        # Create other user (different from default setup)
        other_user = get_user_model().objects.create_user(
            email='otheruser@example.com',
            password='otherpassword123'
        )

        # Assign recipe of one for default (authenticated) and other user
        create_recipe(user=other_user)
        create_recipe(user=self.user, **{'title': 'Default recipe title 2'})

        # Expect only recipe of authenticated user (default)
        res = self.client.get(URL_RECIPE)

        # Filter recipes from authenticated user
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail"""

        # Create sample recipe and assign to user
        recipe = create_recipe(user=self.user)

        # Create a detail url (with id) then
        # send get method to call
        url = detail_url(recipe.id)
        res = self.client.get(url)

        # Just one recipe so dont need 'many=true'
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test create a recipe"""
        sample_test = {
            'title': 'Sample recipe title',
            'minute_to_make_recipe': 10,
            'price': Decimal('4.22'),
            'description': 'sample recipe description',
            'link': 'https://example.com/recipe.pdf'
        }

        # Using post method to create
        # ../api/recipes/recipe this is endpoint
        res = self.client.post(URL_RECIPE, sample_test)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Get recipe by id
        recipe = Recipe.objects.get(id=res.data['id'])

        # Check each fields of recipe in database
        # and the sample must the same
        for key, value in sample_test.items():
            # getattr to get atribute of recipe object
            # and check each value must be the same
            self.assertEqual(getattr(recipe, key), value)

        # User assigned to create recipe API must
        # matched the user we authenticated (in setUp)
        self.assertEqual(recipe.user, self.user)
