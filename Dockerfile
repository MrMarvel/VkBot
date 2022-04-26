FROM python:3

ADD ./src/queue_vk_bot_mrmarvel ./app

WORKDIR /app
RUN pip install -r requirements.txt

CMD [ "python", "-m", "queue_vk_bot_mrmarvel" ]