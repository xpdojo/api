import logging
import random

import yaml
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logging.basicConfig(level=logging.DEBUG)

with open('config.yaml', 'r') as file:
    slack_config = yaml.safe_load(file)

# https://slack.dev/python-slack-sdk/
# https://slack.dev/python-slack-sdk/web/index.html
# https://api.slack.com/apps/
# OAuth & Permissions > OAuth Tokens for Your Workspace > Bot User OAuth Token
# slack_token = os.environ["SLACK_BOT_TOKEN"]
slack_token = slack_config["app"]["token"]

# Channel > Integrations > Apps > Add apps
channel_id = slack_config["channel"]["test"]

client = WebClient(token=slack_token)

# Sample menu list
yangjae_food = {
    "얌얌김밥": "rice_ball",
    "작은공간": "hot_pepper",
    "쿠니라멘": "ramen",
    "버거킹": "hamburger",
    "피자스쿨": "pizza",
    "스파게티 스토리": "spaghetti",
    "호랑이 초밥": "sushi",
    "사천루": "ramen",
    "태국식당": "stew",
    "백화네": "curry",
    "두두 돼지불백": "pig",
    "김치뚝딱": "hot_pepper",
    "월례네 부대찌개": "stew",
    "장금수 부대찌개": "stew",
    "한솥도시락": "bento",
    "크라이치즈버거": "hamburger",
    "백화네부엌": "ramen",
    "피크니끄": "green_salad",
    "무쏘": "knife_fork_plate",
    "써브웨이": "sandwich",
    "소곰집": "stew",
    "강촌원조쭈꾸미": "pig",
    # "백채김치찌개": "stew", # 맛없음
    "히노카츠": "cut_of_meat",
    "본죽&비빔밥": "rice",
    "영영상점": "green_salad",
    "빨간모자피자": "pizza",
    "송담추어탕": "stew",
    "차돌49": "rice",
    "삼식이": "stew",
    "사계솔 보쌈": "cut_of_meat",
    "카츠오우": "cut_of_meat",
    "엽기떡볶이": "hot_pepper",
    "영이네": "hot_pepper",
    "죠스떡볶이": "hot_pepper",
}


def emoji_escape(emoji_name: str):
    return f":{emoji_name}:"


# --------------- config ---------------

# Define function to generate Slack message payload for voting
def generate_emoji_voting_payload(ranked_menu: dict):
    # Basic text and section block
    text = "어떤 메뉴가 가장 좋으세요? 투표해 주세요! :tada:"
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text
            }
        }
    ]

    # Generate text elements based on the ranked menu and corresponding emojis
    menu_text = []
    result_menu_emoji = []
    for _, (rank, menu) in enumerate(ranked_menu.items()):
        menu_text.append(f"{rank}. {menu} {emoji_escape(yangjae_food[menu])}")
        result_menu_emoji.append(yangjae_food[menu])

    # Add the menu options to the blocks
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "\n".join(menu_text)
        }
    })

    # Complete payload
    payload = {
        "channel": channel_id,
        "text": text,
        "blocks": blocks
    }

    return payload, result_menu_emoji


def main():
    # Randomly select 5 menu items
    # selected_menu = random.sample(menu_list, 5) # list
    selected_menu = random.sample(list(yangjae_food.keys()), 5)  # dict

    # Rank the selected menu items from 1 to 5
    ranked_menu = {f"{i + 1}": menu for i, menu in enumerate(selected_menu)}

    try:
        # https://api.slack.com/messaging/sending
        payload, result_menu_emoji = generate_emoji_voting_payload(ranked_menu)
        print(payload)
        response = client.chat_postMessage(**payload)
        message_ts = response['ts']  # The timestamp of the sent message

        # Define emojis to add as reactions
        # only english!!!
        # emojis_to_add = result_menu_emoji
        print(result_menu_emoji)
        emojis_to_add = ["one", "two", "three", "four", "five", "x"]

        # Simulating adding the emoji reactions
        # reactions:write 권한이 필요한데 chat:write 권한만 있어서 에러 발생
        # {"error":"missing_scope","needed":"reactions:write","provided":"chat:write"}
        # Your Apps > OAuth & Permissions > Scopes > Add an OAuth Scope
        # reinstall your app
        for emoji in emojis_to_add:
            try:
                client.reactions_add(
                    channel=channel_id,
                    timestamp=message_ts,
                    name=emoji.strip(":")  # Remove the colons from the emoji name
                )
            except SlackApiError as e:
                print(f"Error adding emoji: {e.response['error']}")
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'

    print(response)


if __name__ == '__main__':
    main()
