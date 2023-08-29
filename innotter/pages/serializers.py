from pages.models import Page, Tag
from rest_framework import serializers


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("name",)


class PageFullInfoSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = Page
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["follow_requests"] = [
            elem.requester_uuid for elem in instance.follow_requests.all()
        ]
        data["followers"] = [elem.follower_uuid for elem in instance.followers.all()]
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
