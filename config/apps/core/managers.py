from django.db import models

from .querysets import SoftDeleteQuerySet


class SoftDeleteManager(models.Manager):
    def __init__(self, *args, alive_only: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.alive_only = alive_only

    def get_queryset(self):
        qs = SoftDeleteQuerySet(self.model, using=self._db)
        if self.alive_only:
            qs = qs.filter(deleted_at__isnull=True)
        return qs
