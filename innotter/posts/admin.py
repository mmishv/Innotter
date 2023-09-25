from authentication.admin import CustomModelAdmin
from django.contrib import admin
from posts.models import Post, PostLike


@admin.register(Post)
class PostAdmin(CustomModelAdmin):
    list_display = ("page", "content", "updated_at")


admin.site.register(PostLike, CustomModelAdmin)
