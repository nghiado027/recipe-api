"""
Views for recipe API
"""

from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from recipe import serializers

from rest_framework.decorators import action
from rest_framework.response import Response


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

    # Get list of recipes base on authenticated user (authen above)
    # Override this get_queryset to get the current logged user using
    # self.request.user ? (define in AUTH_USER_MODEL)
    # This method from GenericViewSet -> GenericAPIView
    def get_queryset(self):
        """Retrieve recipes for this authenticated user"""

        # Call specific user
        # Retrive all object then filter by user (must optimize ?)
        # We want user manage only their recipe (create, view, update)
        return self.queryset.filter(user=self.request.user).order_by('id')

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
        serialier = self.get_serializer(recipe, data=request.data)

        # Check if valid then save and response
        if serialier.is_valid():
            serialier.save()
            return Response(data=serialier.data, status=status.HTTP_200_OK)

        return Response(serialier.errors, status=status.HTTP_400_BAD_REQUEST)


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
        return self.queryset.filter(user=self.request.user).order_by('name')


class TagViewSet(BaseRecipeAtributeViewSet):
    """Manage tags """
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAtributeViewSet):
    """Manage ingredient"""

    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
