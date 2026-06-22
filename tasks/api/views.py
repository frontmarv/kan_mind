from rest_framework.views import APIView
from .serializers import TaskViewSerializer, TaskChangeSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Task, Comment
from api.mixins import UserAuthenticationMixin
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404


class AssignedTasksView(UserAuthenticationMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks_assigned_to_me = Task.objects.filter(assignee=request.user)
        serializer = TaskViewSerializer(tasks_assigned_to_me, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewingTaskView(UserAuthenticationMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks_reviewing = Task.objects.filter(reviewer=request.user)
        serializer = TaskViewSerializer(tasks_reviewing, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TaskViewSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH', 'DELETE'])
def task_single_view(request, pk):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    task = get_object_or_404(Task, pk=pk)
    board_members = task.board.members.all()
    if request.user not in board_members:
        return Response(
            {"detail": "Verboten. Der Benutzer muss Mitglied des Boards sein, um diese Task zu bearbeiten oder zu löschen."},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method == 'PATCH':
        serializer = TaskChangeSerializer(
            task, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            full_data = serializer.data
            filtered_data = {
                "id": full_data["id"]
            }
            for key in request.data.keys():
                response_key = key[:-3] if key.endswith('_id') else key
                if response_key in full_data:
                    filtered_data[response_key] = full_data[response_key]
            return Response(filtered_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        serializer = TaskChangeSerializer(task)
        data = serializer.data
        task.delete()
        return Response(data, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def task_single_view_comments(request, task_id):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    task = get_object_or_404(Task, pk=task_id)
    board_members = task.board.members.all()
    if request.user not in board_members:
        return Response(
            {"detail": "Verboten. Der Benutzer muss Mitglied des Boards sein."},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method == 'GET':
        comments = Comment.objects.filter(task=task).order_by('created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, task=task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE'])
def task_single_view_comment(request, task_id, comment_id):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    task = get_object_or_404(Task, pk=task_id)
    board_members = task.board.members.all()

    if request.user not in board_members:
        return Response(
            {"detail": "Verboten. Der Benutzer muss Mitglied des Boards sein."},
            status=status.HTTP_403_FORBIDDEN
        )

    comment = get_object_or_404(Comment, pk=comment_id)

    if request.method == 'GET':
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        if comment.author != request.user:
            return Response(
                {"detail": "Du bist nicht berechtigt, diesen Kommentar zu löschen."},
                status=status.HTTP_403_FORBIDDEN
            )
        comment.delete()
        return Response(
            {"detail": "Der Kommentar wurde erfolgreich gelöscht."},
            status=status.HTTP_204_NO_CONTENT
        )
