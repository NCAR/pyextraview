PIP := $(shell command -v pip3 2> /dev/null)
ifeq (, $(shell which pip3))
	@echo "Please specify path to python3 PIP"
endif

install:
	${PIP} install -r requirements.txt
	${PIP} install .
 
test:
	py.test tests

develop:
	${PIP} install --editable .

.PHONY: install test 
