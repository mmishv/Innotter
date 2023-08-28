import pytest
from authentication.service import AuthService
from pages.models import Tag
from pages.permissions import IsPageOwner


@pytest.fixture
def patch_page_data():
    return {"name": "New name", "description": "New description", "uuid": "new uuid"}


@pytest.fixture
def tag():
    return Tag.objects.create(name="test tag")


@pytest.fixture
def mock_is_owner_permission(mocker):
    is_owner_mock = mocker.patch.object(IsPageOwner, "has_object_permission")
    return is_owner_mock


@pytest.fixture
def mock_get_user_id(mocker):
    mocker = mocker.patch.object(AuthService, "get_user_id")
    mocker.return_value = "another id"
    return mocker
