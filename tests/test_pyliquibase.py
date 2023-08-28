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
        self.TEST_LIQUIBASE_VERSION = os.getenv("TEST_LIQUIBASE_VERSION", pyliquibase.DEFAULT_LIQUIBASE_VERSION)

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
        print("Testing LIQUIBASE_VERSION %s" % self.TEST_LIQUIBASE_VERSION)
        self.tearDown()
        lb = Pyliquibase(version=self.TEST_LIQUIBASE_VERSION,
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
        # test re downloading succeeds
        lb.download_additional_java_library(url="https://github.com/liquibase/liquibase-snowflake/releases/download/liquibase-snowflake-4.11.0/liquibase-snowflake-4.11.0.jar")
        # download redshift jdbc
        lb.download_additional_java_library(url="https://repo1.maven.org/maven2/com/amazon/redshift/redshift-jdbc42/2.1.0.16/redshift-jdbc42-2.1.0.16.jar")
        # download snowflake jdbc
        lb.download_additional_java_library(url="https://repo1.maven.org/maven2/net/snowflake/snowflake-jdbc/3.13.33/snowflake-jdbc-3.13.33.jar")

    def test_download_additional_zip_library(self):
        lb = Pyliquibase(defaultsFile=os.path.dirname(os.path.realpath(__file__)) + "/resources/liquibase.properties")
        # download Bigquery jdbc
        lb.download_additional_java_library(
            url="https://storage.googleapis.com/simba-bq-release/jdbc/SimbaJDBCDriverforGoogleBigQuery42_1.3.3.1004.zip")
        # download Bigquery jdbc
        lb.download_additional_java_library(
            url="https://storage.googleapis.com/simba-bq-release/jdbc/SimbaJDBCDriverforGoogleBigQuery42_1.3.3.1004.zip")
