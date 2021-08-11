import os
import pathlib
from unittest import TestCase

from pyliquibase import Pyliquibase


class TestPyliquibase(TestCase):
    def setUp(self):
        self.dir_test = pathlib.Path(__file__).parent
        self.testdb = self.dir_test.as_posix() + 'testdb'
        os.chdir(self.dir_test.as_posix())

    def tearDown(self):
        self.tearDowndb()

    def tearDowndb(self):
        if os.path.exists(self.testdb):
            os.remove(self.testdb)

    def test_update(self):
        self.tearDowndb()
        changeLogFile = 'resources/changelog.xml'
        lb = Pyliquibase(changeLogFile=changeLogFile, username="", password="", url='jdbc:sqlite:%s' % self.testdb,
                         driver="org.sqlite.JDBC", logLevel="info")

        rc = lb.status()
        self.assertTrue("2 change sets have not been applied" in rc)
        rc = lb.validate()
        self.assertTrue("No validation errors found" in rc)
        rc = lb.updateSQL()
        self.assertTrue("001_patch.sql" in rc)
        rc = lb.update()
        self.assertTrue("Liquibase command 'update' was executed successfully" in rc)

    def test_nested_dir(self):
        self.tearDowndb()
        changeLogFile = 'resources/changelog-2.xml'
        lb = Pyliquibase(changeLogFile=changeLogFile, username="", password="", url='jdbc:sqlite:%s' % self.testdb,
                         driver="org.sqlite.JDBC", logLevel="info")

        rc = lb.status()
        self.assertTrue("2 change sets have not been applied" in rc)
        rc = lb.validate()
        self.assertTrue("No validation errors found" in rc)
        rc = lb.updateSQL()
        self.assertTrue("001_patch.sql" in rc)
        rc = lb.update()
        self.assertTrue("Liquibase command 'update' was executed successfully" in rc)

    def test_from_defaults_file(self):
        lb = Pyliquibase.from_file(
            defaultsFile=os.path.dirname(os.path.realpath(__file__)) + "/resources/liquibase.properties")
        rc = lb.status()
        self.assertTrue("2 change sets have not been applied" in rc)
        rc = lb.validate()
        self.assertTrue("No validation errors found" in rc)
        rc = lb.updateSQL()
        self.assertTrue("001_patch.sql" in rc)
        rc = lb.update()
        self.assertTrue("ChangeSet resources/changelog-2/002_patch.sql::1::liqubasetest ran successfully" in rc)

    def test_exception(self):
        changeLogFile = 'resources/changelog-2.xml'
        lb = Pyliquibase(changeLogFile=changeLogFile, username="", password="", url='jdbc:mysql:notexists',
                         driver="org.sqlite.JDBC", logLevel="info")
        lb.changeLogFile = changeLogFile
        try:
            rc = lb.status()
        except Exception as e:
            self.assertTrue("Connection could not be created to" in str(e.stdout))
