from django.core.exceptions import PermissionDenied
from graphql import GraphQLError

from apps.organizations.selectors import require_permission as require_permission_selector


def get_active_organization(info):
    organization = getattr(info.context, 'active_organization', None)
    if organization is None:
        raise GraphQLError('X-Organization-ID header required')
    return organization


def get_membership(info):
    membership = getattr(info.context, 'membership', None)
    if membership is None:
        raise GraphQLError('Invalid organization')
    return membership


def require_permission(*, membership, permission: str) -> None:
    try:
        require_permission_selector(membership=membership, permission=permission)
    except PermissionDenied as exc:
        raise GraphQLError(str(exc)) from exc


def require_org_permission(info, permission: str):
    membership = get_membership(info)
    require_permission(membership=membership, permission=permission)
    organization = get_active_organization(info)
    return organization, membership
