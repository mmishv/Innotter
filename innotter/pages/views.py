import uuid

from authentication.permissions import IsAdministrator, IsModerator, IsNotBlocked
from authentication.service import AuthService
from aws.s3_service import S3Service
from pages.models import Page, Tag
from pages.permissions import IsPageOwner, PageIsNotBlocked
from pages.serializers import (
    PageCreateSerializer,
    PageFullInfoSerializer,
    PagePatchSerializer,
    TagSerializer,
)
from pages.service import PageService
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from innotter.producer import PublishEventService


class MultiSerializerViewSetMixin(object):
    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super(MultiSerializerViewSetMixin, self).get_serializer_class()


class MultiPermissionViewSetMixin(object):
    def get_permissions(self):
        try:
            return [
                permission()
                for permission in self.permission_action_classes[self.action]
            ]
        except (KeyError, AttributeError):
            return super(MultiPermissionViewSetMixin, self).get_permissions()


class PageViewSet(
    MultiSerializerViewSetMixin, MultiPermissionViewSetMixin, viewsets.ModelViewSet
):
    queryset = Page.objects.all()
    serializer_class = PageFullInfoSerializer
    serializer_action_classes = {
        "create": PageCreateSerializer,
        "partial_update": PagePatchSerializer,
    }
    permission_action_classes = {
        "list": [IsNotBlocked],
        "retrieve": [IsNotBlocked],
        "create": [IsNotBlocked],
        "toggle_visibility": [IsPageOwner],
        "partial_update": [IsPageOwner],
        "add_tag": [IsPageOwner],
        "remove_tag": [IsPageOwner],
        "subscribe": [IsNotBlocked, PageIsNotBlocked],
        "unsubscribe": [IsNotBlocked, PageIsNotBlocked],
        "follow_requests": [IsPageOwner, PageIsNotBlocked],
        "accept_request": [IsPageOwner, IsNotBlocked, PageIsNotBlocked],
        "reject_request": [IsPageOwner, IsNotBlocked, PageIsNotBlocked],
        "accept_all_requests": [IsPageOwner, IsNotBlocked, PageIsNotBlocked],
        "reject_all_requests": [IsPageOwner, IsNotBlocked, PageIsNotBlocked],
        "destroy": [IsPageOwner],
        "block": [IsAdministrator | IsModerator, IsNotBlocked],
        "upload_image": [IsPageOwner],
        "user_pages": [IsNotBlocked],
    }

    search_fields = ["name", "uuid", "tags__name"]
    filter_backends = (filters.SearchFilter,)
    auth_service = AuthService()
    page_service = PageService()
    image_service = S3Service()
    statistics_service = PublishEventService()

    def perform_destroy(self, instance):
        if instance.image_s3_path:
            self.image_service.delete_page_image(instance.image_s3_path)
        self.statistics_service.publish_delete_page(str(instance.id))
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        owner_uuid = self.auth_service.get_user_id(self.request)
        page = serializer.save(owner_uuid=owner_uuid, uuid=uuid.uuid4())
        self.statistics_service.publish_create_page(str(page.id), str(owner_uuid))

    @action(detail=True, methods=["patch"])
    def toggle_visibility(self, request, pk=None):
        page = self.get_object()
        self.page_service.toggle_page_visibility(page)
        return Response({"detail": "You have successfully changed page visibility"})

    @action(detail=False, methods=["get"])
    def user(self, request):
        user_uuid = (
            request.query_params.get("user_uuid")
            if "user_uuid" in request.query_params.keys()
            else self.auth_service.get_user_id(self.request)
        )
        pages = Page.objects.filter(owner_uuid=user_uuid)
        serializer = PageFullInfoSerializer(pages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["patch"])
    def add_tag(self, request, pk=None):
        page = self.get_object()
        tag_name = request.data["name"]
        self.page_service.add_tag(page, tag_name)
        return Response({"detail": "You have successfully added to page"})

    @action(detail=True, methods=["patch"])
    def remove_tag(self, request, pk=None):
        page = self.get_object()
        tag_name = request.data["name"]
        self.page_service.remove_tag(page, tag_name)
        return Response({"detail": "You have successfully removed tag from page"})

    @action(detail=True, methods=["post"])
    def subscribe(self, request, pk=None):
        page = self.get_object()
        user_uuid = self.auth_service.get_user_id(self.request)
        self.page_service.subscribe(page, user_uuid)
        return Response({"detail": "You have successfully subscribed to the page"})

    @action(detail=True, methods=["post"])
    def unsubscribe(self, request, pk=None):
        page = self.get_object()
        user_uuid = self.auth_service.get_user_id(self.request)
        self.page_service.unsubscribe(page, user_uuid)
        return Response({"detail": "You have successfully unsubscribed to the page"})

    @action(detail=True, methods=["get"])
    def follow_requests(self, request, pk=None):
        page = self.get_object()
        requests = self.page_service.get_follow_requests(page)
        self.statistics_service.publish_update_followers(str(page.id), 1)
        return Response(data=requests, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def accept_request(self, request, pk=None):
        page = self.get_object()
        request = request.data["request"]
        self.page_service.accept_request(page, request)
        return Response({"detail": "Request accepted"})

    @action(detail=True, methods=["post"])
    def reject_request(self, request, pk=None):
        page = self.get_object()
        request = request.data["request"]
        self.page_service.reject_request(page, request)
        return Response({"detail": "Request rejected"})

    @action(detail=True, methods=["post"])
    def accept_all_requests(self, request, pk=None):
        page = self.get_object()
        self.page_service.accept_all_requests(page)
        return Response({"detail": "All requests accepted"})

    @action(detail=True, methods=["post"])
    def reject_all_requests(self, request, pk=None):
        page = self.get_object()
        self.page_service.reject_all_requests(page)
        return Response({"detail": "All requests rejected"})

    @action(detail=True, methods=["patch"])
    def block(self, request, pk=None):
        page = self.get_object()
        # let forever be 100 years
        days = int(request.query_params.get("days", 36525))
        self.page_service.block_page(page, days)
        return Response({"detail": f"Page is successfully blocked for {days} days"})

    @action(detail=True, methods=["patch"])
    def upload_image(self, request, pk=None):
        page = self.get_object()
        file = request.FILES.get("file")
        self.page_service.upload_page_image(page, file)
        return Response({"detail": "Page image is successfully uploaded"}, status=201)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
