from authentication.tasks import validate_token
from rest_framework import exceptions


class AuthService:
    def retrieve_user_data(self, request):
        access_token = request.META.get("HTTP_TOKEN")
        if not access_token:
            return None
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
        return self._get_value_from_jwt(request, "user_id")

    def get_role(self, request):
        return self._get_value_from_jwt(request, "role")

    def get_block_status(self, request):
        return self._get_value_from_jwt(request, "is_blocked")
