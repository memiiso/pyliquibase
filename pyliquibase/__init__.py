#! /usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
import logging
import os
import pathlib
import shlex
import subprocess
import sys

from pkg_resources import resource_filename

logger = logging.getLogger(name="pyliquibase")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Liquibase(object):

    def __init__(self, changeLogFile, username, password, url, driver, **kwargs):

        """
        :param changeLogFile=<path and filename> <required>	The changelog file to use.
        :param username=<value> <required>	Database username.
        :param password=<value> <required>	Database password.
        :param url=<value> <required>	Database JDBC URL.
        :param driver=<jdbc.driver.Class> <required>

        :param referenceDriver: oracle.jdbc.OracleDriver
        :param referenceUrl: jdbc:oracle:thin:@192.168.0.22:1521/orcl
        :param referencePassword: password
        :param liquibaseProLicenseKey: aeioufakekey32aeioufakekey785463214
        :param classpath: ../path/to/file/ojdbc6-11.2.0.3.0.jar
        :param defaultSchemaName=<schema>
        :param defaultsFile=</path/to/file>
        """

        self.changeLogFile = changeLogFile
        self.username = username
        self.password = password
        self.url = url
        self.driver = driver
        self.params = kwargs

    @property
    def _liquibase_cmd(self):
        cp = "%s:%s:%s" % (resource_filename(__package__, "liquibase/liquibase.jar"),
                           resource_filename(__package__, "liquibase/lib/*"),
                           resource_filename(__package__, "jdbc-drivers/*"))
        if "classpath" in self.params:
            cp = "%s:%s" % (cp, self.params["classpath"])

        cmd = "java -cp '%s' liquibase.integration.commandline.Main" % cp
        cmd = '%s --driver=%s' % (cmd, self.driver)
        cmd = '%s --url=%s' % (cmd, self.url)
        cmd = '%s --username=%s' % (cmd, self.username)
        cmd = '%s --password=%s' % (cmd, self.password)
        cmd = '%s --changeLogFile=%s' % (cmd, self.changeLogFile)

        for key, value in self.params.items():
            if key.startswith("-D") or key.startswith("--"):
                cmd = '%s %s=%s' % (cmd, key, value)
            else:
                cmd = '%s --%s=%s' % (cmd, key, value)

        return cmd

    def _execute(self, *args):
        command = "%s %s" % (self._liquibase_cmd, " ".join(args))
        logger.debug(command)
        output = ''
        with subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   universal_newlines=True,
                                   # FIx "Cannot find base path"
                                   cwd=os.path.dirname(self.changeLogFile)
                                   ) as process:
            logger.info("Liquibase command started with PID:%s" % process.pid)
            while True:
                line = process.stdout.readline()
                output += "%s\n" % (line.strip())
                logger.info(line.strip())
                if not line:
                    break
            rc = process.wait()
            if rc != 0:
                raise Exception("Liquibase command failed (Process: %s)\n return code: %s" % (
                    str(process.pid), str(rc)))
        return output


class Pyliquibase(Liquibase):

    @classmethod
    def from_file(cls, defaultsFile):
        properties = configparser.ConfigParser()
        properties.optionxform = str
        _string = "[%s]\n%s" % (properties.default_section, pathlib.Path(os.path.expanduser(defaultsFile)).read_text())
        properties.read_string(string=_string)
        return cls(**dict(properties.items(section=properties.default_section)))

    def update(self):
        logger.info("Executing liquibase update")
        return self._execute("update")

    def updateSQL(self):
        logger.info("Executing liquibase updateSQL")
        return self._execute("updateSQL")

    def validate(self):
        logger.info("Executing liquibase validate")
        return self._execute("validate")

    def status(self):
        logger.info("Executing liquibase status")
        return self._execute("status")

    def rollback(self, tag):
        logger.info("Rolling back to tag:%s" % tag)
        return self._execute("rollback", tag)

    def rollback_to_datetime(self, datetime):
        logger.info("Rolling back to %s" % str(datetime))
        return self._execute("rollbackToDate", datetime)
