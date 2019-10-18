FROM python:3.7-slim

WORKDIR .

COPY .env .env
COPY ./ship_log.py ./ship_log.py
COPY ./alert_utilities/.env ./alert_utilities/.env
COPY ./alert_utilities/telegram_notifier.py ./alert_utilities/telegram_notifier.py
COPY ./prometheus_exporter/results_manager.py ./prometheus_exporter/results_manager.py
COPY ./requirements.txt requirements.txt

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "./ship_log.py"]
