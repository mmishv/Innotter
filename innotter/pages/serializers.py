from datetime import datetime

from aws.s3_service import S3Service
from django.utils import timezone
from pages.models import Page, Tag
from posts.serializers import PostSerializer
from rest_framework import serializers


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class PageFullInfoSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = Page
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        today = timezone.now().date()
        if instance.unblock_date is None or instance.unblock_date.date() <= today:
            data["unblock_date"] = None
        data["follow_requests"] = [
            elem.requester_uuid for elem in instance.follow_requests.all()
        ]
        data["followers"] = [elem.follower_uuid for elem in instance.followers.all()]
        data["posts"] = PostSerializer(
            instance.posts.all().order_by("-created_at"), many=True
        ).data
        if len(instance.image_s3_path):
            data["image"] = S3Service().get_page_image(instance.image_s3_path)
        return data


class PageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = (
            "name",
            "description",
        )


class PagePatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = (
            "name",
            "uuid",
            "description",
        )
