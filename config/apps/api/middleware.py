from django.contrib.auth.models import AnonymousUser

from apps.accounts.models import User
from apps.organizations.models import OrganizationMember

from .jwt import decode_access_token


class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.jwt_payload = None
        request.auth_error = None

        request.org_error = None

        request.membership = None
        request.active_organization = None

        token = _get_bearer_token(request)
        if not token:
            return self.get_response(request)

        try:
            payload = decode_access_token(token=token)
            user = User.objects.get(pk=payload.get('sub'), is_active=True)
        except Exception:
            request.user = AnonymousUser()
            request.auth_error = 'invalid_token'
            return self.get_response(request)

        request.user = user
        request.jwt_payload = payload

        org_id = request.META.get('HTTP_X_ORGANIZATION_ID') or request.headers.get('X-Organization-ID')
        if org_id:
            org_id = str(org_id).strip()
            try:
                membership = OrganizationMember.objects.select_related('organization').get(
                    user=user,
                    organization_id=org_id,
                )
                request.membership = membership
                request.active_organization = membership.organization
            except Exception:
                request.membership = None
                request.active_organization = None
                request.org_error = 'invalid_organization'

        return self.get_response(request)


def _get_bearer_token(request) -> str | None:
    auth_header = request.META.get('HTTP_AUTHORIZATION', '').strip()
    if not auth_header:
        return None

    parts = auth_header.split(' ', 1)
    if len(parts) != 2:
        return None

    scheme, token = parts[0].strip(), parts[1].strip()
    if scheme.lower() != 'bearer' or not token:
        return None

    return token
