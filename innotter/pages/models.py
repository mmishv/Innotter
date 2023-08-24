from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return f"tag {self.name}"


class Page(models.Model):
    name = models.CharField(max_length=80)
    uuid = models.CharField(max_length=36, unique=True)
    description = models.TextField()
    tags = models.ManyToManyField("Tag", related_name="pages")
    owner_uuid = models.CharField(max_length=36)
    image_s3_path = models.CharField(blank=True)
    is_private = models.BooleanField(default=False)
    unblock_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return (
            f"page with uuid {self.uuid}, owner {self.owner_uuid}: "
            f"name {self.name}, {'private' if self.is_private else 'public'}"
        )


class PageFollower(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="followers")
    follower_uuid = models.CharField(max_length=36)

    class Meta:
        unique_together = ("page", "follower_uuid")

    def __str__(self):
        return f"user {self.follower_uuid} follows page {self.page}"


class PageRequest(models.Model):
    page = models.ForeignKey(
        Page, on_delete=models.CASCADE, related_name="follow_requests"
    )
    requester_uuid = models.CharField(max_length=36)

    class Meta:
        unique_together = ("page", "requester_uuid")

    def __str__(self):
        return f"user {self.requester_uuid} requested page {self.page}"
