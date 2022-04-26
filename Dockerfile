FROM python:3

ADD . /app

WORKDIR /app
RUN pip install -r requirements.txt

VOLUME ["data"]

CMD [ "python", "-m", "src.queue_vk_bot_mrmarvel" ]