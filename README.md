# pyliquibase

Python wrapper for [liquibase](http://www.liquibase.org/). 
Liquibase version : 3.8.4

## Installation

```python
pip install https://github.com/memiiso/pyliquibase/archive/master.zip
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
