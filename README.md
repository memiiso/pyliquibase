![Python package](https://github.com/memiiso/pyliquibase/workflows/Python%20package/badge.svg)

# pyliquibase

Python wrapper for [liquibase](http://www.liquibase.org/). 

## Installation

```python
pip install https://github.com/memiiso/pyliquibase/archive/master.zip --upgrade --user
```

## Usage

MySQL and Postgresql JDBC Drivers included.

##### MySQL

```python
from pyliquibase import Pyliquibase
if __name__ == '__main__':
    liquibase = Pyliquibase(
                    url="jdbc:mysql://localhost:3306/sakila",
                    driver="com.mysql.jdbc.Driver",
                    username="root",
                    password="root",
                    changeLogFile="/mydir/changelog.xml",
                    logLevel="info",
                    classpath="/myjdbcdriver/xyzdatabase_jdbc_driver.jar"
                )
    liquibase.validate()
    liquibase.status()
    liquibase.updateSQL()
    liquibase.update()
```
