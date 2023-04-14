"""
Serializer user API view
"""
from django.contrib.auth import get_user_model, authenticate  # noqa

from django.utils.translation import gettext # noqa

from rest_framework import serializers

from core.models import User


# Create base class for model serialization
# to serialize data
class UserSerializer(serializers.ModelSerializer):
    """Serializer user model to python primitives"""

    # Using meta options
    class Meta:

        # Tell what model is representing
        # in this serialize
        # Serialize for our user modell
        model = User

        # Enable fields want to serialize
        fields = ['name', 'email', 'password']

        # Password settings for validate, if error
        # method create will not be called
        # Set 'write_only' to true to ensure that the field may be used
        # when updating or creating an instance, but is not included when
        # serializing the representation
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    # Overide default create method from
    # serializers.ModelSerializer by our
    # create_user method
    # validated_data: data passed through serialize
    # validation (in this case is name, email. pass)
    def create(self, validated_data):
        """Create a user with hashed password"""
        return User.objects.create_user(**validated_data)

    # Purpose of override is just configure the password
    # instance is the model instance going to be updated
    # validated data same as create above
    def update(self, instance, validated_data):
        """Update user"""

        # Get password from validated_data (field password in this dict)
        # Because we dont force user to change password in this request so
        # set password field to non
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        # Update the old password for user
        if password:
            # Must define password, if not it will stored in clear text
            user.set_password(password)
            user.save()

        return user


# Create a base class for serialize
# authentication token
class AuthTokenSerializer(serializers.Serializer):
    """Serializer for user authentication token"""

    # Serialize two fields: email and password
    email = serializers.EmailField()

    # Choose type password of CharField (for hidden)
    # and does not remove whitespace
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    # Define a validated method for token
    # serializer
    def validate(self, data):
        """Validate and authenticate user"""

        # Retrive email and password user provided
        # for validating
        email = data.get('email')
        password = data.get('password')

        # Call authentication built in function
        # Check password, email if it correct, return
        # user, if not, return empty object
        user = authenticate(
            # Request a context (like: head of message data)
            # May be to make sure request passed consistently ?
            request=self.context.get('request'),

            # Using email as username (define USERNAME_FIELD='email)
            # Check these fields are correct
            username=email,
            password=password,
        )

        # Check the return and raise error
        if not user:
            msg = gettext('Cannot authenticate user with given credentials')
            raise serializers.ValidationError(msg, code='authorization')

        # Set the user atribute with validated
        data['user'] = user
        return data
