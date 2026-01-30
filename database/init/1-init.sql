CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  google_sub TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS station (
  id SERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id),
  name TEXT NOT NULL,
  location TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  pairing_code VARCHAR(20),
  mac_adress VARCHAR(24),
  pairing_timeout TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS capteur (
  id SERIAL PRIMARY KEY,
  station_id INTEGER REFERENCES station(id) ON DELETE CASCADE,
  type TEXT NOT NULL,
  unit TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS intervention (
  id SERIAL PRIMARY KEY,
  station_id INTEGER REFERENCES station(id) ON DELETE CASCADE,
  description TEXT,
  performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TYPE identification_source_t AS ENUM ('GBIF', 'PlantNet', 'Other');

CREATE TABLE maintenance_sheet (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id),
  name TEXT NOT NULL,
  scientific_name TEXT NOT NULL,
  common_name TEXT,
  taxonkey BIGINT,
  taxon_rank TEXT,
  gbif_id BIGINT,
  identification_source identification_source_t NOT NULL DEFAULT 'Other',

  -- valeurs de confiance de l'identification (0-100)
  confidence_score INTEGER CHECK (confidence_score >= 0 AND confidence_score <= 100),

  -- humidité du sol en pourcentage 0-100
  min_soil_humidity INTEGER CHECK (min_soil_humidity >= 0 AND min_soil_humidity <= 100),
  max_soil_humidity INTEGER CHECK (max_soil_humidity >= 0 AND max_soil_humidity <= 100),

  -- éclairement en lux (unité conservée dans lumens_unit)
  min_lumens INTEGER CHECK (min_lumens >= 0),
  max_lumens INTEGER CHECK (max_lumens >= 0),
  lumens_unit TEXT DEFAULT 'lux' NOT NULL, -- XXXXX ENLEVER

  -- humidité de l'air en pourcentage 0-100
  min_air_humidity INTEGER CHECK (min_air_humidity >= 0 AND min_air_humidity <= 100),
  max_air_humidity INTEGER CHECK (max_air_humidity >= 0 AND max_air_humidity <= 100),

  -- température en degrés Celsius
  min_temperature INTEGER CHECK (min_temperature >= -50 AND min_temperature <= 60),
  max_temperature INTEGER CHECK (max_temperature >= -50 AND max_temperature <= 60),

  -- fréquence d'arrosage en jours
  min_watering_days_frequency INTEGER CHECK (min_watering_days_frequency >= 0),
  max_watering_days_frequency INTEGER CHECK (max_watering_days_frequency >= 0),

  -- photo de la plante (stockée en binaire)
  photo BYTEA,

  -- valeurs idéales (ajoutées pour guider l'utilisateur)
  ideal_soil_humidity_after_watering INTEGER CHECK (ideal_soil_humidity_after_watering >= 0 AND ideal_soil_humidity_after_watering <= 100),
  ideal_air_humidity INTEGER CHECK (ideal_air_humidity >= 0 AND ideal_air_humidity <= 100),
  ideal_lumens INTEGER CHECK (ideal_lumens >= 0),
  ideal_temperature INTEGER CHECK (ideal_temperature >= -50 AND ideal_temperature <= 60),
  ideal_watering_days_frequency INTEGER CHECK (ideal_watering_days_frequency >= 0),

  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

ALTER TABLE maintenance_sheet
  ADD CONSTRAINT soil_humidity_min_le_max CHECK (
    min_soil_humidity IS NULL OR max_soil_humidity IS NULL OR min_soil_humidity <= max_soil_humidity
  ),
  ADD CONSTRAINT lumens_min_le_max CHECK (
    min_lumens IS NULL OR max_lumens IS NULL OR min_lumens <= max_lumens
  ),
  ADD CONSTRAINT air_humidity_min_le_max CHECK (
    min_air_humidity IS NULL OR max_air_humidity IS NULL OR min_air_humidity <= max_air_humidity
  ),
  ADD CONSTRAINT temperature_min_le_max CHECK (
    min_temperature IS NULL OR max_temperature IS NULL OR min_temperature <= max_temperature
  );

CREATE INDEX idx_maintenance_user ON maintenance_sheet (user_id);
CREATE INDEX idx_maintenance_taxonkey ON maintenance_sheet (taxonkey);
CREATE INDEX idx_maintenance_scientific_name ON maintenance_sheet (scientific_name);


CREATE TABLE IF NOT EXISTS express_analysis_report (
  id SERIAL PRIMARY KEY,

  plant_id BIGINT NOT NULL REFERENCES maintenance_sheet(id) ON DELETE CASCADE,
  analysis_type TEXT CHECK (analysis_type IN ('express', 'watering')) NOT NULL,

  soil_humidity_mean REAL CHECK (soil_humidity_mean >= 0 AND soil_humidity_mean <= 100),
  lumens_mean REAL CHECK (lumens_mean >= 0),
  air_humidity_mean REAL CHECK (air_humidity_mean >= 0 AND air_humidity_mean <= 100),
  temperature_mean REAL CHECK (temperature_mean >= -50 AND temperature_mean <= 60),

  soil_humidity_data TEXT CHECK (char_length(soil_humidity_data) <= 512),
  lumens_data TEXT CHECK (char_length(lumens_data) <= 512),
  air_humidity_data TEXT CHECK (char_length(air_humidity_data) <= 512),
  temperature_data TEXT CHECK (char_length(temperature_data) <= 512),

  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);


CREATE TABLE IF NOT EXISTS watering_report (
  id SERIAL PRIMARY KEY,

  plant_id BIGINT NOT NULL REFERENCES maintenance_sheet(id) ON DELETE CASCADE,

  soil_humidity_mean REAL CHECK (soil_humidity_mean >= 0 AND soil_humidity_mean <= 100),
  sigma3 REAL CHECK (sigma3 >= 0 AND sigma3 <= 100),
  target_humidity REAL CHECK (target_humidity >= 0 AND target_humidity <= 100),

  soil_humidity_data TEXT CHECK (char_length(soil_humidity_data) <= 512),
  pump_data TEXT CHECK (char_length(pump_data) <= 512),

  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);



CREATE TABLE refresh_tokens (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  revoked BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT now()
);
