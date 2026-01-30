-- Ajouter la colonne photo à la table maintenance_sheet
ALTER TABLE maintenance_sheet
ADD COLUMN photo BYTEA;

-- Ajouter un commentaire pour documenter la colonne
COMMENT ON COLUMN maintenance_sheet.photo IS 'Photo de la plante stockée en format BYTEA (JPEG/PNG)';
