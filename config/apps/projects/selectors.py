from django.db.models import QuerySet

from apps.organizations.models import Organization

from .models import Project


def list_projects(*, organization: Organization) -> QuerySet[Project]:
    return Project.objects.filter(organization=organization).order_by('-created_at')


def get_project(*, organization: Organization, project_id: str) -> Project:
    return Project.objects.get(id=project_id, organization=organization)
