import base64
import os

import boto3

PAGE_IMAGE_BUCKET = "page-images"
CONTENTS_KEY = "Contents"


class SessionSingleton:
    _instance = None

    @classmethod
    def get_instance(cls, aws_access_key_id, aws_secret_access_key):
        if cls._instance is None:
            session = boto3.Session(
                aws_secret_access_key=aws_secret_access_key,
                aws_access_key_id=aws_access_key_id,
            )
            cls._instance = session
        return cls._instance


class S3Singleton:
    _instance = None

    def __new__(cls, aws_access_key_id, aws_secret_access_key, endpoint_url):
        if cls._instance is None:
            session = SessionSingleton.get_instance(
                aws_access_key_id, aws_secret_access_key
            )
            cls._instance = session.client("s3", endpoint_url=endpoint_url)
            try:
                cls._instance.head_bucket(Bucket=PAGE_IMAGE_BUCKET)
            except cls._instance.exceptions.ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    try:
                        cls._instance.create_bucket(Bucket=PAGE_IMAGE_BUCKET)
                    except Exception:
                        raise ConnectionError("Error creating bucket in S3")
                else:
                    raise ConnectionError("Error interacting with S3")

        return cls._instance


class S3Service:
    def __init__(self):
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.endpoint_url = os.getenv("ENDPOINT_URL")

    def _perform_s3_action(self, action_callback):
        try:
            s3 = S3Singleton(
                self.aws_access_key_id, self.aws_secret_access_key, self.endpoint_url
            )
            return action_callback(s3)
        except Exception as e:
            raise ConnectionError(f"Error interacting with S3: {str(e)}")

    def upload_page_image(self, file, page_uuid: str) -> str:
        def upload_to_s3(s3):
            file_path = f"page_image/{page_uuid}"
            s3.upload_fileobj(file, PAGE_IMAGE_BUCKET, file_path)
            return file_path

        return self._perform_s3_action(upload_to_s3)

    def get_page_image(self, avatar_s3_path: str) -> str:
        def get_from_s3(s3):
            try:
                s3_ob = s3.get_object(Bucket=PAGE_IMAGE_BUCKET, Key=avatar_s3_path)
                image_bytes = s3_ob["Body"].read()
                return base64.b64encode(image_bytes).decode("utf-8")
            except s3.exceptions.NoSuchKey:
                raise FileNotFoundError(f"Image not found: {avatar_s3_path}")

        return self._perform_s3_action(get_from_s3)

    def delete_page_image(self, avatar_s3_path: str) -> None:
        def delete_from_s3(s3):
            try:
                s3.delete_object(Bucket=PAGE_IMAGE_BUCKET, Key=avatar_s3_path)
            except s3.exceptions.NoSuchKey:
                raise FileNotFoundError(f"Image not found: {avatar_s3_path}")

        self._perform_s3_action(delete_from_s3)
