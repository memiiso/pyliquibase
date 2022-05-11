import argparse
import logging
import os
import pathlib
import sys
import zipfile
from typing import List
from urllib import request

from pkg_resources import resource_filename

#####  loggger
log = logging.getLogger(name="pyliquibase")
log.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

#####

LAST_STABLE_KNOWN_LB_VERSION: str = "4.6.2"
COMPATIBLE_LIQUIBASE_VERSIONS: List = ["4.6.1", "4.6.2"]
URL_LIQUIBASE_ZIP: str = "https://github.com/liquibase/liquibase/releases/download/v{}/liquibase-{}.zip"
URL_LIQUIBASE_RELEASES: str = "https://api.github.com/repos/liquibase/liquibase/releases"
LIQUIBASE_ZIP_NAME: str = "liquibase-{}.zip"
LIQUIBASE_PATH_TO_EXTRACT: str = "liquibase-{}"


class Pyliquibase():
    version: str = LAST_STABLE_KNOWN_LB_VERSION

    def __init__(self, defaultsFile: str,
                 liquibaseHubMode: str = "off",
                 logLevel: str = None,
                 liquibaseDir: str = None,
                 jdbcDriversDir: str = None,
                 additionalClasspath: str = None,
                 version: str = LAST_STABLE_KNOWN_LB_VERSION):
        """

        :param defaultsFile: pyliquibase defaults file
        :param liquibaseHubMode: liquibase Hub Mode default: off
        :param logLevel: liquibase log level
        :param liquibaseDir: user provided liquibase directory
        :param jdbcDriversDir: user provided jdbc drivers directory.all the jar files under this directory are loaded
        :param additionalClasspath: additional classpath to import java libraries and liquibase extensions
        """
        self._check_liquibase_version_exists(version)
        self._download_liquibase_version()

        self.args = []
        log.warning("Current working dir is %s" % pathlib.Path.cwd())
        if defaultsFile:
            if not pathlib.Path.cwd().joinpath(defaultsFile).is_file() and not pathlib.Path(defaultsFile).is_file():
                raise FileNotFoundError("defaultsFile not found! %s" % defaultsFile)

            self.args.append("--defaults-file=%s" % defaultsFile)

        if liquibaseHubMode:
            self.args.append("--hub-mode=%s" % liquibaseHubMode)

        if logLevel:
            self.args.append("--log-level=%s" % logLevel)

        self.additional_classpath: str = additionalClasspath

        if liquibaseDir:
            self.liquibase_dir: str = liquibaseDir.strip("/")
            self.jdbc_drivers_dir: str = jdbcDriversDir.strip("/") if jdbcDriversDir else None
        else:
            self.liquibase_dir: str = resource_filename(__package__, LIQUIBASE_PATH_TO_EXTRACT.format(self.version))
            self.jdbc_drivers_dir: str = resource_filename(__package__, "jdbc-drivers")

        self.cli = self._cli()

    def _cli(self):
        ##### jnius
        import jnius_config

        LIQUIBASE_CLASSPATH: list = [
            resource_filename(__package__, LIQUIBASE_PATH_TO_EXTRACT.format(self.version) + "/liquibase.jar"),
            resource_filename(__package__, LIQUIBASE_PATH_TO_EXTRACT.format(self.version) + "/lib/*"),
            resource_filename(__package__, LIQUIBASE_PATH_TO_EXTRACT.format(self.version) + "/lib/picocli*"),
            resource_filename(__package__, "jdbc-drivers/*")]

        if self.additional_classpath:
            LIQUIBASE_CLASSPATH.append(self.additional_classpath)

        if not jnius_config.vm_running:
            jnius_config.add_classpath(*LIQUIBASE_CLASSPATH)
            log.debug("classpath: %s" % jnius_config.get_classpath())
        else:
            log.warning("VM is already running, can't set classpath/options")
            log.debug("VM started at" + jnius_config.vm_started_at)

        from jnius import JavaClass, MetaJavaClass, JavaMethod
        #####
        class LiquibaseCommandLine(JavaClass, metaclass=MetaJavaClass):
            __javaclass__ = "liquibase/integration/commandline/LiquibaseCommandLine"

            # methods
            execute = JavaMethod("([Ljava/lang/String;)I")

        return LiquibaseCommandLine()

    def execute(self, *arguments: str):
        log.debug("Executing liquibase %s" % list(arguments))
        rc = self.cli.execute(self.args + list(arguments))
        if rc:
            raise Exception("Liquibase execution failed with exit code:%s" % rc)

    def addarg(self, key: str, val):
        _new_arg = "%s=%s" % (key, val)
        self.args.append(_new_arg)

    def update(self):
        self.execute("update")

    def updateSQL(self):
        self.execute("updateSQL")

    def validate(self):
        self.execute("validate")

    def status(self):
        self.execute("status")

    def rollback(self, tag):
        log.debug("Rolling back to tag:%s" % tag)
        self.execute("rollback", tag)

    def rollback_to_datetime(self, datetime):
        log.debug("Rolling back to %s" % str(datetime))
        self.execute("rollbackToDate", datetime)

    def _check_liquibase_version_exists(self, version: str) -> None:
        if version in COMPATIBLE_LIQUIBASE_VERSIONS:
            self.version = version
        else:
            self.version = LAST_STABLE_KNOWN_LB_VERSION
            log.warning("Version %s is not a valid version of Liquibase. "
                        "Using last stable known version %s" % (version, LAST_STABLE_KNOWN_LB_VERSION))

    def _download_liquibase_version(self) -> None:
        liquibase_path = os.path.join(os.path.dirname(__file__), LIQUIBASE_PATH_TO_EXTRACT.format(self.version))
        if os.path.exists(liquibase_path):
            log.warning("Liquibase version %s directory founded, skipping download..." % str(self.version))
            return
        with request.urlopen(URL_LIQUIBASE_ZIP.format(self.version, self.version)) as response, open(
                LIQUIBASE_ZIP_NAME.format(self.version), "wb") as file:
            file.write(response.read())

        with zipfile.ZipFile(LIQUIBASE_ZIP_NAME.format(self.version), 'r') as zip_ref:
            zip_ref.extractall(liquibase_path)

        os.remove(LIQUIBASE_ZIP_NAME.format(self.version))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--defaultsFile', type=str, default="liquibase.properties",
                        help='Relative path to liquibase.properties file'
                        )
    parser.add_argument('--liquibaseHubMode', type=str, default="off", help='liquibaseHubMode default "off"')
    parser.add_argument('--logLevel', type=str, default=None, help='logLevel name')
    _args, args = parser.parse_known_args()

    pl = Pyliquibase(defaultsFile=_args.defaultsFile,
                     liquibaseHubMode=_args.liquibaseHubMode,
                     logLevel=_args.logLevel)
    pl.execute(*args)


if __name__ == '__main__':
    main()
