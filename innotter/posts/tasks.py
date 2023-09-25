from aws.ses_service import SESService

from innotter.celery import app


@app.task(queue="ses_queue")
def send_email(page_name, recipient_list):
    ses_service = SESService()
    response = ses_service.send_email(
        subject="New Innotter post!",
        body=f"New post was published on {page_name}! Check and rate!",
        sender="sender@example.com",
        recipients=recipient_list,
    )
    return response
