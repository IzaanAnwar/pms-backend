from graphene_django import DjangoObjectType

from apps.accounts.models import User
from apps.organizations.models import Organization, OrganizationMember
from apps.projects.models import Project
from apps.tasks.models import Task, TaskComment


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')


class OrganizationType(DjangoObjectType):
    class Meta:
        model = Organization
        fields = ('id', 'name', 'slug', 'contact_email', 'is_active')


class OrganizationMemberType(DjangoObjectType):
    class Meta:
        model = OrganizationMember
        fields = ('id', 'role', 'permissions', 'is_active', 'organization', 'user')


class ProjectType(DjangoObjectType):
    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'status', 'due_date', 'created_at', 'updated_at')


class TaskType(DjangoObjectType):
    class Meta:
        model = Task
        fields = ('id', 'project', 'title', 'description', 'status', 'assignee_email', 'created_at', 'updated_at')


class TaskCommentType(DjangoObjectType):
    class Meta:
        model = TaskComment
        fields = ('id', 'task', 'author', 'content', 'created_at', 'updated_at')
