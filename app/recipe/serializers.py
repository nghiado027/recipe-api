"""
Serializers for recipe API
"""
from rest_framework import serializers
from core.models import Recipe

from django.utils.translation import gettext # noqa


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe"""

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'minute_to_make_recipe', 'price', 'link']
        read_only_fields = ['id']


# Extend RecipeSerializer above
class RecipeDetailSerializer(RecipeSerializer):

    # Meta class base on too
    class Meta(RecipeSerializer.Meta):

        # Add serialize description
        fields = RecipeSerializer.Meta.fields + ['description']
