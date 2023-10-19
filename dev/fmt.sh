#! /bin/env sh
# This helper script formats the code according to black and isort standarts.
set -e
cd "$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )/../"

echo '+ black (start)'
poetry run black .
echo '+ black (end)'

echo '+ isort (start)'
poetry run isort .
echo '+ isort (end)'

echo '+ ruff (start)'
poetry run ruff check --fix .
echo '+ ruff (end)'
