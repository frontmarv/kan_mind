from rest_framework.permissions import BasePermission
from boards.models import Board


class IsMemberOfBoard(BasePermission):
    """
    Permission, um zu überprüfen, ob der User Mitglied des Boards ist,
    auf das sich die Anfrage bezieht.
    """

    def has_permission(self, request, view):
        # Board ID aus der Anfrage auslesen
        board_id = request.data.get('board') if hasattr(
            request, 'data') else None

        if not board_id:
            return False

        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return False

        # User muss entweder Owner oder Member des Boards sein
        return request.user == board.owner or request.user in board.members.all()
