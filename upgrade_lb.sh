#!/usr/bin/env bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LBVERSION=4.5.0

wget "https://github.com/liquibase/liquibase/releases/download/v4.5.0/liquibase-4.5.0.zip" -O "${DIR}/pyliquibase/liquibase-${LBVERSION}.zip"
cd "${DIR}/pyliquibase/"
unzip "liquibase-${LBVERSION}.zip" -D destination
rm "liquibase-${LBVERSION}.zip"

cd "${DIR}"
git add .
