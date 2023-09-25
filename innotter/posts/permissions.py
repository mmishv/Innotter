from authentication.service import AuthService
from pages.models import Page
from rest_framework import permissions

auth_service = AuthService()


def get_page_from_request(request):
    page_pk = request.parser_context["kwargs"].get("page_pk")
    return Page.objects.get(pk=page_pk)


class IsPageOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        page = get_page_from_request(request)
        return page.owner_uuid == auth_service.get_user_id(request)


class IsPagePublic(permissions.BasePermission):
    def has_permission(self, request, view):
        page = get_page_from_request(request)
        return not page.is_private


class IsUserApprovedByPrivatePage(permissions.BasePermission):
    def has_permission(self, request, view):
        page = get_page_from_request(request)
        return page.is_private and page.followers.all().filter(
            follower_uuid=auth_service.get_user_id(request)
        )
