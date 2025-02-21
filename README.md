[![License](http://img.shields.io/:license-apache%202.0-brightgreen.svg)](http://www.apache.org/licenses/LICENSE-2.0.html)
![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)
[![Create Pypi Release](https://github.com/memiiso/pyliquibase/actions/workflows/release.yml/badge.svg)](https://github.com/memiiso/pyliquibase/actions/workflows/release.yml)
# pyliquibase

A Python module to use [liquibase](http://www.liquibase.org/) in python, using the Java Native Interface (JNI).

For further details on python-java integration [please see here](#python-java-integration)

## Installation
Python-Java integration requires a Java Development Kit (JDK). Ensure a JDK is installed on your operating system.

install:
```shell
pip install pyliquibase
```

## How to Use

using command line:
```shell
pyliquibase --defaultsFile=changelogs/liquibase.properties status
pyliquibase --defaultsFile=changelogs/liquibase.properties validate
pyliquibase --defaultsFile=changelogs/liquibase.properties updateSQL
pyliquibase --defaultsFile=changelogs/liquibase.properties update
```

using python:
```python
from pyliquibase import Pyliquibase

if __name__ == '__main__':
    liquibase = Pyliquibase(defaultsFile="changelogs/liquibase.properties", logLevel="INFO")
    # call execute with arguments
    liquibase.execute("status")
    liquibase.execute("rollback", "MyTag")
    # or 
    liquibase.validate()
    liquibase.status()
    liquibase.updateSQL()
    liquibase.update()
    liquibase.update_to_tag("MyTag")
    liquibase.rollback("MyTag")
    # liquibase maintenance commands
    liquibase.changelog_sync()
    liquibase.changelog_sync_to_tag("MyTag")
    liquibase.clear_checksums()
    liquibase.release_locks()
```

## Python Java Integration

This Python library integrates with Java using the `LiquibaseCommandLine` class.  Our Python `LiquibaseCommandLine` class acts as a reflection of the Java counterpart, passing Liquibase calls to the Java `LiquibaseCommandLine.execute(liquibaseargs)` method.

This integration leverages [Pyjnius](https://github.com/kivy/pyjnius), a Python library for accessing Java classes. Pyjnius either starts a new Java Virtual Machine (JVM) within the current process or connects to an existing JVM.  For more information on Pyjnius, please refer to their documentation: https://pyjnius.readthedocs.io/en/latest/.

```python
class LiquibaseCommandLine(JavaClass, metaclass=MetaJavaClass):
    __javaclass__ = 'liquibase/integration/commandline/LiquibaseCommandLine'
    # methods
    execute = JavaMethod('([Ljava/lang/String;)I')
```

### Contributors
<a href="https://github.com/memiiso/pyliquibase/graphs/contributors">
  <img src="https://contributors-img.web.app/image?repo=memiiso/pyliquibase" />
</a>


##
LIQUIBASE is a registered trademark of [Liquibase](https://www.liquibase.com) , INC.
