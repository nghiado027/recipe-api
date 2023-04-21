"""
Views for recipe API
"""

from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from recipe import serializers

# For custom action
from rest_framework.decorators import action
from rest_framework.response import Response

# For filtering ?
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes
)


# Decorated to extend the auto generated
# schema that created by Django rest spectacular ?
@extend_schema_view(

    # Define list to extend schema for the
    # list endpoint (we add these filter tag and ingredient)
    list=extend_schema(

        # Define params that can be passed to the requests that are made
        # to the list API for this view, we using OpenAPI paramters provided
        # by drf sepctacular allow us to specify details of a paramter
        # accepted in API request ?
        parameters=[
            OpenApiParameter(

                # Define name to to pass in to filter
                name='tags',
                # Accept params as string (IDs string) bc we
                # want to seperated to list of intergers (we
                # convert in this view class)
                type=OpenApiTypes.STR,
                # For documentation
                description='Seperated by comma list of tag IDS to filter',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Seperated comma list of ingredient IDS to filter',
            ),
        ]
    )
)
class RecipeAPIViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs as list and id"""
    serializer_class = serializers.RecipeDetailSerializer

    # For custom api detail endpoint instead
    # of ../api/recipe/recipes/{id}

    # lookup_field = 'title'

    # queryset field represent objects
    # that available for this viewset
    # because it's a model viewset so
    # it's expected work with a model
    # This line define which models use
    # for specify the queryset
    # This is the query set of objects
    # that going to be  manageable through
    # this API or through the APIs that are
    # available through our model view ?
    queryset = Recipe.objects.all()

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # List paramters from list of integer (id)
    # to accept filter arguments as a list of IDs
    # as comma seperated string
    def _params_to_list_ints(self, query_string):
        """Convert list of strings to integers"""
        return list(map(int, query_string.split(',')))

    # Get list of recipes base on authenticated user (authen above)
    # Override this get_queryset to get the current logged user using
    # self.request.user ? (define in AUTH_USER_MODEL)
    # This method from GenericViewSet -> GenericAPIView
    def get_queryset(self):
        """Retrieve recipes for this authenticated user"""

        # Get by comman queryset ?tags=1,2,3&ingredients=1,2,3
        # using query_params ? (request.query_params ~ request.GET)
        # https://www.django-rest-framework.org/api-guide/requests/
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')

        # Define a queryset
        queryset = self.queryset

        # Filter ManyToMany Fields ?
        # We make filter is an optional
        if tags:
            # Convert params from string to list in as
            # defined that represent primary key
            tag_ids = self._params_to_list_ints(tags)

            # Double underscore in queryset mean Field lookup ?
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_list_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        # Call specific user
        # Retrive all object then filter by user (must optimize ?)
        # We want user manage only their recipe (create, view, update)
        # return self.queryset.filter(user=self.request.user).order_by('id')
        # Update for multiple filter, use distinct for not duplicate
        # recipe with same tag same ingredients (base on logic of our
        # code above)
        return queryset.filter(
            user=self.request.user
        ).order_by('id').distinct()

    # Override this method to let DRF call
    # for a particular action ?
    def get_serializer_class(self):
        """Return the serializer class for request"""

        # If want a list (HTTP get all object), use RecipeSerializer
        # is enough
        if self.action == 'list':
            return serializers.RecipeSerializer
        # For upload image, we define a
        # custom action
        elif self.action == 'upload_image':
            return serializers.RecipeDetailImageSerializer

        return self.serializer_class

    # Method for our existing view in order to
    # tell it to save correct user to recipe created
    # Override create method perform_create
    # (DRF save model in a viewset)
    # to create feature of viewset ?
    # Create an object through the model viewset
    # Serializer should be a validated serializer
    def perform_create(self, serializer):
        """Create recipe"""
        # This is a current authenticated user
        serializer.save(user=self.request.user)

    # Custom action for upload image ?
    # Using action decorators let us specify HTTP method support for
    # this custom action
    # detail=True: apply to the detail portion of our model viewset, mean
    # that specific id of recipe, we want apply this custom action
    # to detail endpoint ?
    # not detail ~ list view, generic list of the recipe
    # url_path = custom url path for our action
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):

        # Get recipe object by the primary key
        # we specify in this action
        recipe = self.get_object()

        # get_serializer take class in get_serializer_class that
        # we override to get Image serializer class for this action
        serializer = self.get_serializer(recipe, data=request.data)

        # Check if valid then save and response
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='Assigned to Recipes ?',
                type=OpenApiTypes.INT,
                # True/ False chack in id_assigned in get_queryset
                # define specific options for making the request
                # in API docs (just 2 different int values can assign
                # to this particular API parameters)
                # This for filter Recipes that
                # has tag/ingredients or not (0, 1)
                enum=(0, 1),
                description="Filter tags/ingredient that assigned to Recipes?"
            )
        ]
    )
)
# Implement basic CRUD so just leverage viewset
# base class
# GenericViewSet allow to mixin, it has view set
# functionality to design a particular API ?
# mixins.ListModelMixin for update (the same as
# destroy, list, ...) check mixin with model ?
# In this project, we let user create tag, ingredient
# through recipe API
class BaseRecipeAtributeViewSet(mixins.ListModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.DestroyModelMixin,
                                viewsets.GenericViewSet):

    """Base viewset recipe atribute (tag, ingredients)"""
    # Must authenticated
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Override get_queryset method to make sure
    # return only queryset object for authenticated
    # user by default.
    def get_queryset(self):
        """Filter queryset by authenticated user"""

        # Bool to check if provided (like if else)
        # if get default is 0 => failse
        ids_assigned = bool(
            # Set default value is 0 (of .get)
            # If ids_assigned not provided, else not set is 0
            int(self.request.query_params.get('ids_assigned', 0))
        )

        queryset = self.queryset

        if ids_assigned:
            # Remove null recipe in filter, when tag/ingredients
            # assign to recipe in system, then we delete that recipe
            # a tag/ingredients has no recipe associated with it
            # still appear in listing (tag/ingredients) but
            # by ManyToMany Field so recipe field set to null ?
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('name').distinct()


class TagViewSet(BaseRecipeAtributeViewSet):
    """Manage tags """

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAtributeViewSet):
    """Manage ingredient"""

    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
