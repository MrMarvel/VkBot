FROM python:3

ADD src /app/src
ADD requirements.txt /app/requirements.txt
ADD setup.py /app/setup.py
ADD LICENSE.txt /app/LICENSE.txt
ADD README.md /app/README.md

WORKDIR /app
RUN python setup.py install
RUN rm -rf ./*

VOLUME ["data"]

CMD [ "python", "-m", "queue_vk_bot_mrmarvel" ]