from datetime import datetime, timedelta

from django.db.models import Q
from pages.models import PageFollower
from posts.models import Post, PostLike
from posts.serializers import PostSerializer
from rest_framework.exceptions import ValidationError


class PostService:
    @staticmethod
    def like(post, user_uuid):
        if PostLike.objects.filter(post=post, user_uuid=user_uuid).exists():
            raise ValidationError("You have already liked this post")
        PostLike.objects.create(post=post, user_uuid=user_uuid)

    @staticmethod
    def unlike(post, user_uuid):
        if not PostLike.objects.filter(post=post, user_uuid=user_uuid).exists():
            raise ValidationError("The post wasn't liked")
        PostLike.objects.filter(post=post, user_uuid=user_uuid).delete()

    @staticmethod
    def get_liked_posts(user_uuid):
        likes = PostLike.objects.filter(user_uuid=user_uuid)
        liked_posts = [like.post for like in likes]
        post_serializer = PostSerializer(liked_posts, many=True)
        return post_serializer.data

    @staticmethod
    def get_news_feed(user_uuid):
        one_week_ago = datetime.now() - timedelta(days=7)
        own_pages_posts = Post.objects.filter(
            Q(page__owner_uuid=user_uuid) | Q(created_at__gte=one_week_ago)
        )
        followed_pages = [
            page for page in PageFollower.objects.filter(page__owner_uuid=user_uuid)
        ]
        followed_pages_posts = Post.objects.filter(
            Q(page__in=followed_pages) | Q(created_at__gte=one_week_ago)
        )
        combined_posts = own_pages_posts.union(followed_pages_posts).order_by(
            "-updated_at"
        )
        post_serializer = PostSerializer(combined_posts, many=True)
        return post_serializer.data
