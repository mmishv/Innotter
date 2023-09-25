import os

import pytest
import requests
from pages.models import Page
from posts.models import Post
from rest_framework.test import APIClient
from tests.conftest import create_page_data, test_credentials, user_jwt

client = APIClient()
GET_STATISTICS_URL = os.getenv("STATISTICS_URL")


@pytest.mark.django_db
def test_statistics(user_jwt, create_page_data):
    token = user_jwt
    compare = (
        lambda data, likes, posts, reqs, followers: data["likes"] == likes
        and data["followers"] == followers
        and data["posts"] == posts
        and data["follow_requests"] == reqs
    )
    client.post("/pages/", create_page_data, **{"HTTP_TOKEN": token})
    page = Page.objects.filter(name=create_page_data["name"]).first()
    url = f"{GET_STATISTICS_URL}{page.uuid}/"
    headers = {"token": token}

    response = requests.request("GET", url, headers=headers)
    assert response.status_code == 200
    assert compare(response.json(), likes=0, posts=0, followers=0, reqs=0)

    post_data = {"content": "test post"}
    client.post(f"/pages/{page.pk}/posts/", post_data, **{"HTTP_TOKEN": token})
    response = requests.request("GET", url, headers=headers)
    assert compare(response.json(), likes=0, posts=1, followers=0, reqs=0)

    client.post(f"/pages/{page.pk}/posts/", post_data, **{"HTTP_TOKEN": token})
    response = requests.request("GET", url, headers=headers)
    assert compare(response.json(), likes=0, posts=2, followers=0, reqs=0)

    post = Post.objects.filter(content=post_data["content"]).first()
    client.delete(
        f"/pages/{page.pk}/posts/{post.pk}/", post_data, **{"HTTP_TOKEN": token}
    )
    response = requests.request("GET", url, headers=headers)
    assert compare(response.json(), likes=0, posts=1, followers=0, reqs=0)

    client.delete(f"/pages/{page.id}/", **{"HTTP_TOKEN": token})
