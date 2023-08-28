import pytest
from authentication.service import AuthService
from django.utils import timezone
from pages.models import Page
from rest_framework import exceptions
from rest_framework.test import APIClient
from tests.conftest import (
    base_request,
    create_page_data,
    invalid_jwt_request,
    mock_get_role,
    page,
    request_with_user_jwt,
    test_credentials,
    user_jwt,
)

client = APIClient()


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


@pytest.mark.django_db
@pytest.mark.parametrize(
    "action, expected_block_status", [("block", True), ("unblock", False)]
)
def test_block_unblock_user(
    mock_get_role, base_request, page, action, expected_block_status
):
    mock_get_role.return_value = "ADMIN"
    access_token, page = page
    base_request.META["HTTP_TOKEN"] = access_token
    user_uuid = AuthService().get_user_id(base_request)
    url = f"/users/{user_uuid}/{action}/"

    response = client.patch(url, **{"HTTP_TOKEN": access_token})
    assert response.status_code == 200
    assert AuthService().get_block_status(base_request) == expected_block_status

    assert all(
        [
            page.unblock_date is not None
            if expected_block_status
            else page.unblock_date.date() <= timezone.now().date()
            for page in Page.objects.filter(owner_uuid=user_uuid)
        ]
    )
