from authentication.admin import CustomModelAdmin
from django.contrib import admin
from pages.models import Page, PageFollower, PageRequest, Tag


@admin.register(Page)
class PageAdmin(CustomModelAdmin):
    list_display = ("uuid", "name", "owner_uuid", "is_private", "unblock_date")


admin.site.register(Tag, CustomModelAdmin)
admin.site.register(PageRequest, CustomModelAdmin)
admin.site.register(PageFollower, CustomModelAdmin)
