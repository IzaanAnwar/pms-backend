from graphql import GraphQLError
import graphene

from apps.organizations.models import OrganizationMember
from apps.projects.models import Project
from apps.tasks.models import Task

from .common import get_active_organization, require_org_permission
from .types import TaskType


class TasksQuery(graphene.ObjectType):
    tasks = graphene.List(TaskType, project_id=graphene.ID(required=False), required=True)
    task = graphene.Field(TaskType, id=graphene.ID(required=True))

    def resolve_tasks(self, info, project_id: str | None = None):
        org, membership = require_org_permission(info, OrganizationMember.Permission.TASKS_READ)

        qs = Task.objects.select_related('project').filter(project__organization=org)
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs.order_by('-created_at')

    def resolve_task(self, info, id: str):
        org, membership = require_org_permission(info, OrganizationMember.Permission.TASKS_READ)
        try:
            return Task.objects.select_related('project').get(id=id, project__organization=org)
        except Task.DoesNotExist as exc:
            raise GraphQLError('Task not found') from exc


class CreateTask(graphene.Mutation):
    class Arguments:
        project_id = graphene.ID(required=True)
        title = graphene.String(required=True)
        description = graphene.String(required=False)
        status = graphene.String(required=False)
        assignee_email = graphene.String(required=False)

    task = graphene.Field(TaskType, required=True)

    @classmethod
    def mutate(
        cls,
        root,
        info,
        project_id: str,
        title: str,
        description: str | None = None,
        status: str | None = None,
        assignee_email: str | None = None,
    ):
        org, membership = require_org_permission(info, OrganizationMember.Permission.TASKS_WRITE)

        title_value = title.strip()
        if not title_value:
            raise GraphQLError('Task title is required')

        try:
            project = Project.objects.get(id=project_id, organization=org)
        except Project.DoesNotExist as exc:
            raise GraphQLError('Project not found') from exc

        status_value = status or Task.Status.TODO
        if status_value not in Task.Status.values:
            raise GraphQLError('Invalid task status')

        task = Task.objects.create(
            project=project,
            title=title_value,
            description=(description or '').strip(),
            status=status_value,
            assignee_email=(assignee_email or '').strip(),
        )
        return CreateTask(task=task)


class UpdateTask(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        project_id = graphene.ID(required=False)
        title = graphene.String(required=False)
        description = graphene.String(required=False)
        status = graphene.String(required=False)
        assignee_email = graphene.String(required=False)

    task = graphene.Field(TaskType, required=True)

    @classmethod
    def mutate(
        cls,
        root,
        info,
        id: str,
        project_id: str | None = None,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
        assignee_email: str | None = None,
    ):
        org, membership = require_org_permission(info, OrganizationMember.Permission.TASKS_WRITE)

        try:
            task = Task.objects.select_related('project').get(id=id, project__organization=org)
        except Task.DoesNotExist as exc:
            raise GraphQLError('Task not found') from exc

        update_fields: list[str] = []

        if project_id is not None:
            try:
                project = Project.objects.get(id=project_id, organization=org)
            except Project.DoesNotExist as exc:
                raise GraphQLError('Project not found') from exc
            task.project = project
            update_fields.append('project')

        if title is not None:
            title_value = title.strip()
            if not title_value:
                raise GraphQLError('Task title is required')
            task.title = title_value
            update_fields.append('title')

        if description is not None:
            task.description = description
            update_fields.append('description')

        if status is not None:
            if status not in Task.Status.values:
                raise GraphQLError('Invalid task status')
            task.status = status
            update_fields.append('status')

        if assignee_email is not None:
            task.assignee_email = assignee_email
            update_fields.append('assignee_email')

        if update_fields:
            task.save(update_fields=update_fields)

        return UpdateTask(task=task)


class DeleteTask(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean(required=True)

    @classmethod
    def mutate(cls, root, info, id: str):
        org, membership = require_org_permission(info, OrganizationMember.Permission.TASKS_DELETE)

        try:
            task = Task.objects.get(id=id, project__organization=org)
        except Task.DoesNotExist as exc:
            raise GraphQLError('Task not found') from exc

        task.delete()
        return DeleteTask(ok=True)


class TasksMutation(graphene.ObjectType):
    create_task = CreateTask.Field()
    update_task = UpdateTask.Field()
    delete_task = DeleteTask.Field()
