clean:
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info


build: clean
	@pipenv run python setup.py sdist bdist_wheel

release: clean build
	@pipenv run python -m twine upload dist/*

install:
	@export PIPENV_VENV_IN_PROJECT="enabled" && pipenv install --pre --dev