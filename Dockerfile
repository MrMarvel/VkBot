FROM python:3

WORKDIR /usr/src/app

ADD ./src/queue_vk_bot_mrmarvel ./queue_vk_bot_mrmarvel
	
RUN pip install -r requirements.txt


CMD [ "python", "-m", "queue_vk_bot_mrmarvel" ]