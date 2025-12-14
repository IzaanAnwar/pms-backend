from django.core.exceptions import ValidationError
from graphql import GraphQLError
import graphene

from apps.organizations.models import OrganizationMember
from apps.tasks import selectors as task_selectors
from apps.tasks import services as task_services
from apps.tasks.models import Task, TaskComment

from .common import require_org_permission
from .types import TaskCommentType


class CommentsQuery(graphene.ObjectType):
    task_comments = graphene.List(TaskCommentType, task_id=graphene.ID(required=True), required=True)
    task_comment = graphene.Field(TaskCommentType, id=graphene.ID(required=True))

    def resolve_task_comments(self, info, task_id: str):
        org, _membership = require_org_permission(info, OrganizationMember.Permission.TASKS_READ)
        return task_selectors.list_task_comments(organization=org, task_id=task_id)

    def resolve_task_comment(self, info, id: str):
        try:
            org, _membership = require_org_permission(info, OrganizationMember.Permission.TASKS_READ)
            return task_selectors.get_task_comment(organization=org, comment_id=id)
        except TaskComment.DoesNotExist as exc:
            raise GraphQLError('Comment not found') from exc


class CreateTaskComment(graphene.Mutation):
    class Arguments:
        task_id = graphene.ID(required=True)
        content = graphene.String(required=True)

    comment = graphene.Field(TaskCommentType, required=True)

    @classmethod
    def mutate(cls, root, info, task_id: str, content: str):
        try:
            org, _membership = require_org_permission(info, OrganizationMember.Permission.TASKS_WRITE)
            comment = task_services.create_task_comment(
                organization=org,
                task_id=task_id,
                author=info.context.user,
                content=content,
            )
        except Task.DoesNotExist as exc:
            raise GraphQLError('Task not found') from exc

        except ValidationError as exc:
            raise GraphQLError(' '.join(exc.messages)) from exc

        return CreateTaskComment(comment=comment)


class UpdateTaskComment(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        content = graphene.String(required=True)

    comment = graphene.Field(TaskCommentType, required=True)

    @classmethod
    def mutate(cls, root, info, id: str, content: str):
        try:
            org, _membership = require_org_permission(info, OrganizationMember.Permission.TASKS_WRITE)
            comment = task_services.update_task_comment(
                organization=org,
                comment_id=id,
                content=content,
            )
        except TaskComment.DoesNotExist as exc:
            raise GraphQLError('Comment not found') from exc

        except ValidationError as exc:
            raise GraphQLError(' '.join(exc.messages)) from exc

        return UpdateTaskComment(comment=comment)


class DeleteTaskComment(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean(required=True)

    @classmethod
    def mutate(cls, root, info, id: str):
        try:
            org, _membership = require_org_permission(info, OrganizationMember.Permission.TASKS_WRITE)
            task_services.delete_task_comment(organization=org, comment_id=id)
        except TaskComment.DoesNotExist as exc:
            raise GraphQLError('Comment not found') from exc
        return DeleteTaskComment(ok=True)


class CommentsMutation(graphene.ObjectType):
    create_task_comment = CreateTaskComment.Field()
    update_task_comment = UpdateTaskComment.Field()
    delete_task_comment = DeleteTaskComment.Field()
