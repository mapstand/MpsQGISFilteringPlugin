QGIS_VERSION ?= latest

.PHONY: setup run stop

setup:
	cp .env.example .env
	sed -i "s/^UID=.*/UID=$$(id -u)/" .env
	sed -i "s/^GID=.*/GID=$$(id -g)/" .env
	mkdir -p qgis-profile/QGIS3/profiles/default/python/plugins
	mkdir -p qgis-profile/QGIS4/profiles/default/python/plugins
	@echo "Setup complete (UID=$$(id -u) GID=$$(id -g))"

run:
	xhost +local:docker
	QGIS_VERSION=$(QGIS_VERSION) docker compose up

stop:
	docker compose down
