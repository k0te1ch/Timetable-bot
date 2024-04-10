BASEDIR=$(CURDIR)

pip-tools:
	python -m pip install -U pip
	python -m pip install -U poetry
	poetry add poetry-plugin-up --group dev
	poetry add pre-commit --group dev

requirements: pip-tools
	poetry install --with=dev,test

run:
	python bot.py run

run-runner:
	cd $(BASEDIR)/actions-runner && run.cmd

test:
	poetry run pytest --cov=.
	#TODO edit

check:
	poetry run pre-commit run --show-diff-on-failure --color=always --all-files

update: pip-tools
	poetry update
	poetry run poetry up
	poetry run pre-commit autoupdate

lock:
	poetry lock

docker-build-run:
	docker-compose
