from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Board
from task_app.api.serializers import TaskSerializer
from authentication_app.api.serializers import UserProfileSerializer
User = get_user_model()


class BoardListSerializer(serializers.ModelSerializer):
    """
    Custom serializer for board list display with calculated metrics.
    Overrides standard serializer to provide additional read-only fields for
    calculating member count, ticket count, and priority/status statistics.
    """
    ticket_count = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False,
        write_only=True
    )

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'tasks_high_prio_count',
            'owner_id',
            'members'
        ]

    def get_member_count(self, obj):
        """
        Calculates the number of board members dynamically.
        Used as a read-only field in the API response.
        """
        return obj.members.count()

    def get_ticket_count(self, obj):
        """
        Calculates the total number of tasks/tickets on the board.
        Used as a read-only field in the API response.
        """
        return obj.ticket.count()

    def get_tasks_to_do_count(self, obj):
        """
        Calculates the number of pending tasks with 'to-do' status.
        Used as a read-only field in the API response.
        """
        return obj.ticket.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        """
        Calculates the number of high-priority tasks.
        Used as a read-only field in the API response.
        """
        return obj.ticket.filter(priority='high').count()

    def create(self, validated_data):
        """
        Custom creation with member assignment after board generation.
        Handles the many-to-many 'members' relation separately:
        1. Creates board without members
        2. Sets members using .set() to update the M2M relation
        Overrides default create() because M2M relations must be saved first
        before they can be assigned to an instance.
        """
        members = validated_data.pop('members', [])
        board = Board.objects.create(**validated_data)
        if members:
            board.members.set(members)
        return board


class BoardSingleViewSerializer(serializers.ModelSerializer):
    """
    Custom serializer for detailed board display with nested data.
    Overrides standard serializer to provide all tasks with full details
    and member profiles in a single response.
    """
    tasks = serializers.SerializerMethodField()
    members = UserProfileSerializer(
        many=True,
    )

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'owner_id',
            'members',
            'tasks'
        ]
    read_only_fields = ['id', 'tasks', 'members', 'owner_id']

    def get_tasks(self, obj):
        """
        Custom serialization of all board tasks with complete details.
        Uses TaskSerializer to serialize all related task information including
        assignee and reviewer. This is a read-only field.
        """
        return TaskSerializer(obj.ticket.all(), many=True).data


class BoardUpdateSerializer(serializers.ModelSerializer):
    """
    Custom serializer for board updates with full user data serialization.
    Overrides standard update to display both PrimaryKeyRelatedField (for writing)
    and complete user profiles (for reading).
    """
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False,
        write_only=True
    )
    members_data = serializers.SerializerMethodField()
    owner_data = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'owner_data',
            'members_data',
            'members'
        ]

    def get_members_data(self, obj):
        """
        Serializes all board members with complete user profiles.
        This is a read-only field used to provide user details (email, fullname)
        instead of just IDs.
        """
        return UserProfileSerializer(obj.members.all(), many=True).data

    def get_owner_data(self, obj):
        """
        Serializes the board owner with complete user profile.
        This is a read-only field used to provide owner details (email, fullname)
        instead of just ID.
        """
        return UserProfileSerializer(obj.owner).data

    def update(self, instance, validated_data):
        """
        Custom Update mit separater M2M-Behandlung.
        Behandelt 'members' (Many-to-Many Relation) separat vom Standard-Update:
        1. Extrahiert members aus validated_data
        2. Führt Standard-Update für reguläre Felder durch
        3. Setzt members nach Board-Aktualisierung mit .set() methode
        Dies ist notwendig da M2M Relationen nur nach Instance-Speicherung
        zugewiesen werden können.
        """
        members = validated_data.pop('members', None)
        instance = super().update(instance, validated_data)
        if members is not None:
            instance.members.set(members)
        return instance
