from django.db import models

from .querysets import OrganizationMemberQuerySet, OrganizationQuerySet


class OrganizationManager(models.Manager):
    def __init__(self, *args, active_only: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.active_only = active_only

    def get_queryset(self):
        qs = OrganizationQuerySet(self.model, using=self._db)
        if self.active_only:
            qs = qs.filter(is_active=True)
        return qs


class OrganizationMemberManager(models.Manager):
    def __init__(self, *args, active_only: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.active_only = active_only

    def get_queryset(self):
        qs = OrganizationMemberQuerySet(self.model, using=self._db)
        if self.active_only:
            qs = qs.filter(is_active=True, organization__is_active=True)
        return qs
