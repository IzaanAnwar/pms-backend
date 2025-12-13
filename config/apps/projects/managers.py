from apps.core.managers import SoftDeleteManager


class ProjectManager(SoftDeleteManager):
    def __init__(
        self,
        *args,
        alive_only: bool = True,
        active_org_only: bool = True,
        **kwargs,
    ):
        super().__init__(*args, alive_only=alive_only, **kwargs)
        self.active_org_only = active_org_only

    def get_queryset(self):
        qs = super().get_queryset()
        if self.active_org_only:
            qs = qs.filter(organization__is_active=True)
        return qs
