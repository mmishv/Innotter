from authentication.permissions import IsAdministrator, IsNotBlocked
from authentication.service import AdminService
from posts.service import PostService
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

admin_service = AdminService()


# ModelViewSet specify the queryset attribute is mandatory,
# but since there is no user model I use ViewSet
class UserActionsViewSet(viewsets.ViewSet):
    @action(detail=True, methods=["PATCH"], permission_classes=[IsAdministrator])
    def block(self, request, pk=None):
        admin_service.block_user(request.META.get("HTTP_TOKEN"), pk)
        return Response({"detail": "User and his pages are successfully blocked"})

    @action(detail=True, methods=["PATCH"], permission_classes=[IsAdministrator])
    def unblock(self, request, pk=None):
        admin_service.unblock_user(request.META.get("HTTP_TOKEN"), pk)
        return Response({"detail": "User and his pages are successfully unblocked"})

    @action(detail=True, methods=["GET"], permission_classes=[IsNotBlocked])
    def likes(self, request, pk=None):
        posts = PostService().get_liked_posts(pk)
        return Response(posts)

    @action(detail=True, methods=["GET"], permission_classes=[IsNotBlocked])
    def news(self, request, pk=None):
        posts = PostService().get_news_feed(pk)
        return Response(posts)
