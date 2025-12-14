from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils.text import slugify
from graphql import GraphQLError
import graphene

from apps.accounts.models import User
from apps.organizations.models import Organization, OrganizationMember

from .jwt import create_access_token
from .types import OrganizationMemberType, OrganizationType, UserType


class Signup(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        first_name = graphene.String(required=False)
        last_name = graphene.String(required=False)

    token = graphene.String(required=True)
    user = graphene.Field(UserType, required=True)

    @classmethod
    def mutate(cls, root, info, email: str, password: str, first_name: str | None = None, last_name: str | None = None):
        try:
            validate_password(password)
        except ValidationError as exc:
            raise GraphQLError(' '.join(exc.messages)) from exc

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    first_name=first_name or '',
                    last_name=last_name or '',
                )
        except IntegrityError as exc:
            raise GraphQLError('Email already in use') from exc

        token = create_access_token(user=user)
        return Signup(token=token, user=user)


class Login(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    token = graphene.String(required=True)
    user = graphene.Field(UserType, required=True)

    @classmethod
    def mutate(cls, root, info, email: str, password: str):
        user = authenticate(email=email, password=password)
        if user is None:
            raise GraphQLError('Invalid credentials')
        if not user.is_active:
            raise GraphQLError('User is inactive')

        token = create_access_token(user=user)
        return Login(token=token, user=user)


class Onboard(graphene.Mutation):
    class Arguments:
        organization_name = graphene.String(required=True)
        organization_slug = graphene.String(required=False)
        contact_email = graphene.String(required=False)

    organization = graphene.Field(OrganizationType, required=True)
    membership = graphene.Field(OrganizationMemberType, required=True)

    @classmethod
    def mutate(
        cls,
        root,
        info,
        organization_name: str,
        organization_slug: str | None = None,
        contact_email: str | None = None,
    ):
        user = info.context.user

        slug_value = slugify(organization_slug or organization_name)
        if not slug_value:
            raise GraphQLError('Invalid organization name/slug')

        contact_email_value = (contact_email or user.email).strip()

        try:
            with transaction.atomic():
                organization = Organization.objects.create(
                    name=organization_name.strip(),
                    slug=slug_value,
                    contact_email=contact_email_value,
                )
                membership = OrganizationMember.objects.create(
                    organization=organization,
                    user=user,
                    role=OrganizationMember.Role.OWNER,
                )
        except IntegrityError as exc:
            raise GraphQLError('Organization slug already in use') from exc

        return Onboard(organization=organization, membership=membership)
