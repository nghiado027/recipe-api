"""
View of user API
"""
# Using generics views for handle
# request
# Search more APIview, viewset,
# GenericsAPIView
# authentication and permission for token
from rest_framework import generics, authentication, permissions
from user.serializers import UserSerializer

# For token
from rest_framework.authtoken.views import ObtainAuthToken  # for login
from rest_framework.settings import api_settings
from user.serializers import AuthTokenSerializer  # import serializer of token


# Create API handles HTTP post request
# for creating objects in database and logic
class CreateUserAPIView(generics.CreateAPIView):
    """Create a new user"""

    # Define serializer class
    # Serianlize part already define in Meta
    # option in UserSerializer class
    serializer_class = UserSerializer


# This view use token serializer we defined
# Link to a URL to handle token authentication
class CreateTokenView(ObtainAuthToken):
    """Create a authentication token for user"""

    # Define serializer class (using our customized)
    serializer_class = AuthTokenSerializer

    # Optional, it uses default render of classes for
    # token view
    # Manually add inside the view just in case
    # to get the browser or interface to show API ? (dont know why)
    # Define render class (using default in api)
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


# This view for API user profile page
# Using built in retreving and updating objects
# in the db
class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage authenticated user profile"""
    serializer_class = UserSerializer

    # How do you know that the user is the user say they are ?
    authentication_classes = [authentication.TokenAuthentication]

    # Who the user is, a particular user is allowed to do in system ?
    # must authenticated to use this api
    permission_classes = [permissions.IsAuthenticated]

    # Override get_object() method
    # to retriving user attach to request (make for)
    def get_object(self):
        """Retrive and return authenticated user"""
        return self.request.user
