.PHONY: test
SOURCES=setup.py scripts basie/*.py basie/user_templates/* basie/schemas/* basie/scanmode/*.py basie/configobj/*.py
TESTS=test/*.py
PYTHON=python
EPYDOC=epydoc
#INSTALL=easy_install
INSTALL=pip install

all: dep install

dep:
	$(INSTALL) -r requirements.txt

install: $(SOURCES)
	$(INSTALL) .

doc: doc/epydoc.conf $(SOURCES)
	cd doc; $(EPYDOC) --conf=epydoc.conf

clean:
	rm -rf build basie/*.pyc test/*.pyc doc/html/*

test:
	python -m unittest discover -v test/
