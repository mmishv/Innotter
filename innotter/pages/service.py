from datetime import datetime, timedelta

from aws.s3_service import S3Service
from pages.models import Page, PageFollower, PageRequest, Tag
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from innotter.producer import PublishEventService


class PageService:
    def __init__(self):
        self.statistics_service = PublishEventService()

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

    def subscribe(self, page: Page, user_uuid):
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
            self.statistics_service.publish_update_follow_requests(str(page.id), 1)
            PageRequest.objects.create(requester_uuid=user_uuid, page=page)
        else:
            self.statistics_service.publish_update_followers(str(page.id), 1)
            PageFollower.objects.create(follower_uuid=user_uuid, page=page)

    def unsubscribe(self, page: Page, user_uuid):
        if page.owner_uuid == user_uuid:
            raise ValidationError("You can't unsubscribe from yourself")
        follower = PageFollower.objects.filter(
            follower_uuid=user_uuid, page=page
        ).first()
        if follower:
            self.statistics_service.publish_update_followers(str(page.id), -1)
            follower.delete()
            return
        request = PageRequest.objects.filter(
            requester_uuid=user_uuid, page=page
        ).first()
        if request:
            self.statistics_service.publish_update_follow_requests(str(page.id), -1)
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

    def accept_request(self, page, user_uuid):
        request = get_object_or_404(PageRequest, requester_uuid=user_uuid, page=page)
        PageFollower.objects.create(follower_uuid=user_uuid, page=page)
        request.delete()
        self.accept_requests_for_statistics(str(page.id), 1)

    def reject_request(self, page, user_uuid):
        request = get_object_or_404(PageRequest, requester_uuid=user_uuid, page=page)
        request.delete()
        self.statistics_service.publish_update_follow_requests(str(page.id), -1)

    def accept_all_requests(self, page):
        requests = page.follow_requests.all()
        for elem in requests:
            PageFollower.objects.create(follower_uuid=elem.requester_uuid, page=page)
        PageRequest.objects.filter(page=page).delete()
        self.accept_requests_for_statistics(str(page.id), len(requests))

    def reject_all_requests(self, page):
        requests = PageRequest.objects.filter(page=page)
        requests.delete()
        self.statistics_service.publish_update_follow_requests(
            str(page.id), -len(requests)
        )

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
        image_s3_path = image_service.upload_page_image(file, page.id)
        page.image_s3_path = image_s3_path
        page.save()

    def accept_requests_for_statistics(self, page_id: str, cnt: int):
        self.statistics_service.publish_update_followers(str(page_id), cnt)
        self.statistics_service.publish_update_follow_requests(str(page_id), -cnt)
