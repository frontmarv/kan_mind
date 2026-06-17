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


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = RegistrationSerializer(data=request.data)

            if serializer.is_valid():
                saved_account = serializer.save()
                token, created = Token.objects.get_or_create(
                    user=saved_account)
                response_data = {
                    'token': token.key,
                    'fullname': saved_account.fullname,
                    'email': saved_account.email,
                    'user_id': saved_account.id
                }
                return Response(response_data, headers={'message': 'Der Benutzer wurde erfolgreich erstellt.', }, status=status.HTTP_201_CREATED)

            else:
                response_data = {
                    'message': 'Ungültige Anfragedaten.',
                    'errors': serializer.errors
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response_data = {
                'message': 'Interner Serverfehler.'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = AuthTokenSerializer(
                data=request.data, context={'request': request})
            if serializer.is_valid():
                user = serializer.validated_data['user']
                token, created = Token.objects.get_or_create(user=user)
                response_data = {
                    'message': 'Erfolgreiche Anmeldung.',
                    'user': {
                        'token': token.key,
                        'fullname': user.fullname,
                        'email': user.email,
                        'user_id': user.id
                    }
                }
                return Response(response_data, status=status.HTTP_200_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response_data = {
                'message': 'Ungültige Anfragedaten.'
            }
        return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
