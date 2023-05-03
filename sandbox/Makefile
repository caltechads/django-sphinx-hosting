VERSION = 1.1.0

PACKAGE = sphinx_hosting_demo

.PHONY: clean dist build force-build tag dev dev-detached devup devdown logall log exec restart docker-clean docker-destroy-db docker-destroy list  package
#======================================================================

clean:
	rm -rf *.tar.gz dist *.egg-info *.rpm
	find . -name "*.pyc" -exec rm '{}' ';'

dist: clean
	@python setup.py sdist

package:
	(cd ..; python setup.py sdist)
	cp ../dist/django-sphinx-hosting-${VERSION}.tar.gz django-sphinx-hosting.tar.gz

build: package
	docker build -t ${PACKAGE}:${VERSION} .
	docker tag ${PACKAGE}:${VERSION} ${PACKAGE}:latest
	docker image prune -f

force-build: package
	docker build --no-cache -t ${PACKAGE}:${VERSION} .
	docker tag ${PACKAGE}:${VERSION} ${PACKAGE}:latest
	docker image prune -f

dev:
	docker-compose up

dev-detached:
	docker-compose up -d

devup: dev-detached

devdown:
	docker-compose down

logall:
	docker-compose logs -f

log:
	docker logs -f sphinx_hosting_demo

exec:
	docker exec -it sphinx_hosting_demo /bin/bash

restart:
	docker-compose restart sphinx_hosting_demo

docker-clean:
	docker stop $(shell docker ps -a -q)
	docker rm $(shell docker ps -a -q)

docker-destroy-db: docker-clean
	docker volume rm sandbox_sphinx_hosting_demo_data

docker-destroy: docker-clean docker-destroy-db

list:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' | xargs
