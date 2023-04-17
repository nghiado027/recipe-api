"""
Views for recipe API
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe import serializers


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
        return self.queryset.filter(user=self.request.user).order_by('id')

    # Override this method to let DRF call
    # for a particular action ?
    def get_serializer_class(self):
        """Return the serializer class for request"""

        # If want a list (HTTP get all object), use RecipeSerializer
        # is enough
        if self.action == 'list':
            return serializers.RecipeSerializer

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
