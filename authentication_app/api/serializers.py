from rest_framework import serializers
from django.contrib.auth import authenticate
from ..models import CustomUser


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'fullname']


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for email-based authentication."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, data):
        """
        Custom validation using email instead of username for authentication.
        Overrides default Django username-based authentication to support email-based auth.
        """
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                username=email, password=password)
        else:
            msg = 'Email and password are required.'
            raise serializers.ValidationError(msg, code='authorization')

        if not user:
            msg = 'Invalid email or password.'
            raise serializers.ValidationError(msg, code='authorization')

        data['user'] = user
        return data


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'fullname', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        """
        Custom validation for password confirmation.
        Compares entered password with repeated password to ensure they match.
        Removes 'repeated_password' from validated data as it's only needed for validation
        and is not stored in the database.
        """
        pw = data['password']
        rep_pw = data.pop('repeated_password')

        if pw != rep_pw:
            raise serializers.ValidationError(
                {'repeated_password': 'Passwords do not match'})
        return data

    def validate_email(self, value):
        """
        Custom email validation to prevent duplicates.
        Checks if the email already exists in the database and raises an error
        if attempting to register with an already existing email address.
        """
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def create(self, validated_data):
        """
        Custom user creation with secure password handling.
        Uses create_user() instead of create() to properly hash the password.
        Overrides the default ModelSerializer create method to work with the custom User model
        that uses email-based authentication instead of username.
        """
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            fullname=validated_data['fullname'],
            password=validated_data['password']
        )
        return user
