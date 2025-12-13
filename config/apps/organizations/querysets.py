from django.db import models


class OrganizationQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def inactive(self):
        return self.filter(is_active=False)


class OrganizationMemberQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True, organization__is_active=True)
