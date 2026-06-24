from rest_framework import serializers
from ..models import Task, Comment
from authentication_app.api.serializers import UserProfileSerializer
from authentication_app.models import CustomUser
from rest_framework.exceptions import PermissionDenied
from authentication_app.api.serializers import UserProfileSerializer


class TaskSerializer(serializers.ModelSerializer):
    """
    Custom serializer for task display with nested user profiles.
    Provides read-only user information (assignee, reviewer) as full profiles
    while accepting only user IDs for write operations.
    """
    comments_count = serializers.SerializerMethodField()
    assignee = UserProfileSerializer(read_only=True)
    reviewer = UserProfileSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source='assignee',
        write_only=True,
        required=False,
        allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source='reviewer',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status',
            'priority', 'assignee', 'reviewer', 'due_date',
            'comments_count', 'assignee_id', 'reviewer_id'
        ]
        read_only_fields = ['id']

    def get_comments_count(self, obj):
        return obj.comments.count()


class TaskChangeSerializer(serializers.ModelSerializer):
    """
    Custom serializer for task updates with complex validation and board member checking.
    Overrides validation to ensure assignee and reviewer are members of the task's board.
    Handles conversion between IDs (write) and full user profiles (read).
    """
    assignee_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True)

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status',
            'priority', 'assignee', 'reviewer', 'due_date', 'assignee_id', 'reviewer_id'
        ]
        read_only_fields = ['id', 'board']

    def get_comments_count(self, obj):
        return obj.comments.count()

    def validate_board(self, value):
        """
        Custom board validation to prevent changing a task's board.
        Ensures that if updating an existing task, its board cannot be changed.
        """
        if self.instance and self.instance.board_id != value.id:
            raise serializers.ValidationError(
                "Board cannot be changed.")
        return value

    def validate(self, attrs):
        """
        Custom validation for assignee and reviewer.
        Ensures both assignee and reviewer are members of the board.
        Converts ID-based input to user instances and validates board membership.
        """
        board = self.instance.board if self.instance else attrs.get('board')
        board_members = board.members.all() if board else []
        errors = {}
        assignee_id = attrs.pop('assignee_id', None)
        reviewer_id = attrs.pop('reviewer_id', None)

        if assignee_id is not None:
            try:
                assignee = CustomUser.objects.get(id=assignee_id)
                if assignee not in board_members:
                    errors['assignee'] = "Assigned user must be a member of the board."
                else:
                    attrs['assignee'] = assignee
            except CustomUser.DoesNotExist:
                errors['assignee'] = "User does not exist."
        elif assignee_id is None and 'assignee' not in attrs and not self.instance:
            attrs['assignee'] = None

        if reviewer_id is not None:
            try:
                reviewer = CustomUser.objects.get(id=reviewer_id)
                if reviewer not in board_members:
                    errors['reviewer'] = "Reviewer must be a member of the board."
                else:
                    attrs['reviewer'] = reviewer
            except CustomUser.DoesNotExist:
                errors['reviewer'] = "User does not exist."
        elif reviewer_id is None and 'reviewer' not in attrs and not self.instance:
            attrs['reviewer'] = None

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def to_representation(self, instance):
        """
        Custom representation to serialize assignee and reviewer as full user profiles.
        Converts stored user instances into complete UserProfileSerializer output
        for API responses instead of just returning IDs.
        """
        representation = super().to_representation(instance)

        if instance.assignee:
            representation['assignee'] = UserProfileSerializer(
                instance.assignee).data
        else:
            representation['assignee'] = None

        if instance.reviewer:
            representation['reviewer'] = UserProfileSerializer(
                instance.reviewer).data
        else:
            representation['reviewer'] = None

        return representation


class CommentSerializer(serializers.ModelSerializer):
    """
    Custom serializer for task comments with author name extraction.
    Displays author as their full name string instead of user ID or object,
    providing a cleaner representation in API responses.
    """
    author = serializers.ReadOnlyField(source='author.fullname')

    class Meta:
        ordering = ['-created_at']
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at']
