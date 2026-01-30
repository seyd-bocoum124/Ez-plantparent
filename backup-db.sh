#!/bin/bash

# Script to backup PostgreSQL database
# Usage: ./backup-db.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$SCRIPT_DIR/database/backups"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Database Backup Tool ===${NC}"
echo ""

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

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

# Generate backup filename with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_backup_${TIMESTAMP}.sql"

echo -e "${YELLOW}Creating backup...${NC}"
echo -e "Backup file: ${GREEN}$BACKUP_FILE${NC}"
echo ""

# Create the backup
if docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" --clean --if-exists > "$BACKUP_FILE"; then
    # Get file size
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    
    echo -e "${GREEN}✓ Backup completed successfully${NC}"
    echo -e "File: ${GREEN}$BACKUP_FILE${NC}"
    echo -e "Size: ${GREEN}$BACKUP_SIZE${NC}"
    echo ""
    
    # List recent backups
    echo -e "${YELLOW}Recent backups:${NC}"
    ls -lh "$BACKUP_DIR" | tail -n 5 | awk '{if(NR>1)print "  "$9" ("$5")"}'
    echo ""
    
    # Optional: compress the backup
    echo -e "${YELLOW}Compress backup? (y/n)${NC}"
    read -r COMPRESS
    
    if [ "$COMPRESS" = "y" ] || [ "$COMPRESS" = "Y" ]; then
        echo -e "${YELLOW}Compressing...${NC}"
        gzip "$BACKUP_FILE"
        COMPRESSED_FILE="${BACKUP_FILE}.gz"
        COMPRESSED_SIZE=$(du -h "$COMPRESSED_FILE" | cut -f1)
        echo -e "${GREEN}✓ Compressed: $COMPRESSED_FILE ($COMPRESSED_SIZE)${NC}"
    fi
else
    echo -e "${RED}✗ Backup failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=== Backup completed ===${NC}"
