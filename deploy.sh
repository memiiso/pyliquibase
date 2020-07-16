#!/usr/bin/env bash

# build and test
python3 --version
python3 -m pip install coverage pylint pytest
python3 -m compileall -f pyliquibase setup.py
python3 -m coverage report -m ./pyliquibase/*.py setup.py
python3 -m coverage run --source=./tests/ -m unittest discover -s tests/
python3 setup.py -q install --user
python3 -m pylint pyliquibase setup.py
