from django.core.exceptions import ValidationError
from graphql import GraphQLError
import graphene

from apps.organizations.models import OrganizationMember
from apps.projects.models import Project
from apps.tasks import selectors as task_selectors
from apps.tasks import services as task_services
from apps.tasks.models import Task

from .common import require_org_permission
from .types import TaskType


class TasksQuery(graphene.ObjectType):
    tasks = graphene.List(TaskType, project_id=graphene.ID(required=False), required=True)
    task = graphene.Field(TaskType, id=graphene.ID(required=True))

    def resolve_tasks(self, info, project_id: str | None = None):
        org, _membership = require_org_permission(info, OrganizationMember.Permission.TASKS_READ)
        return task_selectors.list_tasks(organization=org, project_id=project_id)

    def resolve_task(self, info, id: str):
        org, _membership = require_org_permission(info, OrganizationMember.Permission.TASKS_READ)
        try:
            return task_selectors.get_task(organization=org, task_id=id)
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
        try:
            org, _membership = require_org_permission(info, OrganizationMember.Permission.TASKS_WRITE)
            task = task_services.create_task(
                organization=org,
                project_id=project_id,
                title=title,
                description=description,
                status=status,
                assignee_email=assignee_email,
            )
        except Project.DoesNotExist as exc:
            raise GraphQLError('Project not found') from exc

        except ValidationError as exc:
            raise GraphQLError(' '.join(exc.messages)) from exc

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
        try:
            org, _membership = require_org_permission(info, OrganizationMember.Permission.TASKS_WRITE)
            task = task_services.update_task(
                organization=org,
                task_id=id,
                project_id=project_id,
                title=title,
                description=description,
                status=status,
                assignee_email=assignee_email,
            )
        except Task.DoesNotExist as exc:
            raise GraphQLError('Task not found') from exc

        except Project.DoesNotExist as exc:
            raise GraphQLError('Project not found') from exc

        except ValidationError as exc:
            raise GraphQLError(' '.join(exc.messages)) from exc

        return UpdateTask(task=task)


class DeleteTask(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean(required=True)

    @classmethod
    def mutate(cls, root, info, id: str):
        try:
            org, _membership = require_org_permission(info, OrganizationMember.Permission.TASKS_DELETE)
            task_services.delete_task(organization=org, task_id=id)
        except Task.DoesNotExist as exc:
            raise GraphQLError('Task not found') from exc
        return DeleteTask(ok=True)


class TasksMutation(graphene.ObjectType):
    create_task = CreateTask.Field()
    update_task = UpdateTask.Field()
    delete_task = DeleteTask.Field()
