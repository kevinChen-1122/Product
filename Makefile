SERVICES := database-service

.PHONY: all build start stop restart logs clean

all: build

build:
	@for service in $(SERVICES); do \
  		echo "Building $$service..."; \
  		docker-compose build --no-cache $$service; \
    done

up:
ifdef service
	@docker-compose up -d $(service)
else
	@docker-compose up -d
endif

down:
ifdef service
	@docker-compose down $(service)
else
	@docker-compose down
endif

restart: down up

logs:
ifdef service
	@docker-compose logs -f $(service)
else
	@docker-compose logs -f
endif

clean:
	@docker-compose down --volumes

bash:
ifdef service
	@docker exec -it $(service) /bin/bash
endif
