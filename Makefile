
clean:
	@rm -rf venv3/
	@rm -rf venv/
	@rm -f dist/*

install: clean
	@virtualenv --quiet --python=`which python2.7` venv
	@./venv/bin/pip install --quiet ".[dev,build]"
	@virtualenv --quiet --python=`which python3.5` venv3
	@./venv3/bin/pip install --quiet ".[dev,build]"

major:
	@python3 update_version.py --major pyzpl/__init__.py

minor:
	@python3 update_version.py --minor pyzpl/__init__.py

patch:
	@python3 update_version.py --patch pyzpl/__init__.py

build: clean install
	venv/bin/python setup.py build
	venv/bin/python setup.py bdist_wheel
	venv3/bin/python setup.py build
	venv3/bin/python setup.py sdist
	venv3/bin/python setup.py bdist_wheel

dist: clean install build
	venv3/bin/twine upload dist/*

lint:
	@venv3/bin/flake8 .
	@venv/bin/flake8 .

test:
	@venv3/bin/pytest tests.py
	@venv/bin/pytest tests.py
