import os
import requests
# from dotenv import load_dotenv


PY_DIRNAME, PY_FILENAME = os.path.split(os.path.abspath(__file__))
ENV_FILE = os.path.join(PY_DIRNAME, ".env")
# load_dotenv(dotenv_path=ENV_FILE)

with open(ENV_FILE, "r") as fname:
    env = {}
    for line in env:
        if len(line):
            env[line.split("=")[0]] = line.split("=")[1]
    return env


TELEGRAM_TOKEN = env["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = env["TELEGRAM_CHAT_ID"]
TELEGRAM_ENDPOINT = "https://api.telegram.org/bot{}/sendMessage"

class NotificationHandler():

    def emit(self, message):
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        return requests.post(
            TELEGRAM_ENDPOINT.format(TELEGRAM_TOKEN), data=payload
            ).content
