#!/usr/bin/env bash

# build and test
python --version
pylint pyliquibase setup.py
python -m compileall -f pyliquibase setup.py
coverage report -m ./pyliquibase/*.py
coverage run --source=./tests/ -m unittest discover -s tests/
python setup.py -q install --user