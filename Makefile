########################################################################
### Pipenv init

DOCKER_COMPOSE_PROJECT := "poker-game-simulator"

# Initialize Pipenv virtual environment and install dev packages.
# Use local folder (.venv) to enable automation.
.venv:
	PIPENV_VENV_IN_PROJECT=1 pipenv install --dev

########################################################################
### Build & run

.PHONY: run
run: .venv
	pipenv run python main.py

.PHONY: build-agent
build-agent:
	cd agent-build && docker build . -t poker-agent:default-latest

.PHONY: build-simulator
build-simulator:
	docker build . -t poker-simulator:latest
