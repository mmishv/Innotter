import pytest
from pages.models import PageFollower
from posts.models import Post
from posts.permissions import IsPageOwner, IsPagePublic, IsUserApprovedByPrivatePage
from rest_framework.test import APIClient
from tests.conftest import (
    base_request,
    create_page_data,
    mock_get_role,
    page,
    test_credentials,
    user_jwt,
)

client = APIClient()


@pytest.fixture
def mock_is_owner(mocker):
    is_owner_mock = mocker.patch.object(IsPageOwner, "has_permission")
    return is_owner_mock


@pytest.fixture
def mock_is_approved(mocker):
    is_approved_mock = mocker.patch.object(
        IsUserApprovedByPrivatePage, "has_permission"
    )
    return is_approved_mock


@pytest.fixture
def mock_page_visibility(mocker):
    is_public_mock = mocker.patch.object(IsPagePublic, "has_permission")
    return is_public_mock


@pytest.fixture
def post(page):
    token, page = page
    post_data = {"content": "test post"}
    client.post(f"/pages/{page.pk}/posts/", post_data, **{"HTTP_TOKEN": token})
    post = Post.objects.filter(content=post_data["content"]).first()
    return token, page, post


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_role, page_visibility, is_owner, is_approved, expected_status",
    [
        ("USER", True, True, False, 200),
        ("USER", True, False, False, 200),
        ("USER", False, True, False, 200),
        ("USER", False, False, True, 200),
        ("USER", False, False, False, 403),
        ("MODERATOR", False, False, False, 200),
        ("ADMIN", False, False, False, 200),
    ],
)
def test_list_posts(
    page,
    mock_get_role,
    mock_is_owner,
    mock_page_visibility,
    mock_is_approved,
    user_role,
    page_visibility,
    is_owner,
    is_approved,
    expected_status,
):
    token, page = page
    mock_is_owner.return_value = is_owner
    mock_get_role.return_value = user_role
    mock_page_visibility.return_value = page_visibility
    mock_is_approved.return_value = is_approved
    response = client.get(f"/pages/{page.pk}/posts/", **{"HTTP_TOKEN": token})
    assert response.status_code == expected_status


@pytest.mark.parametrize("is_owner, expected_status", [(True, 201), (False, 403)])
@pytest.mark.django_db
def test_create_post(page, mock_is_owner, is_owner, expected_status):
    token, page = page
    mock_is_owner.return_value = is_owner
    post_data = {"content": "test post"}
    PageFollower.objects.create(follower_uuid=page.owner_uuid, page=page)
    response = client.post(
        f"/pages/{page.pk}/posts/", post_data, **{"HTTP_TOKEN": token}
    )
    assert response.status_code == expected_status
    if expected_status == 201:
        assert Post.objects.filter(page=page).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "page_visibility, is_owner, is_approved, expected_status",
    [
        (True, False, False, 201),
        (False, True, False, 201),
        (False, False, True, 201),
        (False, False, False, 403),
    ],
)
@pytest.mark.django_db
def test_create_reply(
    post,
    mock_is_owner,
    mock_page_visibility,
    mock_is_approved,
    page_visibility,
    is_owner,
    is_approved,
    expected_status,
):
    token, page, post = post
    mock_is_owner.return_value = is_owner
    mock_page_visibility.return_value = page_visibility
    mock_is_approved.return_value = is_approved
    reply_data = {"content": "test reply"}
    response = client.post(
        f"/pages/{page.pk}/posts/{post.pk}/reply/", reply_data, **{"HTTP_TOKEN": token}
    )
    assert response.status_code == expected_status
    if expected_status == 200:
        post.refresh_from_db()
        assert Post.objects.filter(reply_to=post.id).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_role, is_owner, expected_status",
    [
        ("USER", True, 204),
        ("USER", False, 403),
        ("MODERATOR", False, 204),
        ("ADMIN", False, 204),
    ],
)
def test_delete_post(
    post, mock_get_role, mock_is_owner, user_role, is_owner, expected_status
):
    token, page, post = post
    mock_is_owner.return_value = is_owner
    mock_get_role.return_value = user_role
    response = client.delete(
        f"/pages/{page.pk}/posts/{post.pk}/", **{"HTTP_TOKEN": token}
    )
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "is_owner, expected_status",
    [
        (True, 200),
        (False, 403),
    ],
)
def test_patch_post(post, mock_is_owner, is_owner, expected_status):
    token, page, post = post
    post_data = {"content": "new content"}
    mock_is_owner.return_value = is_owner
    response = client.patch(
        f"/pages/{page.pk}/posts/{post.pk}/", post_data, **{"HTTP_TOKEN": token}
    )
    assert response.status_code == expected_status
    if expected_status == 200:
        post.refresh_from_db()
        assert post.content == post_data["content"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "expected_status, is_public, is_owner, is_approved",
    [
        (200, False, True, False),
        (200, False, False, True),
        (403, False, False, False),
        (200, True, False, False),
    ],
)
def test_like(
    post,
    expected_status,
    mock_is_owner,
    mock_is_approved,
    mock_page_visibility,
    is_public,
    is_owner,
    is_approved,
):
    token, page, post = post
    mock_page_visibility.return_value = is_public
    mock_is_approved.return_value = is_approved
    mock_is_owner.return_value = is_owner
    response = client.patch(
        f"/pages/{page.pk}/posts/{post.pk}/like/", **{"HTTP_TOKEN": token}
    )
    assert response.status_code == expected_status
    post.refresh_from_db()
    if expected_status == 200:
        assert len(post.liked_by.all()) == 1
        response = client.patch(
            f"/pages/{page.pk}/posts/{post.pk}/unlike/", **{"HTTP_TOKEN": token}
        )
        assert response.status_code == expected_status
        post.refresh_from_db()
        assert len(post.liked_by.all()) == 0


@pytest.mark.django_db
def test_get_user_likes(post):
    token, page, post = post
    user_uuid = page.owner_uuid
    client.patch(f"/pages/{page.pk}/posts/{post.pk}/like/", **{"HTTP_TOKEN": token})
    response = client.get(f"/users/{user_uuid}/likes/", **{"HTTP_TOKEN": token})
    assert response.status_code == 200
    assert len(response.data) == 1


@pytest.mark.django_db
def test_get_news(post):
    token, page, post = post
    user_uuid = page.owner_uuid
    response = client.get(f"/users/{user_uuid}/news/", **{"HTTP_TOKEN": token})
    assert response.status_code == 200
    assert len(response.data) == 1
