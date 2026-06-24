from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import BoardListSerializer, BoardSingleViewSerializer, BoardUpdateSerializer
from ..models import Board


class BoardListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        boards = Board.objects.all()
        boardsWithPermissions = []
        for board in boards:
            if request.user == board.owner or request.user in board.members.all():
                boardsWithPermissions.append(board)
        serializer = BoardListSerializer(boardsWithPermissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = BoardListSerializer(data=request.data)
        if serializer.is_valid():
            board = serializer.save(owner=request.user)
            response_serializer = BoardListSerializer(board)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def board_single_view(request, pk):
    board = get_object_or_404(Board, pk=pk)
    is_owner = request.user == board.owner
    is_member = request.user in board.members.all()

    if request.method == 'GET':
        if is_owner or is_member:
            serializer = BoardSingleViewSerializer(board)
            return Response(serializer.data)
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PATCH':
        if is_owner or is_member:
            serializer = BoardUpdateSerializer(
                board, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == 'DELETE':
        if is_owner:
            serializer = BoardSingleViewSerializer(board)
            data = serializer.data
            board.delete()
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)
