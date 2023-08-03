clean:
	rm -rf *.tar.gz dist build *.egg-info *.rpm
	find . -name "*.pyc" | xargs rm
	find . -name "__pycache__" | xargs rm -rf

dist: clean
	@python setup.py sdist
	@python setup.py bdist_wheel --universal

pypi: dist
	@twine upload dist/*

update_schema:
	@curl -XGET --insecure -o schema/v1.yml https://localhost/api/v1/schema/

tox:
	# create a tox pyenv virtualenv based on 3.7.x
	# install tox and tox-pyenv in that ve
	# activate that ve before running this
	@tox

release: clean
	@python setup.py sdist bdist_wheel
	@twine upload dist/*
