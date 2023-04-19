"""
DB models
"""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)

from django.conf import settings


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


# Use model base class for recipe
class Recipe(models.Model):
    """Recipe model"""

    # Foreign key is User (better is id)
    user = models.ForeignKey(
        # Reference settings from app.settings.py
        # to apply changes from user model (AUTH_USER_MODEL)
        # search more settings.AUTH_USER_MODEL vs get_user_model
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=255)  # for larger strings
    minute_to_make_recipe = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField(to='Tag')
    ingredients = models.ManyToManyField(to='Ingredient')

    # To string method to return title
    def __str__(self):
        return self.title


class Tag(models.Model):
    """Tag for recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient for recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
