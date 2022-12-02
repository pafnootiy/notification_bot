import argparse
import logging
import os
import sys
import time

import requests
import telegram
from dotenv import load_dotenv


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_chat_id,bot):
        super().__init__()
        self.chat_id = tg_chat_id
        self.bot = bot


    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(text=log_entry, chat_id=self.chat_id)


def get_message_from_bot(headers, user_chat_id, logger, bot):
    long_pooling_url = "https://dvmn.org/api/long_polling/"
    payload = {}
    while True:
        try:
            response = requests.get(long_pooling_url,
                                    headers=headers, timeout=200,
                                    params=payload)
            response.raise_for_status()
            lesson_review = response.json()

            if lesson_review["status"] == "found":
                payload = {
                    'timestamp': lesson_review[
                        "last_attempt_timestamp"]
                }

                new_attempt = lesson_review["new_attempts"][0]

                if new_attempt['is_negative']:
                    bot.send_message(
                        text=f'''Ваша работа к уроку "{new_attempt["lesson_title"]
                        }" - проверенна.Необходимо внести правки и отправить на повторную проверку.Ссылка на урок {
                        new_attempt["lesson_url"]}''',
                        chat_id=user_chat_id)
                else:
                    bot.send_message(
                        text=f'''Работа к уроку {new_attempt["lesson_title"]} - принята! Приступайте к следующему уроку.''',
                        chat_id=user_chat_id)

            elif lesson_review["status"] == "timeout":
                payload = {
                    'timestamp': lesson_review[
                        "timestamp_to_request"]
                }

        except (
                requests.exceptions.ReadTimeout,
                requests.exceptions.HTTPError):
            pass
        except requests.exceptions.ConnectionError:
            print("Ошибка соединения", file=sys.stderr)
            logger.error('Ошибка соединения')
            time.sleep(15)


def main():
    load_dotenv()

    devman_token = os.getenv("DEVMAN_TOKEN")
    tg_token = os.getenv("TG_BOT_TOKEN")
    tg_chat_id = os.getenv("TG_CHAT_ID")
    bot = telegram.Bot(token=tg_token)

    logger = logging.getLogger('Logger')
    logger.setLevel(logging.WARNING)
    logger.addHandler(TelegramLogsHandler(tg_chat_id,bot))
    logger.warning('Бот запущен!')

    headers = {
        "Authorization": devman_token
    }

    parser = argparse.ArgumentParser(
        description="Enter your chat_id ")
    parser.add_argument('--chat_id',
                        help='Ваш персональный чат ID в Телеграмм',
                        type=int, default=tg_chat_id)
    args = parser.parse_args()
    user_chat_id = args.chat_id

    get_message_from_bot(headers, user_chat_id, logger, bot)


if __name__ == '__main__':
    main()
