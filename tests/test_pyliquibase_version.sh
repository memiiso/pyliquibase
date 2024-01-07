#!/usr/bin/env bash

set -e

declare -a lbVersionList=("4.9.0" "4.10.0" "4.11.0" "4.21.1" "4.23.2" "4.24.0" "4.25.1")
for version in "${lbVersionList[@]}"; do
  export TEST_LIQUIBASE_VERSION=$version
  echo "Testing TEST_LIQUIBASE_VERSION ${TEST_LIQUIBASE_VERSION}"
  python -m unittest -v tests.test_pyliquibase.TestPyliquibase.test_update
done