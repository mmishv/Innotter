from authentication.tasks import change_user_block_status, validate_token
from pages.models import Page
from pages.service import PageService
from rest_framework import exceptions


class AuthService:
    @staticmethod
    def retrieve_user_data(request):
        access_token = request.META.get("HTTP_TOKEN")
        try:
            data = validate_token.delay(access_token).get()
        except ConnectionError as e:
            raise exceptions.APIException(code=500, detail=str(e))
        except exceptions.AuthenticationFailed as e:
            raise exceptions.AuthenticationFailed(code=e.status_code, detail=str(e))
        return data

    def _get_value_from_jwt(self, request, key):
        data = self.retrieve_user_data(request)
        return data.get(key)

    def get_user_id(self, request):
        return self._get_value_from_jwt(request, "id")

    def get_role(self, request):
        return self._get_value_from_jwt(request, "role")

    def get_block_status(self, request):
        return self._get_value_from_jwt(request, "is_blocked")


class AdminService:
    page_service = PageService()

    def block_user(self, access_token, user_uuid):
        change_user_block_status.delay(access_token, user_uuid, block_status=True).get()
        for page in Page.objects.filter(owner_uuid=user_uuid):
            self.page_service.block_page(page)

    def unblock_user(self, access_token, user_uuid):
        change_user_block_status.delay(
            access_token, user_uuid, block_status=False
        ).get()
        for page in Page.objects.filter(owner_uuid=user_uuid):
            # when checking for page blocking, unblock date is checked either for None,
            # or for the fact that it is <= than the current date. when the page is blocked,
            # the unblock date is the current date + n days period. set n=0, then at the next check
            # the unblock date will be earlier than the current one and the page will be unblocked
            self.page_service.block_page(page, period=0)
