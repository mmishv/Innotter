import pytest
from pages.models import Page, PageFollower, PageRequest, Tag
from pages.tests.fixtures import (
    mock_get_user_id,
    mock_is_owner_permission,
    patch_page_data,
    tag,
)
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
    "expected_status, is_private",
    [
        (200, False),
        (200, True),
    ],
)
def test_subscribe(page, mock_get_user_id, expected_status, is_private):
    token, page = page
    page.is_private = is_private
    page.save()
    response = client.post(f"/pages/{page.pk}/subscribe/", **{"HTTP_TOKEN": token})
    assert response.status_code == expected_status
    if is_private:
        assert PageRequest.objects.filter(
            requester_uuid=mock_get_user_id.return_value, page=page
        ).exists()
    else:
        assert PageFollower.objects.filter(
            follower_uuid=mock_get_user_id.return_value, page=page
        ).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "expected_status, is_private",
    [
        (200, False),
        (200, True),
    ],
)
def test_unsubscribe(
    page, create_page_data, mock_get_user_id, expected_status, is_private
):
    token, page = page
    page.is_private = is_private
    page.save()
    client.post(f"/pages/{page.pk}/subscribe/", **{"HTTP_TOKEN": token})
    response = client.post(f"/pages/{page.pk}/unsubscribe/", **{"HTTP_TOKEN": token})
    assert response.status_code == expected_status
    if is_private:
        assert not PageRequest.objects.filter(
            requester_uuid=mock_get_user_id.return_value, page=page
        ).exists()
    else:
        assert not PageFollower.objects.filter(
            follower_uuid=mock_get_user_id.return_value, page=page
        ).exists()


@pytest.mark.django_db
def test_subscribe_twice(page, create_page_data, mock_get_user_id):
    token, page = page
    client.post(f"/pages/{page.pk}/subscribe/", **{"HTTP_TOKEN": token})
    response = client.post(f"/pages/{page.pk}/subscribe/", **{"HTTP_TOKEN": token})
    assert response.status_code == 400


@pytest.mark.django_db
def test_subscribe_yourself(page, create_page_data):
    token, page = page
    response = client.post(f"/pages/{page.pk}/subscribe/", **{"HTTP_TOKEN": token})
    assert response.status_code == 400


@pytest.mark.django_db
def test_unsubscribe_yourself(page, create_page_data):
    token, page = page
    client.post(f"/pages/{page.pk}/subscribe/", **{"HTTP_TOKEN": token})
    response = client.post(f"/pages/{page.pk}/unsubscribe/", **{"HTTP_TOKEN": token})
    assert response.status_code == 400


@pytest.mark.django_db
def test_unsubscribe_not_subscriber(page, create_page_data):
    token, page = page
    response = client.post(f"/pages/{page.pk}/unsubscribe/", **{"HTTP_TOKEN": token})
    assert response.status_code == 400


@pytest.mark.django_db
def test_private_page_follow_requests(
    page, create_page_data, mock_get_user_id, mock_is_owner_permission
):
    token, page = page
    page.is_private = True
    page.save()
    client.post(f"/pages/{page.pk}/subscribe/", **{"HTTP_TOKEN": token})
    mock_is_owner_permission.return_value = True
    response = client.get(f"/pages/{page.pk}/follow_requests/", **{"HTTP_TOKEN": token})
    assert response.status_code == 200
    assert mock_get_user_id.return_value in response.data


@pytest.mark.django_db
def test_public_page_follow_requests(page, create_page_data):
    token, page = page
    response = client.get(f"/pages/{page.pk}/follow_requests/", **{"HTTP_TOKEN": token})
    assert response.status_code == 400


@pytest.mark.django_db
@pytest.mark.parametrize(
    "is_all, endpoint",
    [
        (False, "accept_request"),
        (False, "reject_request"),
        (True, "accept_all_requests"),
        (True, "reject_all_requests"),
    ],
)
def test_request_actions(
    page, create_page_data, mock_get_user_id, mock_is_owner_permission, is_all, endpoint
):
    token, page = page
    page.is_private = True
    page.save()
    client.post(f"/pages/{page.pk}/subscribe/", **{"HTTP_TOKEN": token})
    mock_is_owner_permission.return_value = True
    if not is_all:
        request = mock_get_user_id.return_value
        response = client.post(
            f"/pages/{page.pk}/{endpoint}/",
            {"request": request},
            **{"HTTP_TOKEN": token},
        )
    else:
        response = client.post(f"/pages/{page.pk}/{endpoint}/", **{"HTTP_TOKEN": token})
    assert response.status_code == 200
    response = client.get(f"/pages/{page.pk}/follow_requests/", **{"HTTP_TOKEN": token})
    assert len(response.data) == 0
