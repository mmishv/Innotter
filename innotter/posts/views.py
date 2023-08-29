from authentication.permissions import IsAdministrator, IsModerator, IsNotBlocked
from authentication.service import AuthService
from pages.models import Page
from pages.views import MultiPermissionViewSetMixin, MultiSerializerViewSetMixin
from posts.models import Post
from posts.permissions import IsPageOwner, IsPagePublic, IsUserApprovedByPrivatePage
from posts.serializers import PostContentSerializer, PostSerializer
from posts.service import PostService
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class PostViewSet(
    MultiSerializerViewSetMixin, MultiPermissionViewSetMixin, viewsets.ModelViewSet
):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    serializer_action_classes = {
        "create": PostContentSerializer,
        "partial_update": PostContentSerializer,
        "reply": PostContentSerializer,
    }
    permission_action_classes = {
        "list": [
            IsPagePublic
            | IsPageOwner
            | (IsUserApprovedByPrivatePage | IsAdministrator | IsModerator)
            & IsNotBlocked
        ],
        "retrieve": [
            IsPagePublic
            | IsPageOwner
            | (IsUserApprovedByPrivatePage | IsAdministrator | IsModerator)
            & IsNotBlocked
        ],
        "destroy": [IsPageOwner | IsNotBlocked & (IsAdministrator | IsModerator)],
        "partial_update": [IsPageOwner],
        "create": [IsNotBlocked & IsPageOwner],
        "reply": [
            IsNotBlocked,
            IsPagePublic | IsPageOwner | IsUserApprovedByPrivatePage,
        ],
        "like": [
            IsNotBlocked,
            IsPagePublic | IsPageOwner | IsUserApprovedByPrivatePage,
        ],
        "unlike": [
            IsNotBlocked,
            IsPagePublic | IsPageOwner | IsUserApprovedByPrivatePage,
        ],
    }

    post_service = PostService()
    auth_service = AuthService()

    def get_queryset(self):
        page_pk = self.kwargs.get("page_pk")
        return Post.objects.filter(page__pk=page_pk)

    def perform_create(self, serializer):
        page_pk = self.kwargs.get("page_pk")
        page = Page.objects.get(pk=page_pk)
        serializer.save(page=page)
        self.post_service.send_notifications(page)

    @action(detail=True, methods=["post"])
    def reply(self, request, page_pk=None, pk=None):
        serializer = PostContentSerializer(context={"view": self}, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(page=Page.objects.get(pk=page_pk), reply_to=self.get_object())
        return Response(
            {"detail": "You have successfully replied to the post"}, status=201
        )

    @action(detail=True, methods=["patch"])
    def like(self, request, page_pk=None, pk=None):
        post = self.get_object()
        user_uuid = self.auth_service.get_user_id(request)
        self.post_service.like(post, user_uuid)
        return Response({"detail": "You have successfully liked the post"})

    @action(detail=True, methods=["patch"])
    def unlike(self, request, page_pk=None, pk=None):
        post = self.get_object()
        user_uuid = self.auth_service.get_user_id(request)
        self.post_service.unlike(post, user_uuid)
        return Response({"detail": "You have successfully unliked the post"})
