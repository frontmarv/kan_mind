from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Board
from tasks.api.serializers import TaskSerializer

User = get_user_model()


class BoardListSerializer(serializers.ModelSerializer):
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
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.ticket.count()

    def get_tasks_to_do_count(self, obj):
        return obj.ticket.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        return obj.ticket.filter(priority='high').count()

    def create(self, validated_data):
        members = validated_data.pop('members', [])
        board = Board.objects.create(**validated_data)
        board.members.set(members)
        return board
