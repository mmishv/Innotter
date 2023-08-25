import os

import pytest
import requests
from authentication.service import AuthService
from django.http import HttpRequest

BASE_URL = os.getenv("USER_MANAGEMENT_BASE_URL")


@pytest.fixture
def test_credentials():
    return {"username": "test", "email": "test@gmail.com", "password": "1111"}


@pytest.fixture
def mock_get_role(mocker):
    auth_service_mock = mocker.patch.object(AuthService, "get_role")
    return auth_service_mock


@pytest.fixture
def mock_get_block_status(mocker):
    auth_service_mock = mocker.patch.object(AuthService, "get_block_status")
    return auth_service_mock


@pytest.fixture
def base_request():
    return HttpRequest()


@pytest.fixture
def invalid_jwt_request(base_request):
    base_request.META["HTTP_TOKEN"] = "invalid token"
    return base_request


@pytest.fixture
def user_jwt(test_credentials):
    signup_url = f"{BASE_URL}/auth/signup/"
    signup_response = requests.post(signup_url, json=test_credentials)
    access_token = signup_response.json().get("access_token")
    yield access_token
    delete_me_url = f"{BASE_URL}/users/me/"
    requests.delete(delete_me_url, headers={"token": access_token})


@pytest.fixture
def request_with_user_jwt(user_jwt, base_request):
    access_token = user_jwt
    base_request.META["HTTP_TOKEN"] = access_token
    return base_request
