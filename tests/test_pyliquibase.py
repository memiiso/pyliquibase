import os
import pathlib
from unittest import TestCase

import pyliquibase
from pyliquibase import Pyliquibase


class TestPyliquibase(TestCase):
    def setUp(self):
        self.dir_test = pathlib.Path(__file__).parent
        self.testdb = self.dir_test.as_posix() + 'testdb'
        self.testlogfile = self.dir_test.joinpath('liquibase.log')
        os.chdir(self.dir_test.as_posix())

    def tearDown(self):
        if os.path.exists(self.testdb):
            os.remove(self.testdb)

        self._delete_testlogfile()

    def _get_liquibase_log(self) -> str:
        return self.testlogfile.read_text()

    def _delete_testlogfile(self):
        if self.testlogfile.exists():
            self.testlogfile.unlink()

    def test_update(self):
        versions = ["4.9.0", "4.10.0", "4.11.0", pyliquibase.DEFAULT_LIQUIBASE_VERSION]
        for version in versions:
            self.tearDown()
            lb = Pyliquibase(version=version,
                             defaultsFile=os.path.dirname(
                                 os.path.realpath(__file__)) + "/resources/liquibase.properties")

            lb.addarg("--log-level", "info")
            lb.addarg("--log-file", self.testlogfile.as_posix())

            lb.status()
            lb.execute("validate")
            lb.execute("updateSQL")
            lb.execute("update")
            self.assertTrue(True)

    def test_exception(self):
        lb = Pyliquibase(
            defaultsFile=os.path.dirname(os.path.realpath(__file__)) + "/resources/liquibase-fail.properties")
        try:
            lb.status()
        except Exception as e:
            self.assertTrue("Liquibase execution failed" in str(e))

    def test_download_additional_java_library(self):
        lb = Pyliquibase(defaultsFile=os.path.dirname(os.path.realpath(__file__)) + "/resources/liquibase.properties")
        lb.download_additional_java_library(url="https://github.com/liquibase/liquibase-snowflake/releases/download/liquibase-snowflake-4.11.0/liquibase-snowflake-4.11.0.jar")
        lb.download_additional_java_library(url="https://github.com/liquibase/liquibase-snowflake/releases/download/liquibase-snowflake-4.11.0/liquibase-snowflake-4.11.0.jar")
