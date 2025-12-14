from django.contrib import admin

from .models import Project

# Register your models here.


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'deleted_at', 'created_at')
    list_filter = ('organization',)
    search_fields = ('name', 'description', 'organization__name', 'organization__slug')
    autocomplete_fields = ('organization',)
    ordering = ('-created_at',)
    readonly_fields = ('deleted_at', 'created_at', 'updated_at')

    def get_queryset(self, request):
        return self.model.all_objects.get_queryset()
