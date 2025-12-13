from apps.core.managers import SoftDeleteManager


class TaskManager(SoftDeleteManager):
    def __init__(
        self,
        *args,
        alive_only: bool = True,
        active_org_only: bool = True,
        active_project_only: bool = True,
        **kwargs,
    ):
        super().__init__(*args, alive_only=alive_only, **kwargs)
        self.active_org_only = active_org_only
        self.active_project_only = active_project_only

    def get_queryset(self):
        qs = super().get_queryset()
        if self.active_project_only:
            qs = qs.filter(project__deleted_at__isnull=True)
        if self.active_org_only:
            qs = qs.filter(project__organization__is_active=True)
        return qs


class TaskCommentManager(SoftDeleteManager):
    def __init__(
        self,
        *args,
        alive_only: bool = True,
        active_org_only: bool = True,
        active_task_only: bool = True,
        active_project_only: bool = True,
        **kwargs,
    ):
        super().__init__(*args, alive_only=alive_only, **kwargs)
        self.active_org_only = active_org_only
        self.active_task_only = active_task_only
        self.active_project_only = active_project_only

    def get_queryset(self):
        qs = super().get_queryset()
        if self.active_task_only:
            qs = qs.filter(task__deleted_at__isnull=True)
        if self.active_project_only:
            qs = qs.filter(task__project__deleted_at__isnull=True)
        if self.active_org_only:
            qs = qs.filter(task__project__organization__is_active=True)
        return qs
