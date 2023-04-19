"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin

# This 'include' helper function
# allow to add URLS from different app
from django.urls import path, include

# For static media file
from django.conf.urls.static import static
from django.conf import settings

# Import spectacular to link url
# to serve api document
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Define api/schema as a view of api schema
    # to generate schema file
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),

    # For document api link using swagger
    # from api_schema url (define above)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='api-schema'),
         name='api-doc'),

    # Add user view url to main app
    # 'user.urls' is file path
    path('api/user/', include('user.urls')),

    # Add recipe
    path('api/recipe/', include('recipe.urls'))
]

# For debug mode, serving media file from local
# In production local files will not accessible (must)
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
