from rest_framework import serializers
from ..models import Task
from authentication.api.serializers import UserProfileSerializer


class TaskSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField()
    assignee = serializers.SerializerMethodField()
    reviewer = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status',
                  'priority', 'assignee', 'reviewer', 'due_date', 'comments_count']

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_assignee(self, obj):
        return UserProfileSerializer(obj.assignee).data

    def get_reviewer(self, obj):
        return UserProfileSerializer(obj.reviewer).data
