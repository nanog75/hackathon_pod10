
DOCKER_TAG = 0.1

build:
	docker build -t nanog75/pod10:$(DOCKER_TAG) .

cli:
	docker run -it \
		-v $(shell pwd):/local \
		-w /local \
		nanog75/pod10:$(DOCKER_TAG) bash

