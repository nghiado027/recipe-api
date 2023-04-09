"""
DB models
"""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)


class MyUserManager(BaseUserManager):
    """My custom Manager of users"""

    def create_user(self, email, password=None, **other_fields):
        """Create and save user"""

        # Check if email field is blank
        # and raise error
        if not email:
            raise ValueError('User must type email address')

        # The way to access model that associated
        # with the manager
        # Call self.model will be the same as
        # defining new user object out of user class
        # because this manager going to be assigned
        # to user class below
        user = self.model(
            # Add normailized eamil method
            email=self.normalize_email(email),
            **other_fields
        )

        # Hashing password
        user.set_password(password)

        # ._db support multiple database
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **other_fields):
        """Create and save superuser"""
        user = self.create_user(
            email=email,
            password=password,
            **other_fields
        )

        # is_superuser = full control any objects
        user.is_superuser = True

        # is_staff = log in as admin interface
        # of our organize for example
        user.is_staff = True
        user.save(using=self._db)

        return user

# AbstractBaseUser contains only func
# for authen system and no actual fields
# create user without reuse email,
# password (compare with AbstractUser)
# PermissionsMixin contains func for
# permission feature and others field
# might need


class User(AbstractBaseUser, PermissionsMixin):
    """User system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.TextField(max_length=255)

    # User is active
    is_active = models.BooleanField(default=True)

    # Check if Django admin user login
    is_staff = models.BooleanField(default=False)

    # Assign custom user manager we define
    # above
    objects = MyUserManager()

    # For replace username default field
    # with default user model to our custom
    # email field
    # Deffine field for authen later
    USERNAME_FIELD = 'email'
