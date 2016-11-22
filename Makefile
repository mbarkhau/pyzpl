
clean:
	rm -rf venv3/
	rm -rf venv/
	rm dist/*

install: clean
	virtualenv --python=`which python2.7` venv
	./venv/bin/pip install ".[dev,build]"
	virtualenv --python=`which python3.5` venv3
	./venv3/bin/pip install ".[dev,build]"

dist: install
	venv/bin/python setup.py build
	venv/bin/python setup.py bdist_wheel
	venv3/bin/python setup.py build
	venv3/bin/python setup.py sdist
	venv3/bin/python setup.py bdist_wheel
	venv3/bin/twine upload dist/*
