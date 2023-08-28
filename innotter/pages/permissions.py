from authentication.service import AuthService
from django.utils import timezone
from rest_framework import permissions

auth_service = AuthService()


class IsPageOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner_uuid == auth_service.get_user_id(request)


class PageIsNotBlocked(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        today = timezone.now().date()
        return obj.unblock_date is None or obj.unblock_date.date() <= today
