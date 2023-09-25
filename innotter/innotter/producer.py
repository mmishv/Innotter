import os
from json import dumps

from pika import BlockingConnection, URLParameters

queue = "statistics_queue"


def publish(body: dict) -> None:
    connection = None
    while True:
        if not connection or not connection.is_open:
            connection = BlockingConnection(
                URLParameters(os.environ.get("RABBITMQ_URL"))
            )
        channel = connection.channel()
        channel.queue_declare(queue=queue)

        channel.basic_publish(
            exchange="", routing_key="statistics_queue", body=str.encode(dumps(body))
        )
        break


class PublishEventService:
    @staticmethod
    def get_page_create_message(page_id: str, owner_uuid: str) -> dict:
        return {
            "event": "page_create",
            "page_uuid": page_id,
            "owner_uuid": owner_uuid,
        }

    @staticmethod
    def get_page_delete_message(page_id: str) -> dict:
        return {"event": "page_delete", "page_uuid": page_id}

    @staticmethod
    def get_page_update_message(page_id: str, field: str, delta: int) -> dict:
        return {
            "event": "page_update",
            "page_uuid": page_id,
            "field": field,
            "delta": delta,
        }

    @staticmethod
    def update_likes(page_id: str, delta: int):
        message = PublishEventService.get_page_update_message(page_id, "likes", delta)
        publish(message)

    @staticmethod
    def publish_update(page_id: str, field: str, delta: int):
        message = PublishEventService.get_page_update_message(page_id, field, delta)
        publish(message)

    @staticmethod
    def publish_update_posts(page_id: str, delta: int):
        PublishEventService.publish_update(page_id, "posts", delta)

    @staticmethod
    def publish_update_followers(page_id: str, delta: int):
        PublishEventService.publish_update(page_id, "followers", delta)

    @staticmethod
    def publish_update_follow_requests(page_id: str, delta: int):
        PublishEventService.publish_update(page_id, "follow_requests", delta)

    @staticmethod
    def publish_update_likes(page_id: str, delta: int):
        PublishEventService.publish_update(page_id, "likes", delta)

    @staticmethod
    def publish_delete_page(page_id: str):
        message = PublishEventService.get_page_delete_message(page_id)
        publish(message)

    @staticmethod
    def publish_create_page(page_id: str, owner_uuid: str):
        message = PublishEventService.get_page_create_message(page_id, owner_uuid)
        publish(message)
