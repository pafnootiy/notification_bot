import os
import sys

import requests
import telegram
from dotenv import load_dotenv


def get_long_pooling_response(headers):
    long_pooling_url = "https://dvmn.org/api/long_polling/"

    while True:
        try:
            response = requests.get(long_pooling_url,
                                    headers=headers, timeout=200)
            response.raise_for_status()
            long_pooling_response = response.json()

            if long_pooling_response["status"] == "timeout":
                payload = {
                    'new_attempts["timestamp"]': long_pooling_response[
                        "timestamp_to_request"]
                }

                response = requests.get(long_pooling_url,
                                        headers=headers,
                                        params=payload)
                response.raise_for_status()
                long_pooling_response = response.json()

        except KeyError:
            continue
        except requests.exceptions.ReadTimeout:
            print(
                "Время ответа сервера истекло",
                file=sys.stderr)
        except requests.exceptions.ConnectionError:
            print("Ошибка соединения", file=sys.stderr)

        return long_pooling_response


def send_message_from_bot(response_up, user_chat_id, tg_token, tg_chat_id):
    bot = telegram.Bot(token=tg_token)

    if user_chat_id:
        chat_id = user_chat_id
    else:
        chat_id = tg_chat_id

    if response_up["new_attempts"][0]["is_negative"]:
        bot.send_message(
            text=f'Ваша работа к уроку'
                 f' {response_up["new_attempts"][0]["lesson_title"]} - проверенна. '
                 f'Необходимо внести правки и отправить на повторную проверку. '
                 f'Ссылка на урок {response_up["new_attempts"][0]["lesson_url"]}',
            chat_id=chat_id)
    else:
        bot.send_message(
            text=f'Работа к уроку {response_up["new_attempts"][0]["lesson_title"]} - принята! '
                 f'Приступайте к следующему уроку.'
                 f'', chat_id=chat_id)


def main():
    load_dotenv()

    token = os.getenv("TOKEN")
    tg_token = os.getenv("TG_BOT_TOKEN")
    tg_chat_id = os.getenv("TG_CHAT_ID")

    headers = {
        "Authorization": token
    }

    user_chat_id = input("Ведите свой чат ID: ")
    long_pooling_result = get_long_pooling_response(headers)
    send_message_from_bot(long_pooling_result, user_chat_id, tg_token,
                          tg_chat_id)


if __name__ == '__main__':
    main()
