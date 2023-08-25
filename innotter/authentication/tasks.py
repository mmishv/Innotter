import os

import requests
from celery import shared_task
from rest_framework import exceptions


@shared_task
def validate_token(access_token):
    validate_jwt_url = os.getenv("VALIDATE_JWT_URL")
    try:
        response = requests.get(validate_jwt_url, headers={"token": access_token})
        if response.status_code == 200:
            return response.json()
        else:
            raise exceptions.AuthenticationFailed(
                code=401, detail="JWT processing decode error: invalid or expired token"
            )
    except requests.exceptions.RequestException:
        raise ConnectionError("User-management service is not available")
