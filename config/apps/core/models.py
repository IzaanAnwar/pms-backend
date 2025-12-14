from django.db import models
from django.utils import timezone

from .managers import SoftDeleteManager
from .ids import generate_cuid

# Create your models here.


class SoftDeleteModel(models.Model):
    id = models.CharField(primary_key=True, max_length=24, default=generate_cuid, editable=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SoftDeleteManager()
    all_objects = SoftDeleteManager(alive_only=False)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        if self.deleted_at is not None:
            return 0, {self._meta.label: 0}

        self.deleted_at = timezone.now()
        self.save(using=using, update_fields=['deleted_at'])
        return 1, {self._meta.label: 1}

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self, using=None):
        if self.deleted_at is None:
            return
        self.deleted_at = None
        self.save(using=using, update_fields=['deleted_at'])
