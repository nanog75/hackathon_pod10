FROM ydkdev/ydk-gen

RUN mkdir /source
COPY . /source

RUN apt-get update
RUN apt-get -y install sshpass

RUN mkdir /root/.ssh
COPY ssh_config /root/.ssh/config
RUN curl -o ~/.ssh/nanog75.key https://storage.googleapis.com/tesuto-public/nanog75.key
RUN chmod 400 ~/.ssh/nanog75.key

RUN pip install -r /source/requirements.txt



