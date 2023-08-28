from datetime import datetime, timedelta

from aws.s3_service import S3Service
from pages.models import Page, PageFollower, PageRequest, Tag
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404


class PageService:
    @staticmethod
    def toggle_page_visibility(page: Page):
        page.is_private = not page.is_private
        page.save()

    @staticmethod
    def remove_tag(page: Page, tag_name):
        tag = get_object_or_404(Tag, name=tag_name)
        page.tags.remove(tag)

    @staticmethod
    def add_tag(page: Page, tag_name):
        tag = get_object_or_404(Tag, name=tag_name)
        page.tags.add(tag)

    @staticmethod
    def subscribe(page: Page, user_uuid):
        if page.owner_uuid == user_uuid:
            raise ValidationError("You can't subscribe to yourself")
        follower = PageFollower.objects.filter(
            follower_uuid=user_uuid, page=page
        ).first()
        request = PageRequest.objects.filter(
            requester_uuid=user_uuid, page=page
        ).first()
        if follower or request:
            raise ValidationError(
                "You are already a subscriber or have requested access"
            )
        if page.is_private:
            PageRequest.objects.create(requester_uuid=user_uuid, page=page)
        else:
            PageFollower.objects.create(follower_uuid=user_uuid, page=page)

    @staticmethod
    def unsubscribe(page: Page, user_uuid):
        if page.owner_uuid == user_uuid:
            raise ValidationError("You can't unsubscribe from yourself")
        follower = PageFollower.objects.filter(
            follower_uuid=user_uuid, page=page
        ).first()
        if follower:
            follower.delete()
            return
        request = PageRequest.objects.filter(
            requester_uuid=user_uuid, page=page
        ).first()
        if request:
            request.delete()
            return
        raise ValidationError("You aren't a subscriber or haven't requested access")

    @staticmethod
    def get_follow_requests(page):
        if page.is_private:
            requests = [elem.requester_uuid for elem in page.follow_requests.all()]
            return requests
        raise ValidationError(
            "Page follow requests is accessible only for private pages"
        )

    @staticmethod
    def accept_request(page, user_uuid):
        request = get_object_or_404(PageRequest, requester_uuid=user_uuid, page=page)
        PageFollower.objects.create(follower_uuid=user_uuid, page=page)
        request.delete()

    @staticmethod
    def reject_request(page, user_uuid):
        request = get_object_or_404(PageRequest, requester_uuid=user_uuid, page=page)
        request.delete()

    @staticmethod
    def accept_all_requests(page):
        for elem in page.follow_requests.all():
            PageFollower.objects.create(follower_uuid=elem.requester_uuid, page=page)
        PageRequest.objects.filter(page=page).delete()

    @staticmethod
    def reject_all_requests(page):
        PageRequest.objects.filter(page=page).delete()

    @staticmethod
    def block_page(page, period=36525):
        unblock_date = datetime.now() + timedelta(period)
        page.unblock_date = unblock_date
        page.save()

    @staticmethod
    def upload_page_image(page, file):
        if not file:
            raise ValidationError("No file provided")
        file_extension = file.name.split(".")[-1].lower()
        image_service = S3Service()
        if page.image_s3_path:
            image_service.delete_page_image(page.image_s3_path)
        if file_extension not in ["jpg", "jpeg", "png"]:
            raise ValidationError("Invalid file extension")
        image_s3_path = image_service.upload_page_image(file, page.uuid)
        page.image_s3_path = image_s3_path
        page.save()
