from django.utils import timezone
from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

#custom serializer for validating credentials using email and password and sending role in it.
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Get email and password from the request
        email = attrs.get('email')
        password = attrs.get('password')

        if email is None or password is None:
            raise AuthenticationFailed('Email and password are required')

        # Try to get the user by email
        # user_model = get_user_model()
        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            raise AuthenticationFailed('No user found with this email')

        # Check if the user’s password is correct
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password')

        # If everything is fine, set the user for JWT token creation
        attrs['user'] = user

        # Add the user's role to the JWT payload
        return super().validate(attrs)

    def get_token(self, user):
        # Get the token from the base class
        token = super().get_token(user)

        # Add custom claims, such as role, to the token
        token['role'] = user.role  # Add the user's role to the token

        return token