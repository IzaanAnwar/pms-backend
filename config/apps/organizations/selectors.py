from django.core.exceptions import PermissionDenied

from .models import Organization, OrganizationMember


def get_active_organization_by_slug(*, slug: str) -> Organization:
    try:
        return Organization.objects.get(slug=slug)
    except Organization.DoesNotExist as exc:
        raise PermissionDenied('Organization not found or inactive') from exc


def get_active_membership(*, user, organization: Organization) -> OrganizationMember:
    try:
        return OrganizationMember.objects.select_related('organization').get(user=user, organization=organization)
    except OrganizationMember.DoesNotExist as exc:
        raise PermissionDenied('You do not have access to this organization') from exc


def require_permission(*, membership: OrganizationMember, permission: str) -> None:
    if not membership.can(permission):
        raise PermissionDenied('Permission denied')
