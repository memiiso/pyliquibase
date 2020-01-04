#!/usr/bin/env bash

# build and test
python --version
pip -q install -r requirements.txt
pylint pprobi setup.py deploy.py
python -m compileall -f pprobi setup.py deploy.py
coverage report -m ./pprobi/*.py ./pprobi/*/*.py ./pprobi/*/*/*.py
coverage run --source=./tests/ -m unittest discover -s tests/

# python setup.py -q install --user