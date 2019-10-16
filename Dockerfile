FROM python:3.7-slim

COPY . ./

WORKDIR ./

RUN pip install -r requirements.txt

CMD [ "python", "./ship_log.py"]
