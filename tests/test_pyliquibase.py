import os
from unittest import TestCase

from pyliquibase import Pyliquibase


class TestPyliquibase(TestCase):
    def setUp(self):
        self.testdb = os.path.dirname(os.path.realpath(__file__)) + 'testdb'

    def tearDown(self):
        self.tearDowndb()

    def tearDowndb(self):
        if os.path.exists(self.testdb):
            os.remove(self.testdb)

    def test_update(self):
        self.tearDowndb()
        changeLogFile = os.path.dirname(os.path.realpath(__file__)) + '/resources/changelog.xml'
        lb = Pyliquibase(changeLogFile=changeLogFile, username="", password="", url='jdbc:sqlite:%s' % self.testdb,
                         driver="org.sqlite.JDBC", logLevel="info")

        rc = lb.status()
        self.assertTrue("2 change sets have not been applied" in rc)
        rc = lb.validate()
        self.assertTrue("No validation errors found" in rc)
        rc = lb.update()
        self.assertTrue("001_patch.sql" in rc)
        self.assertTrue("Custom SQL executed" in rc)
        rc = lb.update()
        self.assertTrue("Liquibase: Update has been successful" in rc)

    def test_nested_dir(self):
        self.tearDowndb()
        changeLogFile = os.path.dirname(os.path.realpath(__file__)) + '/resources/changelog-2.xml'
        lb = Pyliquibase(changeLogFile=changeLogFile, username="", password="", url='jdbc:sqlite:%s' % self.testdb,
                         driver="org.sqlite.JDBC", logLevel="info")

        rc = lb.status()
        self.assertTrue("2 change sets have not been applied" in rc)
        rc = lb.validate()
        self.assertTrue("No validation errors found" in rc)
        rc = lb.update()
        self.assertTrue("001_patch.sql" in rc)
        self.assertTrue("Custom SQL executed" in rc)
        rc = lb.update()
        self.assertTrue("Liquibase: Update has been successful" in rc)

    def test_from_defaults_file(self):
        changeLogFile = os.path.dirname(os.path.realpath(__file__)) + '/resources/changelog-2.xml'
        lb = Pyliquibase.from_file(defaultsFile="./resources/liquibase.properties")
        lb.changeLogFile = changeLogFile
        rc = lb.status()
        self.assertTrue("2 change sets have not been applied" in rc)
        rc = lb.validate()
        self.assertTrue("No validation errors found" in rc)
        rc = lb.update()
        self.assertTrue("001_patch.sql" in rc)
        self.assertTrue("Custom SQL executed" in rc)
        rc = lb.update()
        self.assertTrue("Liquibase: Update has been successful" in rc)
