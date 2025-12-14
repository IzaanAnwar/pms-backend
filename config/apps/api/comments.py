from graphql import GraphQLError
import graphene

from apps.organizations.models import OrganizationMember
from apps.tasks.models import Task, TaskComment

from .common import require_org_permission
from .types import TaskCommentType


class CommentsQuery(graphene.ObjectType):
    task_comments = graphene.List(TaskCommentType, task_id=graphene.ID(required=True), required=True)
    task_comment = graphene.Field(TaskCommentType, id=graphene.ID(required=True))

    def resolve_task_comments(self, info, task_id: str):
        org, membership = require_org_permission(info, OrganizationMember.Permission.TASKS_READ)
        return TaskComment.objects.select_related('task', 'author').filter(
            task_id=task_id,
            task__project__organization=org,
        )

    def resolve_task_comment(self, info, id: str):
        org, membership = require_org_permission(info, OrganizationMember.Permission.TASKS_READ)
        try:
            return TaskComment.objects.select_related('task', 'author').get(
                id=id,
                task__project__organization=org,
            )
        except TaskComment.DoesNotExist as exc:
            raise GraphQLError('Comment not found') from exc


class CreateTaskComment(graphene.Mutation):
    class Arguments:
        task_id = graphene.ID(required=True)
        content = graphene.String(required=True)

    comment = graphene.Field(TaskCommentType, required=True)

    @classmethod
    def mutate(cls, root, info, task_id: str, content: str):
        org, membership = require_org_permission(info, OrganizationMember.Permission.TASKS_WRITE)

        content_value = content.strip()
        if not content_value:
            raise GraphQLError('Comment content is required')

        try:
            task = Task.objects.select_related('project').get(id=task_id, project__organization=org)
        except Task.DoesNotExist as exc:
            raise GraphQLError('Task not found') from exc

        comment = TaskComment.objects.create(
            task=task,
            author=info.context.user,
            content=content_value,
        )
        return CreateTaskComment(comment=comment)


class UpdateTaskComment(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        content = graphene.String(required=True)

    comment = graphene.Field(TaskCommentType, required=True)

    @classmethod
    def mutate(cls, root, info, id: str, content: str):
        org, membership = require_org_permission(info, OrganizationMember.Permission.TASKS_WRITE)

        content_value = content.strip()
        if not content_value:
            raise GraphQLError('Comment content is required')

        try:
            comment = TaskComment.objects.select_related('task', 'author').get(
                id=id,
                task__project__organization=org,
            )
        except TaskComment.DoesNotExist as exc:
            raise GraphQLError('Comment not found') from exc

        comment.content = content_value
        comment.save(update_fields=['content'])
        return UpdateTaskComment(comment=comment)


class DeleteTaskComment(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean(required=True)

    @classmethod
    def mutate(cls, root, info, id: str):
        org, membership = require_org_permission(info, OrganizationMember.Permission.TASKS_WRITE)

        try:
            comment = TaskComment.objects.get(id=id, task__project__organization=org)
        except TaskComment.DoesNotExist as exc:
            raise GraphQLError('Comment not found') from exc

        comment.delete()
        return DeleteTaskComment(ok=True)


class CommentsMutation(graphene.ObjectType):
    create_task_comment = CreateTaskComment.Field()
    update_task_comment = UpdateTaskComment.Field()
    delete_task_comment = DeleteTaskComment.Field()
