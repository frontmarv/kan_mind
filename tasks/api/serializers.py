from rest_framework import serializers
from ..models import Task, Comment
from authentication.api.serializers import UserProfileSerializer
from authentication.models import CustomUser
from rest_framework.exceptions import PermissionDenied
from authentication.api.serializers import UserProfileSerializer


class TaskViewSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField()
    assignee_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True)

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status',
            'priority', 'assignee', 'reviewer', 'due_date', 'comments_count', 'assignee_id', 'reviewer_id'
        ]
        read_only_fields = ['id', 'board']

    def get_comments_count(self, obj):
        return obj.comments.count()


class TaskChangeSerializer(serializers.ModelSerializer):
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
        if self.instance and self.instance.board_id != value.id:
            raise serializers.ValidationError(
                "Das Ändern des Boards ist nicht erlaubt.")
        return value

    def validate(self, attrs):
        board = self.instance.board if self.instance else attrs.get('board')
        board_members = board.members.all() if board else []
        errors = {}
        assignee_id = attrs.pop('assignee_id', None)
        reviewer_id = attrs.pop('reviewer_id', None)

        # Assignee validieren
        if assignee_id is not None:
            try:
                assignee = CustomUser.objects.get(id=assignee_id)
                if assignee not in board_members:
                    errors['assignee'] = "Zugewiesener Benutzer muss Mitglied des Boards sein."
                else:
                    attrs['assignee'] = assignee
            except CustomUser.DoesNotExist:
                errors['assignee'] = "Benutzer existiert nicht."
        elif assignee_id is None and 'assignee' not in attrs and not self.instance:
            attrs['assignee'] = None

        # Reviewer validieren
        if reviewer_id is not None:
            try:
                reviewer = CustomUser.objects.get(id=reviewer_id)
                if reviewer not in board_members:
                    errors['reviewer'] = "Reviewer muss Mitglied des Boards sein."
                else:
                    attrs['reviewer'] = reviewer
            except CustomUser.DoesNotExist:
                errors['reviewer'] = "Benutzer existiert nicht."
        elif reviewer_id is None and 'reviewer' not in attrs and not self.instance:
            attrs['reviewer'] = None

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def to_representation(self, instance):
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
    author = serializers.ReadOnlyField(source='author.fullname')

    class Meta:
        ordering = ['-created_at']
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at']
