from authentication.permissions import IsAdministrator
from django.contrib import admin
from django.contrib.admin import AdminSite, ModelAdmin, sites


class AdminPermissionCheckMixin:
    def has_permission(self, request):
        return IsAdministrator().has_permission(request, None)


class CustomAdminSite(AdminPermissionCheckMixin, AdminSite):
    pass


class CustomModelAdmin(AdminPermissionCheckMixin, ModelAdmin):
    def _has_permission_wrapper(self, request, obj=None):
        return self.has_permission(request)

    has_module_permission = _has_permission_wrapper
    has_add_permission = _has_permission_wrapper
    has_change_permission = _has_permission_wrapper
    has_delete_permission = _has_permission_wrapper
    has_view_permission = _has_permission_wrapper

    # by default logger LogEntry.objects.log_action will create
    # its objects through the user model from the request,
    # so before overriding this mechanism I disable logging
    def log_addition(self, request, obj, message):
        pass

    def log_change(self, request, obj, message):
        pass

    def log_deletion(self, request, obj, message):
        pass


custom_admin_site = CustomAdminSite()
admin.site = custom_admin_site
sites.site = custom_admin_site
