"""
Tests for ingredient API
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer


# Base on DefaultRouter() generate url ?
URL_INGREDIENT = reverse('recipe:ingredient-list')


def create_user(email='test@example.com', password='testpassword123'):
    """Create a user"""
    return get_user_model().objects.create_user(email=email, password=password)


def detail_url(ingredient_id):
    """Return URL of detail ingredient base on id"""
    # Base on DefaultRouter() generate url
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


class PublicAPIIngredientTest(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_authen_is_required(self):
        """Test authen is required for retrieving ingredients"""
        res = self.client.get(URL_INGREDIENT)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAPIIngredientTest(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredients(self):
        """Test retrieve ingredients"""
        Ingredient.objects.create(user=self.user, name='Bean')
        Ingredient.objects.create(user=self.user, name='Salt')

        # Every single test run, the database entirely
        # refresh ?
        res = self.client.get(URL_INGREDIENT)

        ingredients = Ingredient.objects.all().order_by('name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test ingredients is limited to authenticated user"""
        user_unauthen = create_user(
            email='unauthen@example.com',
            password='testpass123'
        )

        Ingredient.objects.create(user=user_unauthen, name='ABC')
        authen_ingredient = Ingredient.objects.create(
            user=self.user,
            name='XYZ',
        )

        res = self.client.get(URL_INGREDIENT)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], authen_ingredient.id)
        self.assertEqual(res.data[0]['name'], authen_ingredient.name)

    def test_update_ingredient(self):
        """Test update ingredient"""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Test ingredient'
        )

        url = detail_url(ingredient.id)
        update_name = {'name': 'Update ingredient'}

        res = self.client.patch(url, update_name)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingredient.refresh_from_db()

        self.assertEqual(ingredient.name, update_name['name'])

    def test_delete_ingredient(self):
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Delete ingredient'
        )
        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        ingredients = Ingredient.objects.filter(user=self.user)

        self.assertEqual(len(ingredients), 0)

    def test_filter_ingredients_associated_with_recipes(self):
        """Test list ingredients that associate with recipes"""
        ingredient1 = Ingredient.objects.create(user=self.user, name='I1')
        ingredient2 = Ingredient.objects.create(user=self.user, name='I2')

        recipe = Recipe.objects.create(
            user=self.user,
            title='Default recipe title',
            minute_to_make_recipe=1,
            price=Decimal('1.0'),
            description='Default recipe description',
            link='https://example.com/recipe.pdf'
        )

        recipe.ingredients.add(ingredient1)

        s1 = IngredientSerializer(ingredient1)
        s2 = IngredientSerializer(ingredient2)

        # Pass param 'assigned_only'
        res = self.client.get(URL_INGREDIENT, {'ids_assigned': s1.data['id']})

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filter_ingredients_distinct(self):
        """Test filterd ingredients must (get) uniquely"""
        ingredient = Ingredient.objects.create(user=self.user, name="I3")
        Ingredient.objects.create(user=self.user, name="I4")

        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Title 12',
            minute_to_make_recipe=1,
            price=Decimal('1.0'),
            description='Default recipe 12 description',
            link='https://example.com/recipe.pdf'
        )

        recipe2 = Recipe.objects.create(
            user=self.user,
            title='Title 22',
            minute_to_make_recipe=1,
            price=Decimal('1.0'),
            description='Default recipe 22 description',
            link='https://example.com/recipe.pdf'
        )

        recipe1.ingredients.add(ingredient)
        recipe2.ingredients.add(ingredient)

        res = self.client.get(URL_INGREDIENT, {'ids_assigned': recipe1.id})

        self.assertEqual(len(res.data), 1)
