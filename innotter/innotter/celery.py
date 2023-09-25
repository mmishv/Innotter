import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "innotter.settings")

app = Celery("innotter")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.task_queues = {
    "user_management_queue": {
        "exchange": "user_management_exchange",
        "routing_key": "user_management",
    },
    "ses_queue": {"exchange": "ses_exchange", "routing_key": "ses"},
}
