# Nom du service défini dans docker-compose.yml
SERVICE=backend
COMPOSE=docker compose -f ../docker-compose.yml

# Juste
test-only:
	$(COMPOSE) exec backend pytest -p no:terminal -s tests -k TestCreateStationAction

test:
	$(COMPOSE) exec -e TESTING=1 backend pytest -p no:terminal tests

test-cover:
	$(COMPOSE) exec -e TESTING=1 backend pytest --cov=backend --cov=backend/usecases --cov-report=term-missing --cov-report=html:/app/backend/usecases/SeeTestsResults tests