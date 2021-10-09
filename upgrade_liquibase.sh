#!/usr/bin/env bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LBVERSION="4.5.0"
LBFILE="liquibase-${LBVERSION}.zip"

# download liquibase
wget "https://github.com/liquibase/liquibase/releases/download/v${LBVERSION}/liquibase-${LBVERSION}.zip" -O "${DIR}/${LBFILE}"
unzip -o "${DIR}/${LBFILE}" -d "${DIR}/pyliquibase/liquibase"
rm "liquibase-${LBVERSION}.zip"

# pull in extensions
rm -rf ${DIR}/pyliquibase/jdbc-drivers/liquibase-redshift*
wget "https://github.com/liquibase/liquibase-redshift/releases/download/liquibase-redshift-${LBVERSION}/liquibase-redshift-${LBVERSION}.jar"  -O "${DIR}/pyliquibase/jdbc-drivers/liquibase-redshift-${LBVERSION}.jar"
rm -rf ${DIR}/pyliquibase/jdbc-drivers/liquibase-bigquery*
wget "https://github.com/liquibase/liquibase-bigquery/releases/download/liquibase-bigquery-${LBVERSION}/liquibase-bigquery-${LBVERSION}.jar"  -O "${DIR}/pyliquibase/jdbc-drivers/liquibase-bigquery-${LBVERSION}.jar"

# commit to git
git add .
git commit -m "upgrade liquibase ${LBVERSION}"