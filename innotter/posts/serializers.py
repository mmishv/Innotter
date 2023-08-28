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
        return data


class PostContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("content",)

    def create(self, validated_data):
        page_pk = self.context["view"].kwargs.get("page_pk")
        page = Page.objects.get(pk=page_pk)
        new_post = Post.objects.create(page=page, **validated_data)
        return new_post
