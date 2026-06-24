from rest_framework import serializers
from django.contrib.auth import authenticate
from ..models import CustomUser


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'fullname']


class AuthTokenSerializer(serializers.Serializer):
    """Serializer für Email-basierte Authentifizierung"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                username=email, password=password)
        else:
            msg = 'Email und Password sind erforderlich.'
            raise serializers.ValidationError(msg, code='authorization')

        if not user:
            msg = 'E-Mail oder Passwort ist ungültig.'
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
        pw = data['password']
        rep_pw = data.pop('repeated_password')

        if pw != rep_pw:
            raise serializers.ValidationError(
                {'repeated_password': 'Passwords do not match'})
        return data

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            fullname=validated_data['fullname'],
            password=validated_data['password']
        )
        return user
