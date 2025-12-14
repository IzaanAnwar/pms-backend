from django.db.models import QuerySet

from apps.organizations.models import Organization

from .models import Task, TaskComment


def list_tasks(*, organization: Organization, project_id: str | None = None) -> QuerySet[Task]:
    qs = Task.objects.select_related('project').filter(project__organization=organization)
    if project_id:
        qs = qs.filter(project_id=project_id)
    return qs.order_by('-created_at')


def get_task(*, organization: Organization, task_id: str) -> Task:
    return Task.objects.select_related('project').get(id=task_id, project__organization=organization)


def list_task_comments(*, organization: Organization, task_id: str) -> QuerySet[TaskComment]:
    return TaskComment.objects.select_related('task', 'author').filter(
        task_id=task_id,
        task__project__organization=organization,
    )


def get_task_comment(*, organization: Organization, comment_id: str) -> TaskComment:
    return TaskComment.objects.select_related('task', 'author').get(
        id=comment_id,
        task__project__organization=organization,
    )
