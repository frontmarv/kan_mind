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
            return Response(
                {"error": "Ungültige Anfrage. Die E-Mail-Adresse fehlt oder hat ein falsches Format."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Email nicht gefunden. Die Email exestiert nicht."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
