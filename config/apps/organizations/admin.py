from django.contrib import admin

from .models import Organization, OrganizationMember

# Register your models here.


class OrganizationMemberInline(admin.TabularInline):
    model = OrganizationMember
    extra = 0
    autocomplete_fields = ('user',)
    fields = ('user', 'role', 'is_active', 'permissions')

    def get_queryset(self, request):
        return self.model.all_objects.get_queryset()


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'contact_email', 'is_active', 'deactivated_at', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'contact_email')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [OrganizationMemberInline]

    def get_queryset(self, request):
        return self.model.all_objects.get_queryset()


@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    list_display = ('organization', 'user', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active')
    search_fields = (
        'organization__name',
        'organization__slug',
        'user__email',
    )
    autocomplete_fields = ('organization', 'user')

    def get_queryset(self, request):
        return self.model.all_objects.get_queryset()
