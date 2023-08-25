from authentication.service import AuthService
from rest_framework import exceptions, permissions

auth_service = AuthService()


class HasExpectedValue(permissions.BasePermission):
    def __init__(self, expected_value, check_method):
        self.expected_value = expected_value
        self.check_method = check_method

    def check_value(self, request):
        try:
            return self.check_method(request)
        except exceptions.AuthenticationFailed:
            return None

    def has_object_permission(self, request, view, obj):
        value = self.check_value(request)
        return value == self.expected_value

    def has_permission(self, request, view):
        value = self.check_value(request)
        return value == self.expected_value


class IsRole(HasExpectedValue):
    def __init__(self, role):
        super().__init__(role, auth_service.get_role)


class IsAdministrator(IsRole):
    def __init__(self):
        super().__init__("ADMIN")


class IsModerator(IsRole):
    def __init__(self):
        super().__init__("MODERATOR")


class IsUser(IsRole):
    def __init__(self):
        super().__init__("USER")


class IsBlocked(HasExpectedValue):
    def __init__(self):
        super().__init__(False, auth_service.get_block_status)
