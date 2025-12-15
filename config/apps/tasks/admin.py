from django.contrib import admin

from .models import Task, TaskComment

# Register your models here.


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 0
    autocomplete_fields = ('author',)
    fields = ('author', 'content', 'deleted_at', 'created_at')
    readonly_fields = ('deleted_at', 'created_at')

    def get_queryset(self, request):
        return self.model.all_objects.get_queryset()


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status', 'due_date', 'assignee_email', 'deleted_at', 'created_at')
    list_filter = ('status', 'due_date')
    search_fields = (
        'title',
        'description',
        'assignee_email',
        'project__name',
        'project__organization__name',
    )
    autocomplete_fields = ('project',)
    ordering = ('-created_at',)
    readonly_fields = ('deleted_at', 'created_at', 'updated_at')
    inlines = [TaskCommentInline]

    def get_queryset(self, request):
        return self.model.all_objects.get_queryset()


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'deleted_at', 'created_at')
    list_filter = ('deleted_at',)
    search_fields = ('content', 'author__email', 'task__title')
    autocomplete_fields = ('task', 'author')
    ordering = ('-created_at',)
    readonly_fields = ('deleted_at', 'created_at', 'updated_at')

    def get_queryset(self, request):
        return self.model.all_objects.get_queryset()
