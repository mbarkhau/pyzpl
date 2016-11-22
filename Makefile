
clean:
	rm -rf venv3/
	rm -rf venv/

install: clean
	virtualenv --python=`which python3.5` venv3
	./venv3/bin/python setup.py install
	virtualenv --python=`which python2.7` venv
	./venv/bin/python setup.py install

dist: install
	venv3/bin/python setup.py build
	venv3/bin/python setup.py sdist upload
	venv3/bin/python setup.py bdist_wheel upload
