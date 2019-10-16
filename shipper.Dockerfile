FROM python:3.7-slim

WORKDIR .

COPY .env .env
COPY ./docker_ship_log.py ./docker_ship_log.py
COPY ./alert_utilities/.env ./alert_utilities/.env
COPY ./alert_utilities/telegram_notifier.py ./alert_utilities/telegram_notifier.py

RUN pip install -r requirements.txt

CMD [ "python", "./docker_ship_log.py"]
