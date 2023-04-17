"""
Serializers for recipe API
"""
from rest_framework import serializers
from core.models import Recipe, Tag

from django.utils.translation import gettext # noqa


# Tag serializer
class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags"""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe"""

    # This will becom nested serializer
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'minute_to_make_recipe',
                  'price', 'link', 'tags']
        read_only_fields = ['id']

    # Helper function for get_or_create
    def _get_or_create_tags(self, tags, recipe):
        """Getting or creating tags as a method"""

        # Get authenticated user, because we are
        # using a serializer not the views so we use
        # .context of the request
        # The context passed to serialiers by the view
        # when using serializer for particular view, this
        # is the way that we get context from actual serializer
        # code ?
        authen_user = self.context['request'].user

        # Create each tag object base on tags in validated_data
        for tag in tags:

            # get_or_create: if exist = get, if not = get
            # this is for not create duplicate tag in system
            obj, _ = Tag.objects.get_or_create(
                user=authen_user,
                **tag,  # add the rest of atri in tag
            )
            recipe.tags.add(obj)

    # Override to allow to change tag
    # bc nested serializer default is read_only_field
    # mean can read the values but can't create items
    # with those value
    def create(self, validated_data):
        """Create a recipe"""

        # Remove and retrive tags data from validated_data
        # To ensure pop return as list (tags), put '[]'
        tags = validated_data.pop('tags', [])

        # Create a recipe with remain data
        # Tags cannot directly added to in Recipe model
        # it expected tags to be assigned as a related field
        # so we need to created tags separately and added as
        # a relationship to recipe as ManyToManyFields as we
        # defined ?
        recipe = Recipe.objects.create(**validated_data)

        self._get_or_create_tags(tags, recipe)

        return recipe

    # Override to allow to change tag
    # bc nested serializer default is read_only_field
    # same reason as create method for change tag (nested serialize)
    def update(self, instance, validated_data):
        """Update recipe"""

        # If tags in validated data is empty,
        # assign tags variable to None
        tags = validated_data.pop('tags', None)

        if tags is not None:
            # clear all tags and replace with
            # validated_data tag (bc its just update)
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


# Extend RecipeSerializer above
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for detail recipe"""

    # Meta class base on too
    class Meta(RecipeSerializer.Meta):

        # Add serialize description
        fields = RecipeSerializer.Meta.fields + ['description']
