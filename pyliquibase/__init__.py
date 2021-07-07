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

    def __init__(self, changeLogFile=None, username=None, password=None, url=None, driver=None, logLevel=None,
                 defaultsFile=None,
                 liquibaseHubMode="off", **kwargs):

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

        if defaultsFile is None and (
                changeLogFile is None or username is None or password is None or url is None or driver is None):
            raise Exception("Please provide defaultsFile or {changeLogFile, username, password, url, driver} arguments")

        self.liquibaseHubMode = liquibaseHubMode
        self.changeLogFile = changeLogFile
        self.username = username
        self.password = password
        self.url = url
        self.driver = driver
        self.params = kwargs
        self.logLevel = logLevel
        self.defaultsFile = defaultsFile

    @property
    def _liquibase_cmd(self) -> list:
        command = []
        logger.info("Working dir is %s" % os.getcwd())
        cp = "%s:%s:%s:%s" % (os.getcwd()+"/",
                              resource_filename(__package__, "liquibase/liquibase.jar"),
                              resource_filename(__package__, "liquibase/lib/*"),
                              resource_filename(__package__, "jdbc-drivers/*"))
        if "classpath" in self.params:
            cp = "%s:%s" % (cp, self.params["classpath"])

        command.append("java")
        command.append("-cp")
        command.append(cp)
        command.append("liquibase.integration.commandline.LiquibaseCommandLine")

        if self.defaultsFile:
            command.append('%s=%s' % ("--defaultsFile", self.defaultsFile))
            command.append('--liquibaseHubMode=%s' % (self.liquibaseHubMode))
            return command

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
        command.append('--liquibaseHubMode=%s' % (self.liquibaseHubMode))

        return command

    def _execute(self, *args) -> str:
        _output = ""
        command = self._liquibase_cmd + list(args)
        logger.debug(command)
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1,
                              universal_newlines=True, shell=False) as p:
            for line in p.stdout:
                if line:
                    print(line.strip())
                    _output += line.strip() + "\n"

        if p.returncode != 0:
            _args = []
            # remove password
            for x in p.args:
                if "--password" in str(x):
                    _args.append("--password=***")
                else:
                    _args.append(x)
            raise subprocess.CalledProcessError(p.returncode, p.args, output=_output, stderr=p.stderr)

        return _output


class Pyliquibase(Liquibase):

    @classmethod
    def from_file(cls, defaultsFile):
        properties = configparser.ConfigParser()
        properties.optionxform = str
        _string = "[%s]\n%s" % (properties.default_section, pathlib.Path(os.path.expanduser(defaultsFile)).read_text())
        properties.read_string(string=_string)
        return cls(
            changeLogFile=properties.get(properties.default_section, "changeLogFile"),
            username=properties.get(properties.default_section, "username"),
            password=properties.get(properties.default_section, "password"),
            url=properties.get(properties.default_section, "url"),
            driver=properties.get(properties.default_section, "driver"),
            logLevel=properties.get(properties.default_section, "logLevel", fallback=None),
            liquibaseHubMode=properties.get(properties.default_section, "liquibaseHubMode", fallback="off"),
            defaultsFile=defaultsFile)

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
