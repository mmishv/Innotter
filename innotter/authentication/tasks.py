import os

import requests
from celery import shared_task
from rest_framework import exceptions


def perform_request(url, method, headers=None, params=None, data=None) -> dict:
    try:
        response = requests.request(
            method, url, headers=headers, params=params, data=data
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            raise exceptions.AuthenticationFailed(
                code=403, detail="You must be an administrator to perform this action"
            )
        else:
            raise exceptions.AuthenticationFailed(
                code=401, detail="JWT processing decode error: invalid or expired token"
            )
    except requests.exceptions.RequestException:
        raise ConnectionError("Service is not available")


@shared_task(queue="user_management_queue")
def validate_token(access_token) -> dict:
    validate_jwt_url = os.getenv("VALIDATE_JWT_URL")
    headers = {"token": access_token}
    return perform_request(validate_jwt_url, "GET", headers)


@shared_task(queue="user_management_queue")
def change_user_block_status(access_token, user_uuid, block_status: bool) -> None:
    patch_user_url = os.getenv("PATCH_USER_URL")
    headers = {"token": access_token}
    perform_request(
        f"{patch_user_url}/{user_uuid}/",
        "PATCH",
        headers,
        params={"is_blocked": block_status},
    )


@shared_task(queue="user_management_queue")
def get_secure_data(user_id) -> dict:
    url = f'{os.getenv("SECURE_DATA_URL")}/{user_id}/'
    headers = {"api-key": os.getenv("API_KEY")}
    return perform_request(url, "GET", headers)
