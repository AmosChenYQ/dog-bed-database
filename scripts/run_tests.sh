#!/bin/bash
echo ----Run unit tests and generate coverage data----
pytest --cov=src -s --cov-config=.coveragerc > result.txt
cat result.txt 
if cat result.txt | grep "failed"
then
  echo "Test failed"
  exit 1
fi
echo ----Check coverage rate, target: 100%----
coverage report -m  > cov.txt
coverage_rate=$(cat cov.txt | tail -n 1 | grep -Eo '[^ ]+$' | tr -d %)
if [ $coverage_rate -lt 50 ]
then
  echo "Python code coverage checking failed!"
  coverage xml
  exit 2
fi
coverage xml