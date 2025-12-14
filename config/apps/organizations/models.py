from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.ids import generate_cuid

from .managers import OrganizationManager, OrganizationMemberManager

# Create your models here.


class Organization(models.Model):
    id = models.CharField(primary_key=True, max_length=24, default=generate_cuid, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    contact_email = models.EmailField()

    is_active = models.BooleanField(default=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OrganizationManager()
    all_objects = OrganizationManager(active_only=False)

    class Meta:
        base_manager_name = 'all_objects'
        default_manager_name = 'objects'
        indexes = [
            models.Index(fields=['is_active']),
        ]

    def deactivate(self, using=None):
        if not self.is_active:
            return
        self.is_active = False
        self.deactivated_at = timezone.now()
        self.save(using=using, update_fields=['is_active', 'deactivated_at'])

    def activate(self, using=None):
        if self.is_active:
            return
        self.is_active = True
        self.deactivated_at = None
        self.save(using=using, update_fields=['is_active', 'deactivated_at'])

    def __str__(self) -> str:
        return self.name


class OrganizationMember(models.Model):
    id = models.CharField(primary_key=True, max_length=24, default=generate_cuid, editable=False)
    class Role(models.TextChoices):
        OWNER = 'owner', 'Owner'
        MANAGER = 'manager', 'Manager'
        MEMBER = 'member', 'Member'

    class Permission(models.TextChoices):
        ORGANIZATION_MANAGE = 'organization:manage', 'Manage organization'
        MEMBERS_MANAGE = 'members:manage', 'Manage members'

        PROJECTS_READ = 'projects:read', 'Read projects'
        PROJECTS_WRITE = 'projects:write', 'Write projects'
        PROJECTS_DELETE = 'projects:delete', 'Delete projects'

        TASKS_READ = 'tasks:read', 'Read tasks'
        TASKS_WRITE = 'tasks:write', 'Write tasks'
        TASKS_DELETE = 'tasks:delete', 'Delete tasks'

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='members',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organization_memberships',
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    permissions = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OrganizationMemberManager()
    all_objects = OrganizationMemberManager(active_only=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'user'],
                name='organizations_member_unique_user_per_org',
            ),
        ]
        indexes = [
            models.Index(fields=['organization', 'role']),
            models.Index(fields=['organization', 'is_active']),
        ]

    @classmethod
    def default_permissions_for_role(cls, role: str):
        all_permissions = frozenset(p.value for p in cls.Permission)
        if role == cls.Role.OWNER:
            return all_permissions
        if role == cls.Role.MANAGER:
            return frozenset(
                {
                    cls.Permission.MEMBERS_MANAGE,
                    cls.Permission.PROJECTS_READ,
                    cls.Permission.PROJECTS_WRITE,
                    cls.Permission.PROJECTS_DELETE,
                    cls.Permission.TASKS_READ,
                    cls.Permission.TASKS_WRITE,
                    cls.Permission.TASKS_DELETE,
                }
            )
        return frozenset(
            {
                cls.Permission.PROJECTS_READ,
                cls.Permission.TASKS_READ,
                cls.Permission.TASKS_WRITE,
            }
        )

    def clean(self):
        super().clean()
        if self.permissions is None:
            return

        if not isinstance(self.permissions, list) or any(not isinstance(p, str) for p in self.permissions):
            raise ValidationError({'permissions': 'Permissions must be a list of strings.'})

        valid_permissions = {p.value for p in self.Permission}
        unknown = set(self.permissions) - valid_permissions
        if unknown:
            raise ValidationError({'permissions': f'Unknown permission codes: {", ".join(sorted(unknown))}'})

    @property
    def effective_permissions(self) -> set[str]:
        role_perms = set(self.default_permissions_for_role(self.role))
        extra_perms = set(self.permissions or [])
        return role_perms | extra_perms

    def can(self, permission: str) -> bool:
        if not self.is_active or not self.organization.is_active:
            return False
        return permission in self.effective_permissions

    def __str__(self) -> str:
        return f'{self.organization} / {self.user}'
