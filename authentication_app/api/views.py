from .serializers import RegistrationSerializer, AuthTokenSerializer, UserProfileSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from ..models import CustomUser
from rest_framework.permissions import IsAuthenticated


class EmailCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuthBaseView(APIView):
    """
    Custom base view for authentication endpoints.
    Provides shared functionality for login and registration views.
    """
    permission_classes = [AllowAny]

    def get_user_response(self, user):
        """
        Custom method for generating user response with token.
        Creates or retrieves a DRF token and builds a standardized response
        containing token, user data, and user ID. Used to ensure consistent
        authentication responses for both login and registration endpoints.
        """
        token, _ = Token.objects.get_or_create(user=user)
        return {
            'token': token.key,
            'fullname': user.fullname,
            'email': user.email,
            'user_id': user.id
        }


class RegistrationView(AuthBaseView):
    """
    Registration endpoint with custom error handling.
    Inherits custom get_user_response() to provide standardized token-based
    responses after successful registration.
    """

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(self.get_user_response(user), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(AuthBaseView):
    """
    Login endpoint with email-based authentication.
    Inherits custom get_user_response() to provide standardized token-based
    responses after successful authentication.
    """

    def post(self, request):
        serializer = AuthTokenSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response(self.get_user_response(user), status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
