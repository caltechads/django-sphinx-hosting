VERSION = 1.7.1

PACKAGE = sphinx_hosting_demo

.PHONY: clean dist build force-build tag dev dev-detached devup devdown logall log exec restart docker-clean docker-destroy-db docker-destroy list  package
#======================================================================

clean:
	rm -rf *.tar.gz dist *.egg-info *.rpm
	find . -name "*.pyc" -exec rm '{}' ';'
	find . -name "__pycache__" -exec rm -rf '{}' ';'

dist: clean
	@uv build --sdist

uv.lock:
	@uv lock

compile: uv.lock
	@uv pip compile pyproject.toml -o requirements.txt

package:
	(cd ..; uv build --sdist)
	cp ../dist/django_sphinx_hosting-${VERSION}.tar.gz django-sphinx-hosting.tar.gz
	uv sync --upgrade --dev

build: package compile
	docker build -t ${PACKAGE}:${VERSION} .
	docker tag ${PACKAGE}:${VERSION} ${PACKAGE}:latest
	docker image prune -f

force-build: package compile
	docker build --no-cache -t ${PACKAGE}:${VERSION} .
	docker tag ${PACKAGE}:${VERSION} ${PACKAGE}:latest
	docker image prune -f

dev:
	docker compose up

dev-detached:
	docker compose up -d

devup: dev-detached

devdown:
	docker compose down

logall:
	docker compose logs -f

log:
	docker logs -f sphinx_hosting_demo

exec:
	docker exec -it sphinx_hosting_demo /bin/bash

restart:
	docker compose restart sphinx_hosting_demo

scout:
	docker scout cves --only-severity=critical,high ${PACKAGE}:${VERSION}

docker-clean:
	docker stop $(shell docker ps -a -q)
	docker rm $(shell docker ps -a -q)

docker-destroy-db: docker-clean
	docker volume rm sandbox_sphinx_hosting_demo_data

docker-destroy: docker-clean docker-destroy-db

test:
	@echo "Starting sphinx_hosting_demo..."
	docker compose up -d
	@echo "Waiting for sphinx_hosting_demo to be up on port 443..."
	@until nc -z localhost 443; do \
		echo "Still waiting for container..."; \
		sleep 2; \
	done
	@if [ -z "$(ARGS)" ]; then \
		docker exec sphinx_hosting_demo /bin/bash -c "TESTING=True DJANGO_SETTINGS_MODULE=demo.settings pytest -c pyproject.toml -m 'not integration' /ve/lib/python3.13/site-packages/sphinx_hosting/tests"; \
	else \
		docker exec sphinx_hosting_demo /bin/bash -c "TESTING=True DJANGO_SETTINGS_MODULE=demo.settings pytest -c pyproject.toml $(ARGS)"; \
	fi;

list:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' | xargs
