from django.db import models

from apps.core.models import SoftDeleteModel
from apps.organizations.models import Organization

from .managers import ProjectManager

# Create your models here.


class Project(SoftDeleteModel):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name='projects',
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    objects = ProjectManager()
    all_objects = ProjectManager(alive_only=False, active_org_only=False)

    class Meta:
        base_manager_name = 'all_objects'
        default_manager_name = 'objects'
        indexes = [
            models.Index(fields=['organization'], name='projects_project_org_idx'),
        ]

    def __str__(self) -> str:
        return self.name
