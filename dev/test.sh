#! /bin/env sh
# This helper script runs all tests and checks included in the project's CI
# pipeline, for easy local testing.

set -e
cd "$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )/../"

echo "Python tests and checks:"

echo "+ black (start)"
poetry run black --check .
echo "+ black (end)"

echo "+ isort (start)"
poetry run isort --check .
echo "- isort (end)"

echo '+ ruff (start)'
poetry run ruff check .
echo '+ ruff (end)'

echo "+ mypy (start)"
poetry run mypy .
echo "+ mypy (end)"

echo "+ pytest (start)"
poetry run pytest --doctest-modules -v
echo "- pytest (end)"
