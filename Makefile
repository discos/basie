.PHONY: test
SOURCES=setup.py scripts src/*.py src/user_templates/* src/schemas/* src/scanmode/*.py src/configobj/*.py
TESTS=test/*.py
PYTHON=python
EPYDOC=epydoc
#INSTALL=easy_install
INSTALL=pip install

all: dep install

dep:
	$(INSTALL) -r requirements.txt

install: $(SOURCES)
	$(PYTHON) setup.py install

doc: doc/epydoc.conf $(SOURCES)
	cd doc; $(EPYDOC) --conf=epydoc.conf

clean:
	rm -rf build src/*.pyc test/*.pyc doc/html/*

test:
	python -m unittest discover -v test/
