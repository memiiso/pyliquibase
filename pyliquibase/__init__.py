#! /usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
import logging
import os
import pathlib
import subprocess
import sys

from pkg_resources import resource_filename

logger = logging.getLogger(name="pyliquibase")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Liquibase(object):

    def __init__(self, changeLogFile, username, password, url, driver, logLevel=None, **kwargs):

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
        self.logLevel = logLevel

    @property
    def _liquibase_cmd(self) -> list:
        command = []
        cp = "%s:%s:%s" % (resource_filename(__package__, "liquibase/liquibase.jar"),
                           resource_filename(__package__, "liquibase/lib/*"),
                           resource_filename(__package__, "jdbc-drivers/*"))
        if "classpath" in self.params:
            cp = "%s:%s" % (cp, self.params["classpath"])

        cp = "%s:%s" % (cp, "/")

        command.append("java")
        command.append("-cp")
        command.append(cp)
        command.append("liquibase.integration.commandline.Main")

        for key, value in self.params.items():
            if key.startswith("-D") or key.startswith("--"):
                command.append('%s=%s' % (key, value))
            else:
                command.append('--%s=%s' % (key, value))

        command.append('--driver=%s' % (self.driver))
        if self.logLevel:
            command.append('--logLevel=%s' % (self.logLevel))
        command.append('--url=%s' % (self.url))
        command.append('--username=%s' % (self.username))
        command.append('--password=%s' % (self.password))
        command.append('--changeLogFile=%s' % (self.changeLogFile))

        return command

    def _execute(self, *args) -> str:
        _output = ""
        command = self._liquibase_cmd + list(args)
        logger.debug(command)
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              universal_newlines=True,
                              # FIx "Cannot find base path"
                              cwd=os.path.dirname(self.changeLogFile)
                              ) as process:
            logger.debug("Liquibase command started with PID:%s" % process.pid)
            for line in process.stdout:
                if line:
                    logger.info(line.strip())
                    _output += line.strip() + "\n"

        if process.returncode != 0:
            _args = []
            # remove password
            for x in process.args:
                if "--password" in str(x):
                    _args.append("--password=***")
                else:
                    _args.append(x)
            raise subprocess.CalledProcessError(process.returncode, _args)

        return _output


class Pyliquibase(Liquibase):

    @classmethod
    def from_file(cls, defaultsFile):
        properties = configparser.ConfigParser()
        properties.optionxform = str
        _string = "[%s]\n%s" % (properties.default_section, pathlib.Path(os.path.expanduser(defaultsFile)).read_text())
        properties.read_string(string=_string)
        return cls(**dict(properties.items(section=properties.default_section)))

    def update(self):
        logger.debug("Executing liquibase update")
        return self._execute("update")

    def updateSQL(self):
        logger.debug("Executing liquibase updateSQL")
        return self._execute("updateSQL")

    def validate(self):
        logger.debug("Executing liquibase validate")
        return self._execute("validate")

    def status(self):
        logger.debug("Executing liquibase status")
        return self._execute("status")

    def rollback(self, tag):
        logger.debug("Rolling back to tag:%s" % tag)
        return self._execute("rollback", tag)

    def rollback_to_datetime(self, datetime):
        logger.debug("Rolling back to %s" % str(datetime))
        return self._execute("rollbackToDate", datetime)
