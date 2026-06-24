from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import TaskChangeSerializer, CommentSerializer, TaskSerializer
from ..models import Task, Comment
from board_app.models import Board


class TaskFilterView(APIView):
    """
    Base class for filtering tasks by a specific user field.
    Provides common filtering logic reused by AssignedTasksView and ReviewingTaskView.
    Subclasses override filter_field to specify which user relation to filter by.
    """
    permission_classes = [IsAuthenticated]
    filter_field = None

    def get(self, request):
        """
        Returns tasks filtered by the specified user field (assignee or reviewer).
        Uses filter_field attribute to determine which relation to filter.
        """
        filters = {self.filter_field: request.user}
        tasks = Task.objects.filter(**filters)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AssignedTasksView(TaskFilterView):
    """
    Custom view for retrieving tasks assigned to the current user.
    Inherits filtering logic from TaskFilterView with filter_field='assignee'.
    """
    filter_field = 'assignee'


class ReviewingTaskView(TaskFilterView):
    """
    Custom view for retrieving tasks assigned for review to the current user.
    Inherits filtering logic from TaskFilterView with filter_field='reviewer'.
    """
    filter_field = 'reviewer'


class TaskView(APIView):
    """
    Custom view for creating tasks with board membership validation.
    Ensures user creating a task is a member of the target board before
    allowing task creation.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Creates a new task with permission check.
        Validates that the requesting user is a member of the specified board.
        """
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
    """
    Custom single task view with update and delete functionality.
    Implements custom response filtering: only fields that were requested
    in the PATCH request are returned, not the complete serialized object.
    This reduces response payload and provides focused feedback to the client.
    """
    task = get_object_or_404(Task, pk=pk)

    if request.user not in task.board.members.all():
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PATCH':
        # Updates task and returns only the modified fields.
        # Constructs response to include only fields that were in the request.
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
        # Deletes the task and returns its data before deletion.
        serializer = TaskChangeSerializer(task)
        data = serializer.data
        task.delete()
        return Response(data, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def task_single_view_comments(request, task_id):
    """
    Custom view for managing task comments.
    GET: Retrieves all comments for a task ordered by creation date.
    POST: Creates a new comment, automatically associating it with the
    requesting user as the author and the specified task.
    """
    task = get_object_or_404(Task, pk=task_id)
    if request.user not in task.board.members.all():
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        # Retrieves comments ordered by creation date (newest first).
        comments = Comment.objects.filter(task=task).order_by('created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        # Creates a comment with automatic author and task assignment.
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(author=request.user, task=task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def task_single_view_comment(request, task_id, comment_id):
    """
    Custom view for deleting individual comments.
    Only the comment author can delete their own comments.
    Ensures user is a board member and comment author before allowing deletion.
    """
    task = get_object_or_404(Task, pk=task_id)
    comment = get_object_or_404(Comment, pk=comment_id)

    if request.user not in task.board.members.all():
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == 'DELETE':
        # Deletes comment only if requesting user is the author.
        if comment.author != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
