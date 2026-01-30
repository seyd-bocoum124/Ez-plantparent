# Nom du service défini dans docker-compose.yml
SERVICE=backend

# Lancer le backend (hot reload)
start:
	docker compose up

# Installer / rebuild image
install:
	docker compose build

install-clean:
	docker compose build --no-cache

# Arrêter les conteneurs
stop:
	docker compose down

# Nettoyer les conteneurs orphelins
clean:
	docker compose down --remove-orphans