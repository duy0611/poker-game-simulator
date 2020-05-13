########################################################################
### Pipenv init

DOCKER_COMPOSE_PROJECT := "poker-game-simulator"
DOCKER_COMPOSE_NETWORK := "poker-game-simulator-shared"

# Initialize Pipenv virtual environment and install dev packages.
# Use local folder (.venv) to enable automation.
.venv:
	PIPENV_VENV_IN_PROJECT=1 pipenv install --dev

########################################################################
### Build & run

.PHONY: run
run: .venv
	pipenv run python main.py

.PHONY: run-reload
run-reload: .venv
	FLASK_APP=app.py FLASK_ENV=development pipenv run flask run

.PHONY: run-docker
run-docker: build-agent build-simulator
	docker container ls -aq | xargs --no-run-if-empty docker stop
	docker network inspect $(DOCKER_COMPOSE_NETWORK) >/dev/null 2>&1 || docker create network $(DOCKER_COMPOSE_NETWORK)
	docker run --rm -d --name $(DOCKER_COMPOSE_PROJECT) --network $(DOCKER_COMPOSE_NETWORK) -p 5000:5000 -v /var/run/docker.sock:/var/run/docker.sock poker-simulator:latest
	@echo "Run following to execute simulation: "
	@echo "curl -X POST 'http://localhost:5000/players/register/playerOne'"
	@echo "curl -X POST 'http://localhost:5000/players/register/playerTwo'"
	@echo "curl -X POST 'http://localhost:5000/simulations/start_new?players=playerOne,playerTwo&init_pot=50&small_blind_stake=5&max_iterations=1'"

.PHONY: run-docker-with-bots
run-docker-with-bots: build-agent build-simulator
	docker container ls -aq | xargs --no-run-if-empty docker stop
	docker network inspect $(DOCKER_COMPOSE_NETWORK) >/dev/null 2>&1 || docker create network $(DOCKER_COMPOSE_NETWORK)
	docker run --rm -d --name agent-botOne --network $(DOCKER_COMPOSE_NETWORK) poker-agent:default-latest
	docker run --rm -d --name agent-botTwo --network $(DOCKER_COMPOSE_NETWORK) poker-agent:default-latest
	docker run --rm -d --name $(DOCKER_COMPOSE_PROJECT) --network $(DOCKER_COMPOSE_NETWORK) -p 5000:5000 -v /var/run/docker.sock:/var/run/docker.sock poker-simulator:latest
	@echo "Run following to execute simulation: "
	@echo "curl -X POST 'http://localhost:5000/simulations/start_new?players=botOne,botTwo&init_pot=50&small_blind_stake=5&max_iterations=1'"


.PHONY: stop-docker
stop-docker:
	docker container ls -aq | xargs --no-run-if-empty docker stop

.PHONY: build-agent
build-agent:
	cd agent-build && docker build . -t poker-agent:default-latest

.PHONY: build-simulator
build-simulator:
	docker build . -t poker-simulator:latest

########################################################################
### Run tests

.PHONY: pylint
pylint: .venv
	pipenv run pylint src/
