import graphene

from apps.organizations.models import OrganizationMember

from .types import OrganizationMemberType, OrganizationType, UserType


class AccountType(graphene.ObjectType):
    user = graphene.Field(UserType, required=True)
    organizations = graphene.List(OrganizationType, required=True)
    memberships = graphene.List(OrganizationMemberType, required=True)


class AccountQuery(graphene.ObjectType):
    account = graphene.Field(AccountType, required=True)

    def resolve_account(self, info):
        user = info.context.user

        memberships = list(
            OrganizationMember.objects.select_related('organization')
            .filter(
                user=user,
                is_active=True,
                organization__is_active=True,
            )
            .order_by('created_at')
        )

        organizations = [m.organization for m in memberships]
        return AccountType(user=user, organizations=organizations, memberships=memberships)
