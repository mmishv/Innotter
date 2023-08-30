import os
from json import dumps

from pika import BlockingConnection, URLParameters

queue = "statistics_queue"
connection = BlockingConnection(URLParameters(os.environ.get("RABBITMQ_URL")))

channel = connection.channel()
channel.queue_declare(queue=queue)


def publish(body: dict) -> None:
    channel.basic_publish(
        exchange="", routing_key="statistics_queue", body=str.encode(dumps(body))
    )


class PublishEventService:
    @staticmethod
    def get_page_create_message(page_uuid: str, owner_uuid: str) -> dict:
        return {
            "event": "page_create",
            "page_uuid": page_uuid,
            "owner_uuid": owner_uuid,
        }

    @staticmethod
    def get_page_delete_message(page_uuid: str) -> dict:
        return {"event": "page_delete", "page_uuid": page_uuid}

    @staticmethod
    def get_page_update_message(page_uuid: str, field: str, delta: int) -> dict:
        return {
            "event": "page_update",
            "page_uuid": page_uuid,
            "field": field,
            "delta": delta,
        }

    @staticmethod
    def update_likes(page_uuid: str, delta: int):
        message = PublishEventService.get_page_update_message(page_uuid, "likes", delta)
        publish(message)

    @staticmethod
    def publish_update(page_uuid: str, field: str, delta: int):
        message = PublishEventService.get_page_update_message(page_uuid, field, delta)
        publish(message)

    @staticmethod
    def publish_update_posts(page_uuid: str, delta: int):
        PublishEventService.publish_update(page_uuid, "posts", delta)

    @staticmethod
    def publish_update_followers(page_uuid: str, delta: int):
        PublishEventService.publish_update(page_uuid, "followers", delta)

    @staticmethod
    def publish_update_follow_requests(page_uuid: str, delta: int):
        PublishEventService.publish_update(page_uuid, "follow_requests", delta)

    @staticmethod
    def publish_update_likes(page_uuid: str, delta: int):
        PublishEventService.publish_update(page_uuid, "likes", delta)

    @staticmethod
    def publish_delete_page(page_uuid: str):
        message = PublishEventService.get_page_delete_message(page_uuid)
        publish(message)

    @staticmethod
    def publish_create_page(page_uuid: str, owner_uuid: str):
        message = PublishEventService.get_page_create_message(page_uuid, owner_uuid)
        publish(message)
