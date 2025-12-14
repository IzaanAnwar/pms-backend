import graphene

from .mutations import Login, Onboard, Signup
from .comments import CommentsMutation, CommentsQuery
from .projects import ProjectsMutation, ProjectsQuery
from .tasks import TasksMutation, TasksQuery
from .types import OrganizationType, UserType


class Query(ProjectsQuery, TasksQuery, CommentsQuery, graphene.ObjectType):
    me = graphene.Field(UserType, required=True)
    active_organization = graphene.Field(OrganizationType)

    def resolve_me(self, info):
        return info.context.user

    def resolve_active_organization(self, info):
        return getattr(info.context, 'active_organization', None)


class Mutation(ProjectsMutation, TasksMutation, CommentsMutation, graphene.ObjectType):
    signup = Signup.Field()
    login = Login.Field()
    onboard = Onboard.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
