import requests
from dotenv import load_dotenv


PY_DIRNAME, PY_FILENAME = os.path.split(os.path.abspath(__file__))
ENV_FILE = os.path.join(PY_DIRNAME, ".env")
load_dotenv(dotenv_path=ENV_FILE)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
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
