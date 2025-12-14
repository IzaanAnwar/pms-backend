from django.core.exceptions import ValidationError

from apps.organizations.models import Organization

from .models import Project


def create_project(
    *,
    organization: Organization,
    name: str,
    description: str | None = None,
) -> Project:
    name_value = name.strip()
    if not name_value:
        raise ValidationError('Project name is required')

    return Project.objects.create(
        organization=organization,
        name=name_value,
        description=(description or '').strip(),
    )


def update_project(
    *,
    organization: Organization,
    project_id: str,
    name: str | None = None,
    description: str | None = None,
) -> Project:
    project = Project.objects.get(id=project_id, organization=organization)

    update_fields: list[str] = []

    if name is not None:
        name_value = name.strip()
        if not name_value:
            raise ValidationError('Project name is required')
        project.name = name_value
        update_fields.append('name')

    if description is not None:
        project.description = description
        update_fields.append('description')

    if update_fields:
        project.save(update_fields=update_fields)

    return project


def delete_project(*, organization: Organization, project_id: str) -> None:
    project = Project.objects.get(id=project_id, organization=organization)
    project.delete()
