![Python package](https://github.com/memiiso/pyliquibase/workflows/Python%20package/badge.svg)

# pyliquibase

Use [liquibase](http://www.liquibase.org/) with python. Java integration is done using Java Native Interface (JNI) using [pyjnius](https://github.com/kivy/pyjnius)

MySQL, Postgresql, Bigquery, Redshift JDBC Drivers included.

## Installation

install:
```shell
pip install pyliquibase
```

install from github:
```shell
pip install https://github.com/memiiso/pyliquibase/archive/master.zip --upgrade --user
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
    liquibase.rollback("MyTag")
```

## Python Java Integration
Python library is using `LiquibaseCommandLine` reflection class which uses/equivalent `LiquibaseCommandLine` java class.
liquibase calls are executed by `LiquibaseCommandLine.execute(liquibaseargs)` method by passing given python arguments to java class.

python java integration class using pyjnius(using the Java Native Interface (JNI))
```python
class LiquibaseCommandLine(JavaClass, metaclass=MetaJavaClass):
    __javaclass__ = 'liquibase/integration/commandline/LiquibaseCommandLine'
    # methods
    execute = JavaMethod('([Ljava/lang/String;)I')
```

LIQUIBASE is a registered trademark of [Liquibase](https://www.liquibase.com) , INC.