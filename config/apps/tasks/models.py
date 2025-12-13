from django.conf import settings
from django.db import models

from apps.core.models import SoftDeleteModel
from apps.projects.models import Project

from .managers import TaskCommentManager, TaskManager

# Create your models here.


class Task(SoftDeleteModel):
    class Status(models.TextChoices):
        TODO = 'todo', 'Todo'
        IN_PROGRESS = 'in_progress', 'In progress'
        DONE = 'done', 'Done'

    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name='tasks',
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    assignee_email = models.EmailField(blank=True)

    objects = TaskManager()
    all_objects = TaskManager(alive_only=False, active_org_only=False, active_project_only=False)

    class Meta:
        base_manager_name = 'all_objects'
        default_manager_name = 'objects'
        indexes = [
            models.Index(fields=['project', 'status']),
        ]
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.title


class TaskComment(SoftDeleteModel):
    task = models.ForeignKey(
        Task,
        on_delete=models.PROTECT,
        related_name='comments',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='task_comments',
    )
    content = models.TextField()

    objects = TaskCommentManager()
    all_objects = TaskCommentManager(
        alive_only=False,
        active_org_only=False,
        active_task_only=False,
        active_project_only=False,
    )

    class Meta:
        base_manager_name = 'all_objects'
        default_manager_name = 'objects'
        indexes = [
            models.Index(fields=['task', 'created_at']),
        ]
        ordering = ['created_at']

    def __str__(self) -> str:
        return f'Comment on {self.task_id}'
