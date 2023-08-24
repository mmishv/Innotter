from django.db import models
from pages.models import Page


class Post(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="posts")
    content = models.CharField(max_length=180)
    reply_to = models.ForeignKey(
        "Post", on_delete=models.SET_NULL, null=True, blank=True, related_name="replies"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"post on {self.page}, created {self.created_at}"


class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="liked_by")
    user_uuid = models.CharField(max_length=36)

    class Meta:
        unique_together = ("post", "user_uuid")

    def __str__(self):
        return f"user {self.user_uuid} liked post {self.post}"
