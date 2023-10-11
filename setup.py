import os
import pathlib

from setuptools import setup, find_packages

setup_py_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(setup_py_dir)

setup(
    name='pyliquibase',
    entry_points={
        'console_scripts': [
            'pyliquibase = pyliquibase:main',
        ],
    },
    version='2.1.0',
    packages=find_packages(),
    author="Memiiso Organization",
    description='Python liquibase',
    long_description=pathlib.Path(__file__).parent.joinpath("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url='https://github.com/memiiso/pyliquibase',
    download_url='https://github.com/memiiso/pyliquibase/archive/master.zip',
    include_package_data=True,
    license="Apache License 2.0",
    test_suite='tests',
    install_requires=["pyjnius~=1.6.0"],
    python_requires='>=3.8',
)
