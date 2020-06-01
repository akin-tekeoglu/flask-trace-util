# Flask Trace

`export PIPENV_VENV_IN_PROJECT="enabled" && pipenv install --pre --dev`

# Deployment

`pipenv run python setup.py sdist bdist_wheel`

`pipenv run python -m twine upload dist/*`
