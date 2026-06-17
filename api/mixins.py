from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework import status


class Forced401Unauthenticated(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Nicht autorisiert. Der Benutzer muss eingeloggt sein.'
    default_code = 'not_authenticated'


class UserAuthenticationMixin:
    def permission_denied(self, request, message=None, code=None):
        if request.authenticators and not request.successful_authenticator:
            raise Forced401Unauthenticated()

        raise PermissionDenied(detail=message, code=code)
