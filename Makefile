clean:
	rm -rf *.tar.gz dist build *.egg-info *.rpm
	find . -name "*.pyc" | xargs rm

compile: uv.lock
	@uv pip compile --group=demo --group=docs pyproject.toml -o requirements.txt

sync:
	@uv sync --dev

update_schema:
	@curl -XGET --insecure -o schema/v1.yml https://localhost/api/v1/schema/

tox:
	# create a tox pyenv virtualenv based on 3.7.x
	# install tox and tox-pyenv in that ve
	# activate that ve before running this
	@tox

docs:
	@echo "Generating docs..."
	@cd doc && rm -rf build && make html
	@open doc/build/html/index.html

release: clean
	@bin/release.sh

napoleon-gate:
	@.venv/bin/python bin/check_napoleon_gate.py --target sphinx_hosting --target sandbox/demo

napoleon-gate-strict:
	@.venv/bin/python bin/check_napoleon_gate.py --strict --target sphinx_hosting --target sandbox/demo

napoleon-gate-baseline:
	@mkdir -p doc/quality
	@.venv/bin/python bin/check_napoleon_gate.py --write-baseline --target sphinx_hosting --target sandbox/demo
