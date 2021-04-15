import os
from setuptools import setup, find_packages

setup_py_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(setup_py_dir)

setup(
    name='pyliquibase',
    version='1.1.0',
    packages=find_packages(),
    author='Memiiso',
    description='Python liquibase Wrapper',
    url='https://github.com/memiiso/pyliquibase',
    download_url='https://github.com/memiiso/pyliquibase/archive/master.zip',
    include_package_data=True,
    test_suite='tests',
    install_requires=[],
    python_requires='>=3',
)
