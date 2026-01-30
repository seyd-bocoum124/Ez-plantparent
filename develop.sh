#!/bin/sh
set -eu

COMPOSE_FILE="docker-compose.yml"

# place ces fonctions en haut de ton script (avant la boucle)
run_with_ctrlc_return() {
  # usage: run_with_ctrlc_return <command...>
  # lance la commande en background, attend son PID et gère SIGINT pour tuer proprement le child
  "$@" &
  CHILD_PID=$!

  _cleanup_child() {
    # protection si CHILD_PID vide ou déjà terminé
    if [ -n "${CHILD_PID:-}" ] && kill -0 "$CHILD_PID" 2>/dev/null; then
      echo
      echo "Stopping process (pid ${CHILD_PID})..."
      kill -INT "$CHILD_PID" 2>/dev/null || kill -TERM "$CHILD_PID" 2>/dev/null || true
      wait "$CHILD_PID" 2>/dev/null || true
    fi
  }

  # intercepter SIGINT pour n'affecter que le child
  trap '_cleanup_child; trap - INT; echo; echo "Returned to menu."; ' INT

  # attendre le child (bloque ici)
  wait "$CHILD_PID" 2>/dev/null || true

  # restaurer le trap par défaut
  trap - INT
}

# option utile: wrapper qui lance dans une session distincte (isolée des signaux du parent)
run_detached_session() {
  # usage: run_detached_session <command...>
  # démarre la commande dans une session séparée pour éviter propagation des signaux (requires setsid)
  if command -v setsid >/dev/null 2>&1; then
    setsid "$@" >/dev/null 2>&1 &
  else
    "$@" >/dev/null 2>&1 &
  fi
}

show_menu() {
  cat <<'EOF'

Choose action:
--------Operating--------
 1 : Start system
 2 : Reinstall & Start
 3 : Stop system
 -------Monitoring-------
 4 : live logs
 5 : System activity status
 -------Testing--(Require system to operate)-------
 6 : test
 7 : test with logs
 -------------------------------------------------
 8 : Generate security certificates (local dev)
 9 : Generate MQTT certificates (production)
 -------------------------------------------------
 m : Build mobile APK (Android - Docker)
 g : Open Android Studio (local build)
 r : Refresh Android (build + sync, no open)
 -------------------------------------------------
 q : Quit

EOF
}

while true; do
  show_menu
  printf "Enter number: "
  if ! IFS= read -r action; then
    echo "EOF on input, exiting."
    exit 0
  fi

  case "$action" in
    1)
      echo "Running system in background"
      run_with_ctrlc_return docker compose -f "$COMPOSE_FILE" up -d
      ;;
    2)
      echo "Clean reinstall - start in background"
      run_with_ctrlc_return docker compose -f "$COMPOSE_FILE" down -v --remove-orphans
      run_with_ctrlc_return docker compose -f "$COMPOSE_FILE" build --no-cache
      run_with_ctrlc_return docker compose -f "$COMPOSE_FILE" up -d --force-recreate --remove-orphans
      echo "Started in background."
      ;;
    3)
      echo "Stopping all services..."
      run_with_ctrlc_return docker compose -f "$COMPOSE_FILE" stop
      ;;
    4)
      echo "live logs (ctrl+c stops logs and returns to menu)"
      run_with_ctrlc_return docker compose -f "$COMPOSE_FILE" logs -f
      ;;
    5)
      echo "Project containers:"
      run_with_ctrlc_return docker compose -f "$COMPOSE_FILE" ps --all
      ;;
    6)
      echo "Running tests (no logs)..."
      docker compose -f "$COMPOSE_FILE" exec -e TESTING=1 backend pytest -p no:terminal tests
      ;;

    7)
      echo "Running tests (with logs)..."
      docker compose -f docker-compose.yml exec -e TESTING=1 backend \
    pytest --cov=backend --cov=backend/usecases --cov-report=term-missing --cov-report=html:/app/backend/usecases/SeeTestsResults tests
      ;;

    8)
      echo "Creating local development certificates..."
      run_with_ctrlc_return ./security/security.sh
      ;;

    9)
      echo "Creating production MQTT certificates..."
      chmod +x ./security/security-prod.sh
      run_with_ctrlc_return ./security/security-prod.sh
      ;;

    "m"|"M")
      echo "🚀 Building mobile APK..."
      echo "This will:"
      echo "  1. Build Angular app"
      echo "  2. Sync with Capacitor"
      echo "  3. Build Android APK"
      echo ""
      mkdir -p mobile-apk
      run_with_ctrlc_return docker compose -f docker-compose.mobile.yml up
      run_with_ctrlc_return docker compose -f docker-compose.mobile.yml down
      echo ""
      echo "✅ APK generated at: mobile-apk/app-debug.apk"
      ;;

    "g"|"G")
      echo "🔨 Opening Android Studio (local build)..."
      run_with_ctrlc_return ./build-android-local.sh
      ;;

    "r"|"R")
      echo "🔄 Refreshing Android project (no Android Studio open)..."
      run_with_ctrlc_return ./refresh-android.sh
      ;;

    "q")
      echo "Quit"
      exit 0
      ;;

    *)
      echo "Unknown option: $action"
      ;;
  esac

  echo
  printf "Press Enter to continue..."
  IFS= read -r _ || true
done