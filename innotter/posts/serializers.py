from aws.s3_service import S3Service
from pages.models import Page
from posts.models import Post
from rest_framework import serializers


class PostSerializer(serializers.ModelSerializer):
    page = serializers.PrimaryKeyRelatedField(queryset=Page.objects.all())
    reply_to = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Post
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["liked_by"] = [elem.user_uuid for elem in instance.liked_by.all()]
        if instance.reply_to:
            page = instance.reply_to.page
            data["reply_to"] = {
                "post_id": instance.reply_to.id,
                "page_uuid": page.uuid,
                "page_id": page.id,
            }
        data["replies"] = PostSerializer(
            instance.replies.all().order_by("-created_at"), many=True
        ).data
        data["page"] = {
            "id": instance.page.id,
            "name": instance.page.name,
            "uuid": instance.page.uuid,
            "owner_uuid": instance.page.owner_uuid,
        }
        if instance.page.image_s3_path:
            image = S3Service().get_page_image(instance.page.image_s3_path)
            data["page"]["image"] = image
        return data


class PostContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("content",)
