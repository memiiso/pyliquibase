# Usage

`pyliquibase` can be used either as a command-line tool or as a library within your Python scripts.

## Command Line Interface (CLI)

You can run Liquibase commands directly from the shell. A common pattern is to use a `liquibase.properties` file for configuration.

```bash
pyliquibase --defaultsFile=changelogs/liquibase.properties status
pyliquibase --defaultsFile=changelogs/liquibase.properties validate
pyliquibase --defaultsFile=changelogs/liquibase.properties updateSQL
pyliquibase --defaultsFile=changelogs/liquibase.properties update
```

## Python API

Using `pyliquibase` in your Python code is simple.

### Basic Example

```python
from pyliquibase import Pyliquibase

if __name__ == '__main__':
    # Initialize with a properties file
    liquibase = Pyliquibase(defaultsFile="changelogs/liquibase.properties", logLevel="INFO")
    
    # Execute specific commands
    liquibase.status()
    liquibase.validate()
    liquibase.update()
```

### Advanced Usage

You can also use the generic `execute` method to run any Liquibase command:

```python
# Call execute with arguments
liquibase.execute("status")
liquibase.execute("rollback", "MyTag")

# Specific helper methods
liquibase.update_to_tag("MyTag")
liquibase.rollback("MyTag")

# Maintenance commands
liquibase.changelog_sync()
liquibase.clear_checksums()
liquibase.release_locks()
```
