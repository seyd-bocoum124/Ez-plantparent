#!/bin/bash

# Script to run database migrations in production
# Usage: ./updatedb.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_INIT_DIR="$SCRIPT_DIR/database/init"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Database Migration Tool ===${NC}"
echo ""

# Try to find database container by common names (prioritize main postgres)
DB_CONTAINER=$(docker ps --format '{{.Names}}' | grep -E '^postgres$' | head -n 1)

# If not found, try postgres_prod
if [ -z "$DB_CONTAINER" ]; then
    DB_CONTAINER=$(docker ps --format '{{.Names}}' | grep -E '^postgres_prod$' | head -n 1)
fi

# If still not found, try any postgres or database container
if [ -z "$DB_CONTAINER" ]; then
    DB_CONTAINER=$(docker ps --format '{{.Names}}' | grep -E '(postgres|database)' | head -n 1)
fi

# Verify container exists and is running
if [ -z "$DB_CONTAINER" ] || ! docker ps --format '{{.Names}}' | grep -q "^${DB_CONTAINER}$"; then
    echo -e "${RED}Error: No database container found or container is not running${NC}"
    echo "Available containers:"
    docker ps --format "  - {{.Names}}"
    exit 1
fi

echo -e "Database container: ${GREEN}$DB_CONTAINER${NC}"
echo ""

# Detect database name based on container
if [[ "$DB_CONTAINER" == *"test"* ]]; then
    DB_NAME_DEFAULT="ezplantparent_test"
else
    DB_NAME_DEFAULT="ezplantparent"
fi

# Load database credentials from .env files
DB_USER=${DB_USER:-postgres}
DB_NAME=${DB_NAME:-$DB_NAME_DEFAULT}

# Try to load from .env files
if [ -f "$SCRIPT_DIR/.env.prod" ]; then
    source "$SCRIPT_DIR/.env.prod"
elif [ -f "$SCRIPT_DIR/.env" ]; then
    source "$SCRIPT_DIR/.env"
fi

# Re-apply default based on container name if not set
if [ -z "$DB_NAME" ]; then
    DB_NAME=$DB_NAME_DEFAULT
fi

echo -e "Database user: ${GREEN}$DB_USER${NC}"
echo -e "Database name: ${GREEN}$DB_NAME${NC}"
echo ""

# List all migration files
echo "Available migrations:"
echo ""

MIGRATIONS=($(ls -1 "$DB_INIT_DIR"/*.sql 2>/dev/null | sort -V))

if [ ${#MIGRATIONS[@]} -eq 0 ]; then
    echo -e "${RED}No migration files found in $DB_INIT_DIR${NC}"
    exit 1
fi

# Display migrations with their prefix numbers
declare -A MIGRATION_MAP
for MIGRATION_FILE in "${MIGRATIONS[@]}"; do
    FILE=$(basename "$MIGRATION_FILE")
    NUMBER=$(echo "$FILE" | grep -oE '^[0-9]+')
    MIGRATION_MAP[$NUMBER]="$MIGRATION_FILE"
    echo "  [$NUMBER] $FILE"
done

echo ""
echo -e "${YELLOW}Enter the migration number to execute (e.g., 3 for 3-add-photo-column.sql):${NC}"
read -r SELECTION

if [ -z "${MIGRATION_MAP[$SELECTION]}" ]; then
    echo -e "${RED}Invalid migration number: $SELECTION${NC}"
    exit 1
fi

# Find all migrations >= selected number
START_INDEX=-1
for i in "${!MIGRATIONS[@]}"; do
    FILE=$(basename "${MIGRATIONS[$i]}")
    NUMBER=$(echo "$FILE" | grep -oE '^[0-9]+')
    if [ "$NUMBER" -ge "$SELECTION" ] && [ "$START_INDEX" -eq -1 ]; then
        START_INDEX=$i
        break
    fi
done

echo ""
echo -e "${YELLOW}Migrations to execute:${NC}"
for i in $(seq $START_INDEX $((${#MIGRATIONS[@]} - 1))); do
    echo "  - $(basename "${MIGRATIONS[$i]}")"
done

echo ""
echo -e "${YELLOW}Continue? (y/n)${NC}"
read -r CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo -e "${GREEN}Executing migrations...${NC}"
echo ""

# Execute migrations
for i in $(seq $START_INDEX $((${#MIGRATIONS[@]} - 1))); do
    MIGRATION_FILE="${MIGRATIONS[$i]}"
    FILE_NAME=$(basename "$MIGRATION_FILE")
    
    echo -e "${YELLOW}Running: $FILE_NAME${NC}"
    
    if docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" < "$MIGRATION_FILE"; then
        echo -e "${GREEN}✓ Success: $FILE_NAME${NC}"
    else
        echo -e "${RED}✗ Failed: $FILE_NAME${NC}"
        echo -e "${RED}Migration stopped due to error${NC}"
        exit 1
    fi
    
    echo ""
done

echo -e "${GREEN}=== All migrations completed successfully ===${NC}"
