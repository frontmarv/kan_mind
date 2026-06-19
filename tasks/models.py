from django.db import models
from django.conf import settings
from boards.models import Board  # Wir importieren das Board Model


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = 'to-do'
        IN_PROGRESS = 'in-progress'
        REVIEW = 'review'
        DONE = 'done'

    class Priority(models.TextChoices):
        LOW = 'low'
        MEDIUM = 'medium'
        HIGH = 'high'

    board = models.ForeignKey(
        Board, on_delete=models.CASCADE, related_name='ticket')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='assigned_user', blank=True, null=True, on_delete=models.SET_NULL)
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='assigned_revier', blank=True, null=True, on_delete=models.SET_NULL)
    due_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.fullname} on {self.task.title}"
