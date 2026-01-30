-- Add ideal values columns to maintenance_sheet table
ALTER TABLE maintenance_sheet 
  ADD COLUMN IF NOT EXISTS ideal_soil_humidity_after_watering INTEGER CHECK (ideal_soil_humidity_after_watering >= 0 AND ideal_soil_humidity_after_watering <= 100),
  ADD COLUMN IF NOT EXISTS ideal_air_humidity INTEGER CHECK (ideal_air_humidity >= 0 AND ideal_air_humidity <= 100),
  ADD COLUMN IF NOT EXISTS ideal_lumens INTEGER CHECK (ideal_lumens >= 0),
  ADD COLUMN IF NOT EXISTS ideal_temperature INTEGER CHECK (ideal_temperature >= -50 AND ideal_temperature <= 60),
  ADD COLUMN IF NOT EXISTS ideal_watering_days_frequency INTEGER CHECK (ideal_watering_days_frequency >= 0);
