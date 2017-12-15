install:
	pip install -r requirements.txt
	pip install .
 
test:
	py.test tests

develop:
	pip install --editable .

.PHONY: install test 
