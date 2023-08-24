from django.contrib import admin
from pages.models import Page, PageFollower, PageRequest, Tag


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("uuid", "name", "owner_uuid", "is_private", "unblock_date")


admin.site.register(Tag)
admin.site.register(PageRequest)
admin.site.register(PageFollower)
