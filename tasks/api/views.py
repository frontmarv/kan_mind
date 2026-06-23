from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import TaskChangeSerializer, CommentSerializer, TaskSerializer
from ..models import Task, Comment
from api.mixins import UserAuthenticationMixin
from boards.models import Board


class TaskFilterView(UserAuthenticationMixin, APIView):
    permission_classes = [IsAuthenticated]
    filter_field = None

    def get(self, request):
        filters = {self.filter_field: request.user}
        tasks = Task.objects.filter(**filters)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AssignedTasksView(TaskFilterView):
    filter_field = 'assignee'


class ReviewingTaskView(TaskFilterView):
    filter_field = 'reviewer'


class TaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        board_id = request.data.get('board')
        board = get_object_or_404(Board, id=board_id)
        if request.user not in board.members.all():
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = TaskSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def task_single_view(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.user not in task.board.members.all():
        return Response(status=status.HTTP_403_FORBIDDEN)

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


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def task_single_view_comments(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.user not in task.board.members.all():
        return Response(status=status.HTTP_403_FORBIDDEN)

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


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def task_single_view_comment(request, task_id, comment_id):
    task = get_object_or_404(Task, pk=task_id)
    comment = get_object_or_404(Comment, pk=comment_id)

    if request.user not in task.board.members.all():
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == 'DELETE':
        if comment.author != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
