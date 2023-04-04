"""
Custom Django admin
"""

from django.contrib import admin

# Import as base class to customize
# Dont meet conflict other UserAdmin uses
from django.contrib.auth.admin import UserAdmin

# Import translation option
from django.utils.translation import gettext_lazy

# Import customed models
from . import models

class MyAdmin(UserAdmin):
    """Custom admin page"""

    # Order by id and show
    # only name + email
    ordering = ['id']
    list_display = ['email', 'name']

    # Customized fields sets, only
    # specified fields exist in model
    # created by me or intergrated with
    # permissionmixin like is_active,
    # is_staff, is_staff email, password
    fieldsets = (
        # Fields set, no title = None
        (None, {'fields': ('email', 'password')}),
        (
            gettext_lazy('Permission'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (gettext_lazy('Dates'), {'fields': ('last_login',)})
    )

    # Add read only fields
    readonly_fields = ['last_login']

# Register the model that use
# this admin
admin.site.register(models.User, MyAdmin)
