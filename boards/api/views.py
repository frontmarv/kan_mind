from rest_framework.views import APIView
from .serializers import BoardListSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Board
from api.mixins import UserAuthenticationMixin
from rest_framework.exceptions import NotAuthenticated, PermissionDenied


class BoardListView(UserAuthenticationMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        boards = Board.objects.all()
        boardsWithPermissions = []
        for board in boards:
            if request.user == board.owner or request.user in board.members.all():
                boardsWithPermissions.append(board)
        serializer = BoardListSerializer(boardsWithPermissions, many=True)
        return Response(serializer.data, headers={'message': 'Erfolgreich. Gibt eine Liste der Boards zurück.'}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = BoardListSerializer(data=request.data)
        if serializer.is_valid():
            board = serializer.save(owner=request.user)
            response_serializer = BoardListSerializer(board)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
