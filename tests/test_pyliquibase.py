import os
import pathlib
from unittest import TestCase

from pyliquibase import Pyliquibase, COMPATIBLE_LIQUIBASE_VERSIONS, LAST_STABLE_KNOWN_LB_VERSION


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
        self.tearDown()
        lb = Pyliquibase(defaultsFile=os.path.dirname(os.path.realpath(__file__)) + "/resources/liquibase.properties")

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

    def test_valid_version(self):
        lb = Pyliquibase(
            defaultsFile=os.path.dirname(os.path.realpath(__file__)) + "/resources/liquibase-fail.properties",
            version=LAST_STABLE_KNOWN_LB_VERSION
        )
        self.assertTrue(lb.version in COMPATIBLE_LIQUIBASE_VERSIONS)

    def test_no_valid_version_set_last_stable_known_version(self):
        lb = Pyliquibase(
            defaultsFile=os.path.dirname(os.path.realpath(__file__)) + "/resources/liquibase-fail.properties",
            version="0.0.1"
        )
        self.assertTrue(lb.version == LAST_STABLE_KNOWN_LB_VERSION)
