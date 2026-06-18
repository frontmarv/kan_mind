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
        current_user = request.user
        serializer = UserProfileSerializer(current_user)
        if serializer.data['email'] == "":
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)


class AuthBaseView(APIView):
    permission_classes = [AllowAny]

    def get_user_response(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        return {
            'token': token.key,
            'fullname': user.fullname,
            'email': user.email,
            'user_id': user.id
        }


class RegistrationView(AuthBaseView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(self.get_user_response(user), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(AuthBaseView):
    def post(self, request):
        serializer = AuthTokenSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response(self.get_user_response(user), status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
