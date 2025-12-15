from graphql import GraphQLError


class AuthRequiredMiddleware:
    def resolve(self, next, root, info, **args):
        root_field = _get_root_field_name(info.path)
        if root_field.startswith('__'):
            return next(root, info, **args)

        if root_field in {'signup', 'login'}:
            return next(root, info, **args)

        request = info.context

        if getattr(request, 'auth_error', None):
            raise GraphQLError('Invalid token')

        if getattr(request, 'jwt_payload', None) is None:
            raise GraphQLError('Authentication required')

        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            raise GraphQLError('Authentication required')

        if root_field not in {'onboard', 'me', 'account'}:
            if getattr(request, 'org_error', None):
                raise GraphQLError('Invalid organization')

            if getattr(request, 'active_organization', None) is None:
                raise GraphQLError('X-Organization-ID header required')

        return next(root, info, **args)


def _get_root_field_name(path) -> str:
    while getattr(path, 'prev', None) is not None:
        path = path.prev
    return str(getattr(path, 'key', ''))
