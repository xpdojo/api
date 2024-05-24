"""
알림 발송 - Mail
"""
import json
import uuid
from datetime import datetime
from pprint import pprint

import urllib3

ENV = "dev"
SENDGRID_API_KEY = "SENDGRID_API_KEY"
SENDGRID_TEMPLATE_ID = "SENDGRID_TEMPLATE_ID"
TESTER_MAIL_ADDRESS = "tester@example.com"


class InvalidEnvironmentException(Exception):
    """dev, prod가 아닌 환경일 때 발생하는 예외"""

    def __init__(self):
        super().__init__("env must be dev or prod")


class SendGridException(Exception):
    """SendGrid API 호출 시 발생하는 예외"""

    def __init__(self, message):
        super().__init__("SendGrid API 호출 실패:", message)


class Mailer:
    """
    알림을 보내기 위한 클래스
    """

    def __init__(self, env="dev"):
        if env not in ("local", "dev", "prod"):
            raise InvalidEnvironmentException()

        # if env in ["local", "dev"]:
        #     pass
        # elif env in ["prod"]:
        #     pass

        self.sendgrid_sender_email_address = "noreply@example.com"
        self.sendgrid_sender_name = "Test Script"

    def __str__(self):
        """
        java에서 toString()과 같은 역할을 한다.
        이거 없으면 <__main__.Configs object at 0x1042820d0> 이렇게 출력됨.
        configs.__dict__로도 가능하긴 함.
        """
        return json.dumps(self.__dict__)

    def send(self, http, messages=None):
        """
        이메일을 발송한다.

        - `1 <https://docs.sendgrid.com/ui/sending-email/how-to-send-an-email-with-dynamic-templates#send-a-transactional-email>`_
        - `2 <https://docs.sendgrid.com/ui/sending-email/adding-dynamic-content-with-handlebars-in-marketing-campaigns>`_
        - `3 <https://docs.sendgrid.com/for-developers/sending-email/using-handlebars#basic-iterator>`_
        """
        if not messages:
            print("메시지가 없습니다.")
            return None

        print("Email 클라이언트로 메시지를 발송한다.")
        mail_sender = {
            "email": self.sendgrid_sender_email_address,
            "name": self.sendgrid_sender_name
        }

        sendgrid_request_header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SENDGRID_API_KEY}",
        }
        print(messages)
        _personalizations = [
            {
                "to": [
                    {"email": receiverEmail} for receiverEmail in messages[0]["receiverEmails"]
                ],
                # https://docs.sendgrid.com/api-reference/mail-send/mail-send
                "dynamic_template_data": {
                    "count": len(messages),  # for 신규 신청
                    "requests": messages,
                }
            },
        ]
        pprint(_personalizations)

        sendgrid_request_body = json.dumps(
            {
                "template_id": messages[0]["templateId"],
                "personalizations": _personalizations,
                # "content": [
                #     {
                #         "type": "text/html",
                #         "value": "<p>Hello from Twilio SendGrid!</p><p>Sending with the email service trusted by developers and marketers for <strong>time-savings</strong>, <strong>scalability</strong>, and <strong>delivery expertise</strong>.</p><p>%open-track%</p>"
                #     }
                # ],
                # "subject": "Your Example Order Confirmation",
                "from": mail_sender,
                "categories": ["test", "document"],
                "mail_settings": {
                    "bypass_list_management": {"enable": False},
                    "footer": {"enable": True},
                    "sandbox_mode": {"enable": False},
                },
                "tracking_settings": {
                    "click_tracking": {"enable": True, "enable_text": False},
                    "open_tracking": {"enable": True, "substitution_tag": "%open-track%"},
                    "subscription_tracking": {"enable": True},
                },
            }
        )

        # 메일 발송
        # https://stackoverflow.com/questions/61998724/httpresponse-object-has-no-attribute-json
        try:
            sendgrid_res: urllib3.HTTPResponse = http.request(
                method="POST",
                url="https://api.sendgrid.com/v3/mail/send",
                headers=sendgrid_request_header,
                body=sendgrid_request_body,
            )
            # print(dir(sendgrid_res))
            if sendgrid_res.status != 202:
                raise SendGridException("sendgrid_res.status != 202")
        except SendGridException as error:
            # 에러 발생 시 히스토리 저장
            # {'errors': [{'message': "The requestor's IP Address is not whitelisted", 'field': None, 'help': None}]}
            print(error)

        return None


def main():
    sender = Mailer(ENV)

    print(f"current_time -> {datetime.now().strftime('%Y-%m-%dT%H:%M:%S %p')}")

    http = urllib3.PoolManager()
    message1 = {
        "exportRequestId": 4,
        "messageCode": str(uuid.uuid4()),
        "eventDateTime": "2023-09-25T10:42:45.416223034",
        "receiverCompanyName": "receiver1 Co.",
        "receiverEmails": [TESTER_MAIL_ADDRESS],

        "certificateLanguage": "국문",
        "vehicleInformationNumber": "a2345678901234567",
        "sellerCompanyName": "seller Corp",

        "title": "이것은 메일 제목입니다.",
        "templateId": SENDGRID_TEMPLATE_ID,
    }
    message2 = {
        "exportRequestId": 4,
        "messageCode": str(uuid.uuid4()),
        "eventDateTime": "2023-09-25T10:42:45.416223034",
        "receiverCompanyName": "receiver1 Co.",
        "receiverEmails": [TESTER_MAIL_ADDRESS],

        "certificateLanguage": "국문",
        "vehicleInformationNumber": "b2345678901234567",
        "sellerCompanyName": "seller Corp",

        "title": "이것은 메일 제목입니다.",
        "templateId": SENDGRID_TEMPLATE_ID,
    }
    messages = [message1, message2]
    sender.send(http, messages=messages)


""" python send_mail.py """
if __name__ == "__main__":
    main()
