clean:
	rm -rf *.tar.gz dist build *.egg-info *.rpm
	find . -name "*.pyc" | xargs rm
	find . -name "__pycache__" | xargs rm -rf

compile: uv.lock
	@uv pip compile --extra=docs pyproject.toml -o requirements.txt

sync:
	@uv sync -U --extra=docs --extra=sandbox

update_schema:
	@curl -XGET --insecure -o schema/v1.yml https://localhost/api/v1/schema/

tox:
	# create a tox pyenv virtualenv based on 3.7.x
	# install tox and tox-pyenv in that ve
	# activate that ve before running this
	@tox

release: clean
	@uv build --sdist --wheel
	@twine upload dist/*
