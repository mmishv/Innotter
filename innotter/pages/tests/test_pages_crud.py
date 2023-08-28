import io

import pytest
from aws.s3_service import S3Service
from django.core.files.uploadedfile import SimpleUploadedFile
from pages.models import Page
from pages.tests.fixtures import mock_is_owner_permission, patch_page_data, tag
from PIL import Image
from rest_framework.test import APIClient
from tests.conftest import (
    base_request,
    create_page_data,
    mock_get_block_status,
    mock_get_role,
    page,
    test_credentials,
    user_jwt,
)

client = APIClient()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_role, days, expected_status",
    [
        ("ADMIN", None, 200),
        ("MODERATOR", None, 200),
        ("USER", None, 403),
        ("MODERATOR", 100, 200),
    ],
)
def test_block_page(page, mock_get_role, user_role, days, expected_status):
    token, page = page
    mock_get_role.return_value = user_role
    params = {} if days is None else {"days": days}
    response = client.patch(f"/pages/{page.pk}/block/", params, **{"HTTP_TOKEN": token})
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "extension, is_page_owner, is_valid, expected_status",
    [
        ("jpeg", True, True, 201),
        ("png", True, True, 201),
        ("gif", True, False, 400),
        ("bmp", True, False, 400),
        ("jpeg", False, True, 403),
    ],
)
def test_photo_upload(
    page, mock_is_owner_permission, extension, is_page_owner, is_valid, expected_status
):
    token, page = page
    mock_is_owner_permission.return_value = is_page_owner
    image = Image.new("RGB", (100, 100), color="red")
    image_io = io.BytesIO()
    image.save(image_io, extension.upper())
    image_file = SimpleUploadedFile(
        f"test.{extension}",
        content=image_io.getvalue(),
        content_type=f"image/{extension}",
    )
    response = client.patch(
        f"/pages/{page.pk}/upload_image/",
        {"file": image_file},
        **{"HTTP_TOKEN": token},
        format="multipart",
    )
    page.refresh_from_db()
    assert response.status_code == expected_status
    if expected_status == 201:
        assert page.image_s3_path is not None
        assert S3Service().get_page_image(page.image_s3_path)
    else:
        assert not page.image_s3_path


@pytest.mark.django_db
def test_search(page, tag):
    token, page = page
    response = client.get(f"/pages/?search={page.uuid}/", **{"HTTP_TOKEN": token})
    assert response.status_code == 200
    assert len(response.data) == 1

    client.patch(
        f"/pages/{page.pk}/add_tag/", {"name": tag.name}, **{"HTTP_TOKEN": token}
    )
    response = client.get(f"/pages/?search={tag.name}/", **{"HTTP_TOKEN": token})
    assert response.status_code == 200
    assert len(response.data) == 1

    response = client.get(f"/pages/?search={page.name}/", **{"HTTP_TOKEN": token})
    assert response.status_code == 200
    assert len(response.data) == 1


@pytest.mark.django_db
def test_create_page(user_jwt, create_page_data):
    token = user_jwt
    response = client.post("/pages/", create_page_data, **{"HTTP_TOKEN": token})
    assert response.status_code == 201
    assert Page.objects.filter(name=create_page_data["name"]).exists()


@pytest.mark.django_db
def test_create_page_unauthorized(user_jwt, create_page_data):
    response = client.post("/pages/", create_page_data)
    assert response.status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize(
    "is_owner_permission_value, expected_status",
    [
        (False, 403),
        (True, 200),
    ],
)
def test_change_visibility_permissions(
    page, mock_is_owner_permission, is_owner_permission_value, expected_status
):
    mock_is_owner_permission.return_value = is_owner_permission_value
    token, page = page
    response = client.patch(
        f"/pages/{page.pk}/toggle_visibility/", **{"HTTP_TOKEN": token}
    )
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "tag_name, expected_status",
    [
        ("test tag", 200),
        ("doesn't exist", 404),
    ],
)
def test_add_tag(page, tag, tag_name, expected_status):
    token, page = page
    response = client.patch(
        f"/pages/{page.pk}/add_tag/", {"name": tag_name}, **{"HTTP_TOKEN": token}
    )
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "tag_name, expected_status",
    [
        ("test tag", 200),
        ("doesn't exist", 404),
    ],
)
def test_remove_tag(page, tag, tag_name, expected_status):
    token, page = page
    response = client.patch(
        f"/pages/{page.pk}/remove_tag/", {"name": tag_name}, **{"HTTP_TOKEN": token}
    )
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "is_owner_permission_value, expected_status",
    [
        (False, 403),
        (True, 200),
    ],
)
@pytest.mark.django_db
def test_update_page_info(
    page,
    mock_is_owner_permission,
    is_owner_permission_value,
    expected_status,
    patch_page_data,
):
    token, page = page
    mock_is_owner_permission.return_value = is_owner_permission_value
    response = client.patch(
        f"/pages/{page.pk}/", patch_page_data, **{"HTTP_TOKEN": token}
    )
    assert response.status_code == expected_status


@pytest.mark.django_db
def test_update_page_info_duplicate_uuid(page, patch_page_data):
    token, page = page
    another_page_data = {"name": "another", "description": "another"}
    client.post("/pages/", another_page_data, **{"HTTP_TOKEN": token})
    patch_page_data["uuid"] = (
        Page.objects.filter(name=another_page_data["name"]).first().uuid
    )
    response = client.patch(
        f"/pages/{page.pk}/", patch_page_data, **{"HTTP_TOKEN": token}
    )
    assert response.status_code == 400
