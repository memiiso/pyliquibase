#!/usr/bin/env bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LBVERSION="4.10.0"
JDBC_SNOWFLAKE="3.13.18"
JDBC_REDSHIFT="2.1.0.7"
JDBC_BIGQUERY="1.2.22.1026"

# download liquibase
LBFILE="liquibase-${LBVERSION}.zip"
wget "https://github.com/liquibase/liquibase/releases/download/v${LBVERSION}/liquibase-${LBVERSION}.zip" -O "${DIR}/${LBFILE}"
rm -rf "${DIR}/pyliquibase/liquibase/*"
unzip -o "${DIR}/${LBFILE}" -d "${DIR}/pyliquibase/liquibase"
rm "liquibase-${LBVERSION}.zip"

# pull in extensions AND JDBC DRIVERS
rm -rf ${DIR}/pyliquibase/jdbc-drivers/*
wget "https://github.com/liquibase/liquibase-redshift/releases/download/liquibase-redshift-${LBVERSION}/liquibase-redshift-${LBVERSION}.jar"  -O "${DIR}/pyliquibase/jdbc-drivers/liquibase-redshift-${LBVERSION}.jar"
wget "https://github.com/liquibase/liquibase-bigquery/releases/download/liquibase-bigquery-${LBVERSION}/liquibase-bigquery-${LBVERSION}.jar"  -O "${DIR}/pyliquibase/jdbc-drivers/liquibase-bigquery-${LBVERSION}.jar"
wget "https://github.com/liquibase/liquibase-snowflake/releases/download/liquibase-snowflake-${LBVERSION}/liquibase-snowflake-${LBVERSION}.jar"  -O "${DIR}/pyliquibase/jdbc-drivers/liquibase-snowflake-${LBVERSION}.jar"
wget "https://repo1.maven.org/maven2/net/snowflake/snowflake-jdbc/${JDBC_SNOWFLAKE}/snowflake-jdbc-${JDBC_SNOWFLAKE}.jar"  -O "${DIR}/pyliquibase/jdbc-drivers/snowflake-jdbc-${JDBC_SNOWFLAKE}.jar"
wget "https://repo1.maven.org/maven2/com/amazon/redshift/redshift-jdbc42/${JDBC_REDSHIFT}/redshift-jdbc42-${JDBC_REDSHIFT}.jar"  -O "${DIR}/pyliquibase/jdbc-drivers/redshift-jdbc42-${JDBC_REDSHIFT}.jar"

wget "https://storage.googleapis.com/simba-bq-release/jdbc/SimbaJDBCDriverforGoogleBigQuery42_${JDBC_BIGQUERY}.zip" -O "${DIR}/SimbaJDBCDriverforGoogleBigQuery42_${JDBC_BIGQUERY}.zip"
unzip -o "${DIR}/SimbaJDBCDriverforGoogleBigQuery42_${JDBC_BIGQUERY}.zip" -d "${DIR}/pyliquibase/jdbc-drivers"
rm "SimbaJDBCDriverforGoogleBigQuery42_${JDBC_BIGQUERY}.zip"
# commit to git
git add --all
git commit -m "upgrade liquibase ${LBVERSION}"