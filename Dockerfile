FROM python:3.6.8-stretch

RUN mkdir /source
COPY . /source

RUN mkdir /root/.ssh
COPY ssh_config /root/.ssh/config
RUN curl -o ~/.ssh/nanog75.key https://storage.googleapis.com/tesuto-public/nanog75.key
RUN chmod 400 ~/.ssh/nanog75.key

RUN pip install -r /source/requirements.txt



