import os
import sys
import time
import argparse

import requests
import telegram
from dotenv import load_dotenv


def get_long_pooling_response(headers):
    long_pooling_url = "https://dvmn.org/api/long_polling/"
    paylaod={}
    print("test",paylaod)
    try:

        response = requests.get(long_pooling_url,
                                headers=headers, timeout=200,params=paylaod)
        response.raise_for_status()
        lesson_review = response.json()

        print("first attempt", lesson_review)

        if lesson_review["status"] == "timeout":
            print("fill payload")
            payload = {
                'last_attempt_timestamp': lesson_review[
                    "timestamp_to_request"]
            }

        else:
            print("test pass")
            pass
            # lesson_review = response.json()
            # print("what with timeout",lesson_review)

    # except KeyError:
    #     continue
    except requests.exceptions.ReadTimeout:
        pass
    except requests.exceptions.ConnectionError:
        print("Ошибка соединения", file=sys.stderr)
        time.sleep(15)

    return lesson_review

def send_message_from_bot(long_pooling_result, user_chat_id, tg_token,
                          tg_chat_id):
    bot = telegram.Bot(token=tg_token)

    if user_chat_id:
        chat_id = user_chat_id

    # print("what is in long_pooling_result",
    #
    #       long_pooling_result)
    try:
        if long_pooling_result["new_attempts"][0]["is_negative"]:
            bot.send_message(
                text=f'''Ваша работа к уроку {long_pooling_result["new_attempts"][0]["lesson_title"]
                } - проверенна.Необходимо внести правки и отправить на повторную проверку.Ссылка на урок {
                long_pooling_result["new_attempts"][0]["lesson_url"]}''',
                chat_id=chat_id)
        else:
            bot.send_message(
                text='''Работа к уроку {response_up["new_attempts"][0]["lesson_title"]} - принята!Приступайте к следующему уроку.''',
                chat_id=chat_id)
    except:
        pass


def main():
    load_dotenv()

    devman_token = os.getenv("DEVMAN_TOKEN")
    tg_token = os.getenv("TG_BOT_TOKEN")
    tg_chat_id = os.getenv("TG_CHAT_ID")

    parser = argparse.ArgumentParser(
        description="Enter your chat_id ")
    parser.add_argument('chat_id', help='Ваш персональный чат ID в Телеграмм', type=int,default="tg_chat_id")
    args = parser.parse_args()
    user_chat_id =args.chat_id



    headers = {
        "Authorization": devman_token
    }

    # user_chat_id = 230938172

    while True:
        long_pooling_result = get_long_pooling_response(headers)
        send_message_from_bot(long_pooling_result, user_chat_id, tg_token,
                              tg_chat_id)


if __name__ == '__main__':
    main()
