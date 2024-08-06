import argparse
import logging
import os
import pathlib
import sys
import tempfile
import zipfile
from urllib import request

from pkg_resources import resource_filename

DEFAULT_LIQUIBASE_VERSION: str = "4.21.1"
LIQUIBASE_ZIP_URL: str = "https://github.com/liquibase/liquibase/releases/download/v{}/liquibase-{}.zip"
LIQUIBASE_DIR: str = "liquibase-{}"


class Pyliquibase():

    def __init__(self, defaultsFile: str = None,
                 liquibaseDir: str = None,
                 jdbcDriversDir: str = None,
                 additionalClasspath: str = None,
                 version: str = DEFAULT_LIQUIBASE_VERSION):
        """

        :param defaultsFile: pyliquibase defaults file
        :param liquibaseDir: user provided liquibase directory
        :param jdbcDriversDir: user provided jdbc drivers directory. all the jar files under this directory are loaded
        :param additionalClasspath: additional classpath to import java libraries and liquibase extensions
        """

        self._log = None
        # if liquibaseDir is provided then switch to user provided liquibase.
        self.version: str = version if version else DEFAULT_LIQUIBASE_VERSION
        self.liquibase_dir: str = liquibaseDir.rstrip("/") if liquibaseDir else resource_filename(__package__,
                                                                                                  LIQUIBASE_DIR.format(
                                                                                                      self.version))

        self.args = []
        if defaultsFile:
            if not pathlib.Path.cwd().joinpath(defaultsFile).is_file() and not pathlib.Path(defaultsFile).is_file():
                raise FileNotFoundError("defaultsFile not found! %s" % defaultsFile)

            self.args.append("--defaults-file=%s" % defaultsFile)

        self.additional_classpath: str = additionalClasspath.rstrip('/') if additionalClasspath else None
        # if jdbcDriversDir is provided then use user provided jdbc driver libraries
        self.jdbc_drivers_dir: str = jdbcDriversDir.rstrip("/") if jdbcDriversDir else None
        self.liquibase_lib_dir: str = self.liquibase_dir + "/lib"
        self.liquibase_internal_dir: str = self.liquibase_dir + "/internal"
        self.liquibase_internal_lib_dir: str = self.liquibase_internal_dir + "/lib"

        # if liquibase directory not found download liquibase from Github and extract it under the directory
        if os.path.exists(self.liquibase_dir) and any(pathlib.Path(self.liquibase_dir).iterdir()):
            self.log.debug("Liquibase %s found" % str(self.liquibase_dir))
        else:
            self.log.warning("Downloading Liquibase version: %s ...", self.version)
            self.download_additional_java_library(url=LIQUIBASE_ZIP_URL.format(self.version, self.version),
                                                  destination_dir=self.liquibase_dir)

        self.cli = self._cli()

    @property
    def log(self):
        if not self._log:
            self._log = logging.getLogger("pyliquibase")
            self._log.setLevel(logging.INFO)
            if not self._log.hasHandlers():
                handler = logging.StreamHandler(sys.stdout)
                handler.setLevel(logging.INFO)
                formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                self._log.addHandler(handler)
        return self._log

    def _cli(self):
        ##### jnius
        import jnius_config

        LIQUIBASE_CLASSPATH: list = [
            self.liquibase_dir + "/*",
            self.liquibase_lib_dir + "/*",
            self.liquibase_internal_dir + "/*",
            self.liquibase_internal_lib_dir + "/*"]

        if self.jdbc_drivers_dir:
            LIQUIBASE_CLASSPATH.append(self.jdbc_drivers_dir + "/*")

        if self.additional_classpath:
            LIQUIBASE_CLASSPATH.append(self.additional_classpath + "/*")

        if not jnius_config.vm_running:
            jnius_config.add_classpath(*LIQUIBASE_CLASSPATH)
        else:
            self.log.warning(
                "VM is already running, can't set classpath/options! classpath: %s" % jnius_config.get_classpath())

        self.log.debug("classpath: %s" % jnius_config.get_classpath())

        from jnius import JavaClass, MetaJavaClass, JavaMethod
        #####
        class LiquibaseCommandLine(JavaClass, metaclass=MetaJavaClass):
            __javaclass__ = "liquibase/integration/commandline/LiquibaseCommandLine"

            # methods
            execute = JavaMethod("([Ljava/lang/String;)I")

        return LiquibaseCommandLine()

    def execute(self, *arguments: str):
        self.log.warning("Current working dir is %s" % pathlib.Path.cwd())
        self.log.debug("Executing liquibase %s" % list(arguments))
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
        self.log.debug("Updating to tag: %s" % tag)
        self.execute("update-to-tag", tag)

    def validate(self):
        self.execute("validate")

    def status(self):
        self.execute("status")

    def rollback(self, tag):
        self.log.debug("Rolling back to tag:%s" % tag)
        self.execute("rollback", tag)

    def rollback_to_datetime(self, datetime):
        self.log.debug("Rolling back to %s" % str(datetime))
        self.execute("rollbackToDate", datetime)

    def changelog_sync(self):
        """Executes the changelog-sync Liquibase maintenance command. `Reference Documentation <https://docs.liquibase.com/commands/maintenance/changelog-sync.html>`_.
        """
        self.log.debug("Marking all undeployed changes as executed in database.")
        self.execute("changelog-sync")

    def changelog_sync_to_tag(self, tag: str):
        """Executes the changelog-sync-to-tag Liquibase maintenance command. `Reference Documentation <https://docs.liquibase.com/commands/maintenance/changelog-sync-to-tag.html>`_.

        param: tag: Name of a tag in the changelog.
        """
        self.log.debug("Marking all undeployed changes as executed up to tag %s in database." % tag)
        self.execute("changelog-sync-to-tag", tag)

    def clear_checksums(self):
        """Executes the clear-checksums Liquibase maintenance command. `Reference Documentation <https://docs.liquibase.com/commands/maintenance/clear-checksums.html>`_.
        """
        self.log.debug("Marking all undeployed changes as executed in database.")
        self.execute("clear-checksums")

    def release_locks(self):
        """Executes the release-locks Liquibase maintenance command. `Reference Documentation <https://docs.liquibase.com/commands/maintenance/release-locks.html>`_.
        """
        self.log.debug("Marking all undeployed changes as executed in database.")
        self.execute("release-locks")

    def download_additional_java_library(self, url: str, destination_dir: str = None, override=False):
        """
        Downloads java library file from given url and saves to destination directory. If file already exists it skips the download.
        :param url: url to java library {jar,zip} file, http:xyz.com/mylibrary.jar, http:xyz.com/mylibrary.zip
        :param destination_dir: Optional, download destination. example: /mdirectory1/mydirectory2/libs/
        :return: None
        """
        file_name: str = os.path.basename(url)
        destination_dir = destination_dir if destination_dir else self.liquibase_lib_dir
        destination_file = pathlib.Path(destination_dir).joinpath(file_name)

        if override is False and destination_file.exists():
            self.log.info("File already available skipping download: %s", destination_file.as_posix())
            return

        if destination_file.suffix.lower().endswith('.zip'):
            self._download_zipfile(url=url,
                                   destination=destination_file.parent.as_posix(),
                                   file_name=destination_file.as_posix())

        elif destination_file.suffix.lower().endswith('.jar'):
            self.log.info("Downloading file: %s to %s", url, destination_file.as_posix())
            self._download_file(url=url,
                                destination=destination_file.as_posix())
        else:
            raise RuntimeError("Unexpected url, Expecting link to a `**.jar` or `**.zip` file!")

    def _download_zipfile(self, url: str, destination: str, file_name: str) -> None:
        """downloads zip file from given url and extract to destination folder
        :param url:
        :param destination:
        :return:
        """
        zipfile_dest = pathlib.Path(destination).joinpath(file_name)
        with tempfile.NamedTemporaryFile(suffix="_liquibase.zip", delete=False) as tmpfile:
            self.log.info("Downloading %s to %s" % (url, destination))
            self._download_file(url, tmpfile.name)

            self.log.info("Extracting to %s" % (destination))
            with zipfile.ZipFile(tmpfile, 'r') as zip_ref:
                zip_ref.extractall(destination)
        os.replace(src=tmpfile.name, dst=zipfile_dest)

    def _download_file(self, url: str, destination: str) -> None:
        """downloads file from given url and saves to destination path
        :param url: url to file
        :param destination: destination path including filename
        :return: 
        """
        try:
            request.urlretrieve(url, destination)
        except Exception as e:
            self.log.error("Failed to download %s" % url)
            raise e


def main():
    parser = argparse.ArgumentParser()
    _args, args = parser.parse_known_args()

    pl = Pyliquibase()
    pl.execute(*args)


if __name__ == '__main__':
    main()
