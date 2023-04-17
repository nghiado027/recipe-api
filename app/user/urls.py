"""
URL mapping for user API (to views)
"""
from django.urls import path
from user import views

# Define to use 'reverse' mapping
# in test user API
# In tests/test_api_user.py we define
# that REATE_USER_PATH = reverse('user:create')
# so app name must be 'user'
# Whenever the reverse(...) function get
# executed, Django looking for an
# application namespace first, than any other
app_name = 'user'

# Mapping path to view
urlpatterns = [
    # Define 'create' path in 'user:create'
    # from app name
    # Because 'view' parameter in path expect
    # a function so use .as_view() method
    # to get view function, this is the way
    # that DRF converts class view to supported
    # Django view
    # Define the 'name' for 'reverse' lookup
    path('create/', view=views.CreateUserAPIView.as_view(), name='create'),

    # Define URL for token
    path('token/', view=views.CreateTokenView.as_view(), name='token'),

    # Define URL for user profile
    path('me/', view=views.ManageUserView.as_view(), name='me'),
]
