# pgAdmin - Interface GUI PostgreSQL

## Accès

### Développement
- URL: http://localhost:5050
- Email: `admin@ezplantparent.com`
- Password: `admin`

### Production
- URL: https://db.ezplantparent.com (nécessite configuration DNS)
- Email: Configurable via `PGADMIN_EMAIL` dans `.env.prod`
- Password: Configurable via `PGADMIN_PASSWORD` dans `.env.prod`

## Démarrage

### Dev
```bash
docker compose up -d pgadmin
```

### Production
```bash
docker compose -f docker-compose.traefik.yml up -d pgadmin
```

## Configuration de la connexion PostgreSQL

Première connexion à pgAdmin:

1. Ouvrir pgAdmin dans le navigateur
2. Cliquer sur "Add New Server"
3. Remplir les informations:

**Onglet General:**
- Name: `EzPlantParent Dev` (ou `Prod`)

**Onglet Connection:**
- Host name/address: `postgres` (dev) ou `postgres_prod` (production)
- Port: `5432`
- Maintenance database: `ezplantparent`
- Username: `postgres`
- Password: `postgres` (dev) ou valeur de `DB_PASSWORD` (prod)

**Onglet Advanced:**
- DB restriction: `ezplantparent` (optionnel, pour limiter aux BDs pertinentes)

4. Cocher "Save password"
5. Cliquer "Save"

## Fonctionnalités

- **Query Tool**: Exécuter des requêtes SQL personnalisées
- **Table Viewer**: Voir et éditer les données dans un tableau
- **Schema Browser**: Explorer la structure de la base de données
- **Backup/Restore**: Sauvegarder et restaurer des bases de données
- **Import/Export**: Importer/exporter des données CSV
- **Database Designer**: Créer des diagrammes ERD

## Accès rapide

### Dev (via psql)
```bash
docker exec -it postgres psql -U postgres -d ezplantparent
```

### Production (via psql)
```bash
docker exec -it postgres_prod psql -U postgres -d ezplantparent
```

## Notes de sécurité

**IMPORTANT pour la production:**
1. Changer le mot de passe par défaut dans `.env.prod`:
   ```
   PGADMIN_EMAIL=ton-email@domaine.com
   PGADMIN_PASSWORD=un-mot-de-passe-securise
   ```

2. Configurer un sous-domaine DNS pour `db.ezplantparent.com` pointant vers ton VPS

3. Optionnellement, ajouter une authentification supplémentaire via Traefik BasicAuth

## Troubleshooting

### Permission denied sur volume pgadmin_data
```bash
docker compose down
docker volume rm web-ezplantparent_pgadmin_data
docker compose up -d pgadmin
```

### Cannot connect to PostgreSQL
- Vérifier que les containers sont sur le même network
- Vérifier les credentials dans la configuration du serveur
- Utiliser le nom du container comme hostname (`postgres` ou `postgres_prod`)
