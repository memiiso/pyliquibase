import argparse
import logging
import os
import pathlib
import sys
import tempfile
import zipfile
from urllib import request
from urllib.error import HTTPError
from urllib.parse import urlparse

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

DEFAULT_LIQUIBASE_VERSION: str = "4.21.1"
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
        :param jdbcDriversDir: user provided jdbc drivers directory. all the jar files under this directory are loaded
        :param additionalClasspath: additional classpath to import java libraries and liquibase extensions
        """

        self.args = []
        if defaultsFile:
            if not pathlib.Path.cwd().joinpath(defaultsFile).is_file() and not pathlib.Path(defaultsFile).is_file():
                raise FileNotFoundError("defaultsFile not found! %s" % defaultsFile)

            self.args.append("--defaults-file=%s" % defaultsFile)

        if liquibaseHubMode:
            self.args.append("--hub-mode=%s" % liquibaseHubMode)

        if logLevel:
            self.args.append("--log-level=%s" % logLevel)

        self.additional_classpath: str = additionalClasspath

        # if liquibaseDir is provided then switch to user provided liquibase.
        if liquibaseDir:
            self.liquibase_dir: str = liquibaseDir.strip("/")
            self.version: str = "user-provided"
        else:
            self.version: str = version
            self.liquibase_dir: str = resource_filename(__package__, LIQUIBASE_DIR.format(self.version))

        # if jdbcDriversDir is provided then use user provided jdbc driver libraries
        if jdbcDriversDir:
            self.jdbc_drivers_dir: str = jdbcDriversDir.strip("/")
        else:
            self.jdbc_drivers_dir: str = resource_filename(__package__, "jdbc-drivers")

        self.liquibase_lib_dir: str = self.liquibase_dir + "/lib"
        self.liquibase_internal_dir: str = self.liquibase_dir + "/internal"
        self.liquibase_internal_lib_dir: str = self.liquibase_internal_dir + "/lib"

        # if liquibase directory not found download liquibase from Github and extract it under the directory
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
        log.warning("Current working dir is %s" % pathlib.Path.cwd())
        log.debug("Executing liquibase %s" % list(arguments))
        rc = self.cli.execute(self.args + list(arguments))
        if rc:
            raise RuntimeError("Liquibase execution failed with exit code:%s" % rc)

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
        """ If self.liquibase_dir not found it downloads liquibase from Github and extracts it under self.liquibase_dir
        :return: 
        """
        if os.path.exists(self.liquibase_dir):
            log.debug("Liquibase version %s found, skipping download..." % str(self.version))
        else:
            _file = LIQUIBASE_ZIP_FILE.format(self.version)
            log.warning("Downloading Liquibase version: %s ...", self.version)
            self._download_zipfile(url=LIQUIBASE_ZIP_URL.format(self.version, self.version),
                                   destination=self.liquibase_dir)

        self._download_liquibase_extension_libs()

    def _download_liquibase_extension_libs(self):
        for ext in LIQUIBASE_EXT_LIST:
            ext_version = "%s-%s" % (ext, self.version)
            ext_version2 = "v%s" % self.version
            ext_url = LIQUIBASE_EXT_URL.format(ext, ext_version, ext_version)
            ext_url2 = LIQUIBASE_EXT_URL.format(ext, ext_version2, ext_version)
            try:
                self.download_additional_java_library(url=ext_url, destination_dir=self.liquibase_lib_dir)
            except HTTPError as _:
                try:
                    self.download_additional_java_library(url=ext_url2, destination_dir=self.liquibase_lib_dir)
                except:  # pylint: disable=bare-except
                    log.warning("Failed to download Liquibase extension: %s", ext_version)

    def download_additional_java_library(self, url: str, destination_dir: str = None):
        """
        Downloads java library file from given url and saves to destination directory. If file already exists it skips the download.
        :param url: url to java library jar file, http:xyz.com/mylibrary.jar
        :param destination_dir: Optional, download destination. example: /mdirectory1/mydirectory2/libs/
        :return: None
        """
        _url = urlparse(url)
        lib_file_name = os.path.basename(_url.path)
        destination_dir = destination_dir if destination_dir else self.liquibase_lib_dir
        destination_file = "%s/%s" % (destination_dir, lib_file_name)
        if pathlib.Path(destination_file).exists():
            log.info("Java lib already available skipping download: %s", destination_file)
        else:
            log.info("Downloading java lib: %s to %s", url, destination_file)
            self._download_file(url=url, destination=destination_file)

    def _download_zipfile(self, url: str, destination: str) -> None:
        """downloads zip file from given url and extract to destination folder
        :param url: 
        :param destination: 
        :return: 
        """
        with tempfile.NamedTemporaryFile(suffix="_liquibase.zip") as tmpfile:
            log.info("Downloading %s to %s" % (url, destination))
            self._download_file(url, tmpfile.name)

            log.info("Extracting to %s" % (destination))
            with zipfile.ZipFile(tmpfile, 'r') as zip_ref:
                zip_ref.extractall(destination)

    def _download_file(self, url: str, destination: str) -> None:
        """downloads file from given url and saves to destination path
        :param url: url to file
        :param destination: destination path including filename
        :return: 
        """
        try:
            request.urlretrieve(url, destination)
        except Exception as e:
            log.error("Failed to download %s" % url)
            raise e


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
