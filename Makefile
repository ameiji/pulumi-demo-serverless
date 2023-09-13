.PHONY: clean-pyc clean-build docs clean build-backend build-frontend all preview destroy up up-final

define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

SRC_DIR = aws-serverless-app
FRONTEND_DIR = frontend-src

help:
	@echo "all - build frontend and backend code and run pulumi up"
	@echo "preview - run pulumi preview"
	@echo "destroy - clean provisioned cloud resources"
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "dist - package"
	@echo "install - install the package to the active Python's site-packages"


clean: clean-build clean-pyc clean-test
	rm -fr $(FRONTEND_DIR)/build

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

lint:
	pylint --exit-zero --disable=C0116,C0301,C0114,R1734,R1735,R0903,R0902,E1121,C0115,W0401,E0401 $(SRC_DIR)/*.py
	flake8 --ignore=E501 $(SRC_DIR)/*.py

test:
	python setup.py test

test-all:
	tox

coverage:
	coverage run --source python_boilerplate setup.py test
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs:
	rm -f docs/python_boilerplate.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ python_boilerplate
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: clean
	python setup.py sdist upload
	python setup.py bdist_wheel upload

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean
	python setup.py install


# Pulumi-related targets
stack-init:
	@echo "=> Init Pulumi stack"
	pushd $(SRC_DIR) ;\
	pulumi logout && pulumi login --local ;\
	pulumi stack init aws-serverless-app || true ;\
	pulumi stack select aws-serverless-app ;\
	cp Pulumi.stack_template.yaml Pulumi.aws-serverless-app.yaml ;\
	pulumi stack ls ;\
	popd
	@echo "=> Stack init finished. Make sure you have changed your stack config file Pulumi.aws-serverless-app.yaml:"
	@echo "=>     - Add your account id in the list (allowedAccountIds)"
	@echo "=>     - Add random suffix for the Cognito domain (cognitoDomain)"
	@echo "=>     - Uncomment if you need a boundaryPolicy"
	
build-backend:
	@echo "=> Building backend"
	pushd $(SRC_DIR) ;\
	./build-backend.sh ;\
	popd

build-frontend:
	@echo "=> Building frontend"
	pushd $(SRC_DIR) ;\
	./build-frontend.sh ;\
	popd

preview:
	pushd $(SRC_DIR) ;\
	pulumi preview ;\
	popd

up:
	pushd $(SRC_DIR) ;\
	pulumi up -y ;\
	popd

up-final:
	pushd $(SRC_DIR) ;\
	pulumi up -y ;\
	popd

destroy:
	pushd $(SRC_DIR) ;\
	pulumi destroy

all: clean build-backend up build-frontend up-final

