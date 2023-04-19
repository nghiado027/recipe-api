"""
URL mapping for recipe API (to views)
"""
from django.urls import path, include

# Use with an API view to automatically create
# routes for all of different options
from rest_framework.routers import DefaultRouter
from recipe import views

# Create a new endpoint API
# https://www.django-rest-framework.org/api-guide/routers/#defaultrouter ?
# '{lookup}' in this case is 'id' check the views so we know that
# why it generate those endpoint for api
router = DefaultRouter()

# Dont need to add forward slash, bc router will
# create full url
# Assign all endpoints from recipe viewset to 'recipes'
# endpoint (like create, read, update,... that viewset
# supported, it will create and register endpoints for
# each of those options)
router.register('recipes', views.RecipeAPIViewSet)
router.register('tags', views.TagViewSet)
router.register('igredients', views.IngredientViewSet)
# Name for reverse lookup
app_name = 'recipe'

urlpatterns = [
    # router created above
    # It figures the url that are require for
    # all of function that added to viewset
    # It will generated list of urls associated
    # to our viewset
    path('', include(router.urls)),
]
