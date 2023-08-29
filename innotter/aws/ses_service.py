import os

from boto3.session import Session
from botocore.exceptions import BotoCoreError, ClientError


class SESService:
    def __init__(self):
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.region_name = os.getenv("AWS_DEFAULT_REGION")
        self.endpoint_url = os.getenv("ENDPOINT_URL")

    def _ses_session(self):
        return Session(
            aws_secret_access_key=self.aws_secret_access_key,
            aws_access_key_id=self.aws_access_key_id,
        )

    def _perform_ses_action(self, action_callback):
        try:
            session = self._ses_session()
            ses = session.client(
                "ses", region_name=self.region_name, endpoint_url=self.endpoint_url
            )
            return action_callback(ses)
        except BotoCoreError as e:
            raise ConnectionError(f"Error interacting with SES: {str(e)}")

    def send_email(self, subject, body, sender, recipients):
        def send_email_action(ses):
            try:
                response = ses.send_email(
                    Source=sender,
                    Destination={"ToAddresses": recipients},
                    Message={
                        "Subject": {"Data": subject},
                        "Body": {"Text": {"Data": body}},
                    },
                )
                return response
            except ClientError as e:
                raise ConnectionError(f"Error sending email: {str(e)}")

        return self._perform_ses_action(send_email_action)

    def verify_email(self, email):
        def verify_email_action(ses):
            try:
                response = ses.verify_email_identity(EmailAddress=email)
                return response
            except ClientError as e:
                raise ConnectionError(f"Error verifying email: {str(e)}")

        return self._perform_ses_action(verify_email_action)
