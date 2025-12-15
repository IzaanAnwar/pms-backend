from django.core.exceptions import ValidationError

from apps.organizations.models import Organization
from apps.projects.models import Project

from .models import Task, TaskComment


UNSET = object()


def create_task(
    *,
    organization: Organization,
    project_id: str,
    title: str,
    description: str | None = None,
    status: str | None = None,
    due_date=None,
    assignee_email: str | None = None,
) -> Task:
    title_value = title.strip()
    if not title_value:
        raise ValidationError('Task title is required')

    project = Project.objects.get(id=project_id, organization=organization)

    status_value = status or Task.Status.TODO
    if status_value not in Task.Status.values:
        raise ValidationError('Invalid task status')

    return Task.objects.create(
        project=project,
        title=title_value,
        description=(description or '').strip(),
        status=status_value,
        due_date=due_date,
        assignee_email=(assignee_email or '').strip(),
    )


def update_task(
    *,
    organization: Organization,
    task_id: str,
    project_id: str | None = None,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
    due_date=UNSET,
    assignee_email: str | None = None,
) -> Task:
    task = Task.objects.select_related('project').get(id=task_id, project__organization=organization)

    update_fields: list[str] = []

    if project_id is not None:
        project = Project.objects.get(id=project_id, organization=organization)
        task.project = project
        update_fields.append('project')

    if title is not None:
        title_value = title.strip()
        if not title_value:
            raise ValidationError('Task title is required')
        task.title = title_value
        update_fields.append('title')

    if description is not None:
        task.description = description
        update_fields.append('description')

    if status is not None:
        if status not in Task.Status.values:
            raise ValidationError('Invalid task status')
        task.status = status
        update_fields.append('status')

    if due_date is not UNSET:
        task.due_date = due_date
        update_fields.append('due_date')

    if assignee_email is not None:
        task.assignee_email = assignee_email
        update_fields.append('assignee_email')

    if update_fields:
        task.save(update_fields=update_fields)

    return task


def delete_task(*, organization: Organization, task_id: str) -> None:
    task = Task.objects.get(id=task_id, project__organization=organization)
    task.delete()


def create_task_comment(*, organization: Organization, task_id: str, author, content: str) -> TaskComment:
    content_value = content.strip()
    if not content_value:
        raise ValidationError('Comment content is required')

    task = Task.objects.select_related('project').get(id=task_id, project__organization=organization)

    return TaskComment.objects.create(
        task=task,
        author=author,
        content=content_value,
    )


def update_task_comment(*, organization: Organization, comment_id: str, content: str) -> TaskComment:
    content_value = content.strip()
    if not content_value:
        raise ValidationError('Comment content is required')

    comment = TaskComment.objects.select_related('task', 'author').get(
        id=comment_id,
        task__project__organization=organization,
    )

    comment.content = content_value
    comment.save(update_fields=['content'])
    return comment


def delete_task_comment(*, organization: Organization, comment_id: str) -> None:
    comment = TaskComment.objects.get(id=comment_id, task__project__organization=organization)
    comment.delete()
