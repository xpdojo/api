import yaml
from requests import Response, post

with open('config.yaml', 'r') as file:
    slack_config = yaml.safe_load(file)

slack_channel_id = slack_config["channel"]["test"]
slack_token = slack_config["app"]["token"]


def send_slack_message(message):
    _payload = {
        "channel": slack_channel_id,
        "text": message
    }

    response: Response = post(
        url="https://slack.com/api/chat.postMessage",
        headers={
            "Authorization": f"Bearer {slack_token}",
            "Content-Type": "application/json"
        },
        json=_payload
    )
    print(response.status_code)
    print(response.text)


if __name__ == '__main__':
    send_slack_message("Hello World!")
