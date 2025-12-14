from django.core.exceptions import ValidationError
from graphql import GraphQLError
import graphene

from apps.organizations.models import OrganizationMember
from apps.projects import selectors as project_selectors
from apps.projects import services as project_services
from apps.projects.models import Project

from .common import require_org_permission
from .types import ProjectType


class ProjectsQuery(graphene.ObjectType):
    projects = graphene.List(ProjectType, required=True)
    project = graphene.Field(ProjectType, id=graphene.ID(required=True))

    def resolve_projects(self, info):
        org, _membership = require_org_permission(info, OrganizationMember.Permission.PROJECTS_READ)
        return project_selectors.list_projects(organization=org)

    def resolve_project(self, info, id: str):
        org, _membership = require_org_permission(info, OrganizationMember.Permission.PROJECTS_READ)
        try:
            return project_selectors.get_project(organization=org, project_id=id)
        except Project.DoesNotExist as exc:
            raise GraphQLError('Project not found') from exc


class CreateProject(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=False)

    project = graphene.Field(ProjectType, required=True)

    @classmethod
    def mutate(
        cls,
        root,
        info,
        name: str,
        description: str | None = None,
    ):
        org, _membership = require_org_permission(info, OrganizationMember.Permission.PROJECTS_WRITE)
        try:
            project = project_services.create_project(
                organization=org,
                name=name,
                description=description,
            )
        except ValidationError as exc:
            raise GraphQLError(' '.join(exc.messages)) from exc
        return CreateProject(project=project)


class UpdateProject(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String(required=False)
        description = graphene.String(required=False)

    project = graphene.Field(ProjectType, required=True)

    @classmethod
    def mutate(
        cls,
        root,
        info,
        id: str,
        name: str | None = None,
        description: str | None = None,
    ):
        try:
            org, _membership = require_org_permission(info, OrganizationMember.Permission.PROJECTS_WRITE)
            project = project_services.update_project(
                organization=org,
                project_id=id,
                name=name,
                description=description,
            )
        except Project.DoesNotExist as exc:
            raise GraphQLError('Project not found') from exc

        except ValidationError as exc:
            raise GraphQLError(' '.join(exc.messages)) from exc

        return UpdateProject(project=project)


class DeleteProject(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean(required=True)

    @classmethod
    def mutate(cls, root, info, id: str):
        try:
            org, _membership = require_org_permission(info, OrganizationMember.Permission.PROJECTS_DELETE)
            project_services.delete_project(organization=org, project_id=id)
        except Project.DoesNotExist as exc:
            raise GraphQLError('Project not found') from exc
        return DeleteProject(ok=True)


class ProjectsMutation(graphene.ObjectType):
    create_project = CreateProject.Field()
    update_project = UpdateProject.Field()
    delete_project = DeleteProject.Field()
