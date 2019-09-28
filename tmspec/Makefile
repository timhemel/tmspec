
.PHONY: test

compiler: tmspecVisitor.py

tmspecVisitor.py: tmspec.g4
	sh build.sh

test:
	python3 -m unittest discover -v -p test_\*.py test

