import pytest
from authentication.service import AuthService
from rest_framework import exceptions
from tests.conftest import (
    base_request,
    invalid_jwt_request,
    request_with_user_jwt,
    test_credentials,
    user_jwt,
)


def test_valid_jwt(test_credentials, request_with_user_jwt):
    request = request_with_user_jwt
    data = AuthService().retrieve_user_data(request)
    assert data.get("username") == test_credentials.get("username")
    assert data.get("email") == test_credentials.get("email")
    assert data.get("role") == "USER"
    assert not data.get("is_blocked")


def test_invalid_jwt(invalid_jwt_request):
    with pytest.raises(exceptions.AuthenticationFailed):
        AuthService().retrieve_user_data(invalid_jwt_request)


@pytest.mark.parametrize(
    "method_name, expected_result", [("get_role", "USER"), ("get_block_status", False)]
)
def test_jwt_methods(request_with_user_jwt, method_name, expected_result):
    request = request_with_user_jwt
    jwt_auth = AuthService()
    method = getattr(jwt_auth, method_name)
    result = method(request)
    assert result == expected_result


@pytest.mark.parametrize(
    "method_name, expected_result",
    [("get_user_id", "id"), ("get_role", "USER"), ("get_block_status", False)],
)
def test_invalid_jwt_methods(
    request_with_user_jwt, method_name, expected_result, invalid_jwt_request
):
    with pytest.raises(exceptions.AuthenticationFailed):
        jwt_auth = AuthService()
        method = getattr(jwt_auth, method_name)
        method(invalid_jwt_request)
