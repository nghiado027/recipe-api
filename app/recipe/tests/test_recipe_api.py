"""
Tests recipe APIs
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

# For image test
import tempfile
import os

from PIL import Image

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


# Helper function to generate upload image endpoint
def image_upload_url(recipe_id):
    """Create image upload URL"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


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

    def test_create_recipe_with_new_tag(self):
        """Test create a recipe with new tag"""
        sample_test = {
            'title': 'Sample recipe title',
            'minute_to_make_recipe': 10,
            'price': Decimal('4.22'),
            'description': 'sample recipe description',
            'link': 'https://example.com/recipe.pdf',
            'tags': [{'name': 'Viet Nam'}, {'name': 'Breakfast'}],
        }
        res = self.client.post(URL_RECIPE, sample_test, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)  # because create 1 recipe

        # Test 2 tags must exists
        self.assertEqual(recipes[0].tags.count(), 2)  # we assigned 2 tags
        for tag in sample_test['tags']:
            exists_tag = recipes[0].tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists_tag)

    def test_create_recipe_with_existing_tag(self):
        """Test create a recipe with existing tag"""
        tag_example = Tag.objects.create(user=self.user, name='Viet Nam')
        sample_test = {
            'title': 'Sample recipe title VN',
            'minute_to_make_recipe': 75,
            'price': Decimal('4.22'),
            'description': 'sample recipe description',
            'link': 'https://example.com/recipe.pdf',
            'tags': [{'name': 'Viet Nam'}, {'name': 'Breakfast'}],
        }
        res = self.client.post(URL_RECIPE, sample_test, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        # Test 2 tags must exists
        self.assertEqual(recipes[0].tags.count(), 2)

        self.assertIn(tag_example, recipes[0].tags.all())

        for tag in sample_test['tags']:
            exists_tag = recipes[0].tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists_tag)

    def test_create_tag_when_update(self):
        """Test create a tag when update a recipe"""
        recipe = create_recipe(user=self.user)

        sample_tag = {'tags': [{'name': 'dinner'}]}
        url = detail_url(recipe.id)

        # Using patch to update tags from recipe id
        # should not refresh DB when using ManyToManyField ?
        # (bc essentially its create new query under the hood)
        # When Calling recipe.tag.all, its going to do a seperate
        # query and it's going to retrieve all the fresher objects
        # for particular recipe. Its arent cached when first create
        # the recipes so there's no need to refresh update on recipe
        # instance
        res = self.client.patch(url, sample_tag, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        new_tag = Tag.objects.get(user=self.user, name='dinner')
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test assign an existing tag when update a recipe"""
        tag_default = Tag.objects.create(user=self.user, name='Dinner')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_default)

        tag_update = Tag.objects.create(user=self.user, name='abc')
        sample = {'tags': [{'name': 'abc'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, sample, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_update, recipe.tags.all())
        self.assertNotIn(tag_default, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clear recipes tags"""
        tag = Tag.objects.create(user=self.user, name='tag1')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        sample = {'tags': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, sample, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_with_new_ingredient(self):
        """Test create a recipe with new ingredients"""

        sample_test = {
            'title': 'Sample recipe title VN',
            'minute_to_make_recipe': 75,
            'price': Decimal('4.22'),
            'description': 'sample recipe description',
            'link': 'https://example.com/recipe.pdf',
            'tags': [{'name': 'Viet Nam'}, {'name': 'Breakfast'}],
            'ingredients': [{'name': 'Tomatoes'}, {'name': 'Meat'}]
        }
        res = self.client.post(
            path=URL_RECIPE,
            data=sample_test,
            format='json'
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(len(recipes), 1)

        self.assertEqual(recipes[0].ingredients.count(), 2)

        for ingredient in sample_test['ingredients']:
            exists = recipes[0].ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredient(self):
        """"Test create recipe with existing ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name='Rice')

        sample_test = {
            'title': 'Com tam',
            'minute_to_make_recipe': 75,
            'price': Decimal('4.22'),
            'description': 'sample recipe description',
            'link': 'https://example.com/recipe.pdf',
            'tags': [{'name': 'Viet Nam'}, {'name': 'Breakfast'}],
            'ingredients': [{'name': 'Rice'}, {'name': 'Meat'}]
        }

        res = self.client.post(URL_RECIPE, sample_test, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        self.assertEqual(recipes[0].ingredients.count(), 2)
        self.assertIn(ingredient, recipes[0].ingredients.all())

        for ingredient in sample_test['ingredients']:
            exists = recipes[0].ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_ingredient_when_update(self):
        """Test create a ingredient when update a recipe"""

        recipe = create_recipe(user=self.user)
        sample_ingredient = {'ingredients': [{'name': 'Sugar'}]}
        url = detail_url(recipe.id)

        res = self.client.patch(url, sample_ingredient, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        update_ingredient = Ingredient.objects.get(
            user=self.user,
            name='Sugar',
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(update_ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self):
        """Test assign an existing ingredient when update a recipe"""

        default_ingredient = Ingredient.objects.create(
            user=self.user,
            name='Lemon'
        )

        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(default_ingredient)

        update_ingredient = Ingredient.objects.create(
            user=self.user,
            name='Basil'
        )
        sample = {'ingredients': [{'name': 'Basil'}]}
        url = detail_url(recipe.id)

        res = self.client.patch(url, data=sample, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(update_ingredient, recipe.ingredients.all())
        self.assertNotIn(default_ingredient, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """Test clear recipe ingredients"""

        ingredient1 = Ingredient.objects.create(user=self.user, name='Pepper')
        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name='Fish sauce'
        )

        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1, ingredient2)

        sample = {'ingredients': []}
        url = detail_url(recipe.id)

        res = self.client.patch(url, sample, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_filter_by_tags(self):
        """Test filter recipes by tag"""
        recipe1 = create_recipe(user=self.user, title='Grilled Pork')
        recipe2 = create_recipe(user=self.user, title='Mushroom Soup')
        recipe3 = create_recipe(user=self.user, title='Super Idol')
        tag1 = Tag.objects.create(user=self.user, name='Vegan')
        tag2 = Tag.objects.create(user=self.user, name='Carnism')

        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)

        params = {'tags': f'{tag1.id},{tag2.id}'}
        res = self.client.get(URL_RECIPE, params)

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_by_ingredients(self):
        """Test filter recipes by ingredients"""
        recipe1 = create_recipe(user=self.user, title='Sweet Cake')
        recipe2 = create_recipe(user=self.user, title='Salty Bread')
        recipe3 = create_recipe(user=self.user, title='Super Idol')
        ingredient1 = Ingredient.objects.create(user=self.user, name='Sugar')
        ingredient2 = Ingredient.objects.create(user=self.user, name='Salt')

        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)

        params = {'ingredients': f'{ingredient1.id},{ingredient2.id}'}
        res = self.client.get(URL_RECIPE, params)

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)


# For test upload images
class ImageUploadTests(TestCase):
    """Tests for image upload API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='Test@example.com',
            password='testpassword123',
        )

        # Authenticate user
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    # setUp running before the test and tearDown
    # run after the test
    # Delete image after every test for not buildings up
    # database ?
    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        """Test upload image to recipe"""
        url = image_upload_url(self.recipe.id)

        # Create tempoary file (with then it will clean up)
        # Create tempoary image file to test upload to
        # endpoint
        # Image file that a user will be uploading (like
        # upload from their local machine)
        # When upload that image, this will be a new image file
        # and store that version of image on the server
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:

            # Create a new image and save as  tempoary file that created
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')

            # Need seek back to the begining of the file
            # to upload image (seek the pointer)
            image_file.seek(0)

            # Generate sample payload assign image field is the image file
            # that we want to upload using multipart format ?
            sample = {'image': image_file}
            res = self.client.post(url, sample, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Check image field in response
        self.assertIn('image', res.data)

        # Check path of image exsist in system
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_with_bad_request(self):
        """Test upload invalid image"""
        url = image_upload_url(self.recipe.id)
        sample = {'image': 'NO_IMAGE'}

        res = self.client.post(url, sample, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
