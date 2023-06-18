#!/usr/bin/env bash

set -e

declare -a lbVersionList=("4.9.0" "4.10.0" "4.11.0")
for version in "${lbVersionList[@]}"; do
  export TEST_LIQUIBASE_VERSION=$version
  echo "Testing TEST_LIQUIBASE_VERSION ${TEST_LIQUIBASE_VERSION}"
  python -m unittest -v tests.test_pyliquibase.TestPyliquibase.test_update
done