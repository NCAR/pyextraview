init:
	pip install -r requirements.txt

test:
	py.test tests

develop:
	pip install --editable .

.PHONY: init test
