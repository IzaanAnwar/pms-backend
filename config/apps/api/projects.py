from graphql import GraphQLError
import graphene

from apps.organizations.models import OrganizationMember
from apps.projects.models import Project

from .common import require_org_permission
from .types import ProjectType


class ProjectsQuery(graphene.ObjectType):
    projects = graphene.List(ProjectType, required=True)
    project = graphene.Field(ProjectType, id=graphene.ID(required=True))

    def resolve_projects(self, info):
        org, _membership = require_org_permission(info, OrganizationMember.Permission.PROJECTS_READ)
        return Project.objects.filter(organization=org).order_by('-created_at')

    def resolve_project(self, info, id: str):
        org, _membership = require_org_permission(info, OrganizationMember.Permission.PROJECTS_READ)
        try:
            return Project.objects.get(id=id, organization=org)
        except Project.DoesNotExist as exc:
            raise GraphQLError('Project not found') from exc


class CreateProject(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=False)
        status = graphene.String(required=False)
        due_date = graphene.Date(required=False)

    project = graphene.Field(ProjectType, required=True)

    @classmethod
    def mutate(
        cls,
        root,
        info,
        name: str,
        description: str | None = None,
        status: str | None = None,
        due_date=None,
    ):
        org, membership = require_org_permission(info, OrganizationMember.Permission.PROJECTS_WRITE)

        name_value = name.strip()
        if not name_value:
            raise GraphQLError('Project name is required')

        status_value = status or Project.Status.ACTIVE
        if status_value not in Project.Status.values:
            raise GraphQLError('Invalid project status')

        project = Project.objects.create(
            organization=org,
            name=name_value,
            description=(description or '').strip(),
            status=status_value,
            due_date=due_date,
        )
        return CreateProject(project=project)


class UpdateProject(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String(required=False)
        description = graphene.String(required=False)
        status = graphene.String(required=False)
        due_date = graphene.Date(required=False)

    project = graphene.Field(ProjectType, required=True)

    @classmethod
    def mutate(
        cls,
        root,
        info,
        id: str,
        name: str | None = None,
        description: str | None = None,
        status: str | None = None,
        due_date=None,
    ):
        org, membership = require_org_permission(info, OrganizationMember.Permission.PROJECTS_WRITE)

        try:
            project = Project.objects.get(id=id, organization=org)
        except Project.DoesNotExist as exc:
            raise GraphQLError('Project not found') from exc

        update_fields: list[str] = []

        if name is not None:
            name_value = name.strip()
            if not name_value:
                raise GraphQLError('Project name is required')
            project.name = name_value
            update_fields.append('name')

        if description is not None:
            project.description = description
            update_fields.append('description')

        if status is not None:
            if status not in Project.Status.values:
                raise GraphQLError('Invalid project status')
            project.status = status
            update_fields.append('status')

        if due_date is not None:
            project.due_date = due_date
            update_fields.append('due_date')

        if update_fields:
            project.save(update_fields=update_fields)

        return UpdateProject(project=project)


class DeleteProject(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean(required=True)

    @classmethod
    def mutate(cls, root, info, id: str):
        org, membership = require_org_permission(info, OrganizationMember.Permission.PROJECTS_DELETE)

        try:
            project = Project.objects.get(id=id, organization=org)
        except Project.DoesNotExist as exc:
            raise GraphQLError('Project not found') from exc

        project.delete()
        return DeleteProject(ok=True)


class ProjectsMutation(graphene.ObjectType):
    create_project = CreateProject.Field()
    update_project = UpdateProject.Field()
    delete_project = DeleteProject.Field()
