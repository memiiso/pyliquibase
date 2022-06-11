import argparse
import logging
import os
import pathlib
import sys
import tempfile
import zipfile
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

DEFAULT_LIQUIBASE_VERSION: str = "4.11.0"
LIQUIBASE_ZIP_URL: str = "https://github.com/liquibase/liquibase/releases/download/v{}/liquibase-{}.zip"
LIQUIBASE_ZIP_FILE: str = "liquibase-{}.zip"
LIQUIBASE_DIR: str = "liquibase-{}"
LIQUIBASE_EXT_LIST: list = ["liquibase-bigquery", "liquibase-redshift", "liquibase-snowflake"]
LIQUIBASE_EXT_URL: str = "https://github.com/liquibase/{}/releases/download/{}/{}.jar"


class Pyliquibase():

    def __init__(self, defaultsFile: str,
                 liquibaseHubMode: str = "off",
                 logLevel: str = None,
                 liquibaseDir: str = None,
                 jdbcDriversDir: str = None,
                 additionalClasspath: str = None,
                 version: str = DEFAULT_LIQUIBASE_VERSION):
        """

        :param defaultsFile: pyliquibase defaults file
        :param liquibaseHubMode: liquibase Hub Mode default: off
        :param logLevel: liquibase log level
        :param liquibaseDir: user provided liquibase directory
        :param jdbcDriversDir: user provided jdbc drivers directory.all the jar files under this directory are loaded
        :param additionalClasspath: additional classpath to import java libraries and liquibase extensions
        """

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

        # if liquibaseDir is provided by user then switch to user provided libraries.
        if liquibaseDir:
            self.liquibase_dir: str = liquibaseDir.strip("/")
            self.jdbc_drivers_dir: str = jdbcDriversDir.strip("/") if jdbcDriversDir else None
            self.version: str = "user-provided"
        else:
            self.version: str = version
            self.liquibase_dir: str = resource_filename(__package__, LIQUIBASE_DIR.format(self.version))
            self.jdbc_drivers_dir: str = resource_filename(__package__, "jdbc-drivers")

        self.liquibase_lib_dir: str = self.liquibase_dir + "/lib"
        self.liquibase_internal_dir: str = self.liquibase_dir + "/internal"
        self.liquibase_internal_lib_dir: str = self.liquibase_internal_dir + "/lib"

        if not liquibaseDir:
            self._download_liquibase()

        self.cli = self._cli()

    def _cli(self):
        ##### jnius
        import jnius_config

        LIQUIBASE_CLASSPATH: list = [
            self.liquibase_dir + "/liquibase.jar",
            self.liquibase_lib_dir + "/*",
            self.liquibase_internal_dir + "/*",
            self.liquibase_internal_lib_dir + "/*",
            self.jdbc_drivers_dir + "/*"]

        if self.additional_classpath:
            LIQUIBASE_CLASSPATH.append(self.additional_classpath)

        if not jnius_config.vm_running:
            jnius_config.add_classpath(*LIQUIBASE_CLASSPATH)
        else:
            log.warning("VM is already running, can't set classpath/options")

        log.debug("classpath: %s" % jnius_config.get_classpath())

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

    def update_to_tag(self, tag: str):
        """Executes the update-to-tag Liquibase command. `Reference Documentation <https://docs.liquibase.com/commands/update/update-to-tag.html>`_.

        param: tag: Name of a tag in the changelog.
        """
        log.debug("Updating to tag: %s" % tag)
        self.execute("update-to-tag", tag)

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

    def changelog_sync(self):
        """Executes the changelog-sync Liquibase maintenance command. `Reference Documentation <https://docs.liquibase.com/commands/maintenance/changelog-sync.html>`_.
        """
        log.debug("Marking all undeployed changes as executed in database.")
        self.execute("changelog-sync")

    def changelog_sync_to_tag(self, tag: str):
        """Executes the changelog-sync-to-tag Liquibase maintenance command. `Reference Documentation <https://docs.liquibase.com/commands/maintenance/changelog-sync-to-tag.html>`_.

        param: tag: Name of a tag in the changelog.
        """
        log.debug("Marking all undeployed changes as executed up to tag %s in database." % tag)
        self.execute("changelog-sync-to-tag", tag)

    def clear_checksums(self):
        """Executes the clear-checksums Liquibase maintenance command. `Reference Documentation <https://docs.liquibase.com/commands/maintenance/clear-checksums.html>`_.
        """
        log.debug("Marking all undeployed changes as executed in database.")
        self.execute("clear-checksums")

    def release_locks(self):
        """Executes the release-locks Liquibase maintenance command. `Reference Documentation <https://docs.liquibase.com/commands/maintenance/release-locks.html>`_.
        """
        log.debug("Marking all undeployed changes as executed in database.")
        self.execute("release-locks")

    def _download_liquibase(self) -> None:
        if os.path.exists(self.liquibase_dir):
            log.debug("Liquibase version %s found, skipping download..." % str(self.version))
        else:
            _file = LIQUIBASE_ZIP_FILE.format(self.version)
            log.warning("Downloading Liquibase version: %s ...", self.version)
            self._download_zipfile(url=LIQUIBASE_ZIP_URL.format(self.version, self.version),
                                   destination=self.liquibase_dir)

        for ext in LIQUIBASE_EXT_LIST:
            ext_version = "%s-%s" % (ext, self.version)
            ext_destination = "%s/%s.jar" % (self.liquibase_lib_dir, ext_version)
            ext_url = LIQUIBASE_EXT_URL.format(ext, ext_version, ext_version)
            if not os.path.exists(ext_destination):
                log.warning("Downloading Liquibase extension: %s ...", ext_version)
                self._download_file(url=ext_url, destination=ext_destination)

    def _download_zipfile(self, url: str, destination: str) -> None:
        with tempfile.NamedTemporaryFile(suffix="_liquibase.zip") as tmpfile:
            self._download_file(url, tmpfile.name)

            log.info("Extracting to %s" % (destination))
            with zipfile.ZipFile(tmpfile, 'r') as zip_ref:
                zip_ref.extractall(destination)

    def _download_file(self, url: str, destination: str) -> None:
        log.info("Downloading %s to %s" % (url, destination))
        request.urlretrieve(url, destination)


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
