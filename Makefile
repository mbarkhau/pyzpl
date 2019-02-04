help:
	@awk 'BEGIN {FS = ":.*?##"} /^[a-zA-Z_-]+:.*?##/ {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

clean: 							## clean virtualenvs and build artifacts
	@rm -rf venv3/
	@rm -rf venv/
	@rm -rf dist/
	@rm -rf build/
	@rm -rf __pycache__
	@rm -rf */__pycache__
	@rm -f *.pyc
	@rm -f */*.pyc
	@rm -rf *.egg-info

install: clean 					## create py2 and py3 virtualenvs and install dependencies
	@virtualenv --quiet --python=`which python2.7` venv
	@./venv/bin/pip install --quiet ".[dev,build]"
	@virtualenv --quiet --python=`which python3.5` venv3
	@./venv3/bin/pip install --quiet ".[dev,build]"

major: 							## increment major version
	@python3 update_version.py --major pyzpl/__init__.py

minor: 							## increment minor version
	@python3 update_version.py --minor pyzpl/__init__.py

patch: 							## increment patch version
	@python3 update_version.py --patch pyzpl/__init__.py

lint:							## run linters
	@venv3/bin/flake8 .
	@venv/bin/flake8 .

test: 							## run tests
	@venv3/bin/pytest tests.py
	@venv/bin/pytest tests.py

build: clean install lint test	## build source and wheel distributions
	venv/bin/python setup.py build
	venv/bin/python setup.py bdist_wheel
	venv3/bin/python setup.py build
	venv3/bin/python setup.py sdist
	venv3/bin/python setup.py bdist_wheel

dist: clean install build		## upload distributions to pypi
	venv3/bin/twine upload dist/*
