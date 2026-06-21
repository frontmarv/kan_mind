from rest_framework.views import APIView
from .serializers import TaskSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Task
from api.mixins import UserAuthenticationMixin
from rest_framework.views import APIView
from .permissions import IsMemberOfBoard
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes


class AssigendTasksView(UserAuthenticationMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks_assigned_to_me = Task.objects.filter(assignee=request.user)
        serializer = TaskSerializer(tasks_assigned_to_me, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewingTaskView(UserAuthenticationMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks_reviewing = Task.objects.filter(reviewer=request.user)
        serializer = TaskSerializer(tasks_reviewing, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        permission_classes = [IsMemberOfBoard]
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
