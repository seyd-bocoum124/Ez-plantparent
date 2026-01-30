-- Données de test
INSERT INTO users (google_sub, email)
VALUES
  ('google-sub-12345', 'alice@example.com'),
  ('111390199319577605120', 'pierrelucueisd@gmail.com');

INSERT INTO station (user_id, name, location, pairing_code, mac_adress, pairing_timeout) VALUES
  (1, 'Station A', 'Montréal', 'PAIR123456', 'STA0000000001', now() + interval '300 seconds'),
  (2, 'Station-B76C2C', 'Québec',   'S8Q5XJWT3G', '781C3CB76C2C', now() + interval '300 seconds');

INSERT INTO capteur (station_id, type, unit) VALUES
  (1, 'Température', '°C'),
  (1, 'Humidité', '%'),
  (2, 'Luminosité', 'lux');

INSERT INTO intervention (station_id, description, performed_at) VALUES
  (1, 'Nettoyage des capteurs', '2025-10-10 10:00:00'),
  (2, 'Remplacement du module ESP32', '2025-10-11 14:30:00');

INSERT INTO maintenance_sheet (
  user_id, name, scientific_name, common_name, taxonkey, taxon_rank, gbif_id,
  identification_source, confidence_score,
  min_soil_humidity, max_soil_humidity, min_lumens, max_lumens, lumens_unit,
  min_air_humidity, max_air_humidity, min_temperature, max_temperature,
  min_watering_days_frequency, max_watering_days_frequency,
  ideal_soil_humidity_after_watering, ideal_air_humidity, ideal_lumens, ideal_temperature, ideal_watering_days_frequency
) VALUES
(1, 'Monstera - feuille perforée', 'Monstera deliciosa', 'Monstera', 100001, 'species', NULL, 'GBIF', 95,
  20, 50, 200, 2000, 'lux', 40, 70, 16, 28, 14, 14,
  35, 55, 1000, 22, 14),

(1, 'Ficus caoutchouc', 'Ficus elastica', 'Rubber Plant', 100002, 'species', 100002, 'PlantNet', 88,
  25, 55, 100, 1500, 'lux', 30, 60, 15, 27, 21, 24,
  40, 45, 800, 21, 22),

(2, 'Sansevieria facile', 'Dracaena trifasciata', 'Snake Plant', 100003, 'species', NULL, 'GBIF', 92,
  5, 30, 50, 800, 'lux', 20, 60, 10, 30, 30, 34,
  18, 40, 400, 20, 32),

(2, 'Pilea propagation facile', 'Pilea peperomioides', 'Pilea', 100004, 'species', 100004, 'PlantNet', 80,
  30, 60, 150, 1200, 'lux', 40, 70, 16, 24, 7, 10,
  45, 55, 675, 20, 8),

(2, 'Pothos doré', 'Epipremnum aureum', 'Pothos', 100005, 'species', NULL, 'GBIF', 90,
  25, 60, 100, 1500, 'lux', 35, 70, 15, 26, 10, 12,
  42, 52, 800, 20, 11),

(1, 'Zamioculcas rustique', 'Zamioculcas zamiifolia', 'ZZ Plant', 100006, 'species', 100006, 'PlantNet', 85,
  10, 40, 50, 900, 'lux', 30, 60, 12, 28, 21, 24,
  25, 45, 475, 20, 22);

-- ========================================================
-- Express Analysis Reports
-- ========================================================

-- Plant ID 2: Ficus elastica (alice@example.com) - Analyse complète avec données raw
INSERT INTO express_analysis_report (
  plant_id,
  analysis_type,
  soil_humidity_mean,
  lumens_mean,
  air_humidity_mean,
  temperature_mean,
  soil_humidity_data,
  lumens_data,
  air_humidity_data,
  temperature_data,
  created_at
) VALUES (
  2,
  'express',
  42.3,
  8500.7,
  58.9,
  23.4,
  '40;41;42;43;42;44;43;41;40;42;43;44;45;41;42;43;44;43;42;41;40;42;43;44;45;46;44;43;42;41',
  '8000;8200;8300;8400;8500;8600;8700;8800;8900;9000;9100;9200;9300;9400;9500;9600;9700;9800;9900;10000;10100;10200;10300;10400;10500;10600;10700;10800;10900;11000',
  '55;56;57;58;59;60;61;60;59;58;57;56;55;54;53;52;51;52;53;54;55;56;57;58;59;60;61;60;59;58',
  '22.5;22.7;22.9;23.0;23.2;23.4;23.5;23.6;23.7;23.8;23.9;24.0;24.1;24.2;24.3;24.4;24.5;24.6;24.7;24.8;24.9;25.0;25.1;25.2;25.3;25.4;25.5;25.6;25.7;25.8',
  NOW() - INTERVAL '50 days'
);

-- Plant ID 3: Snake Plant (pierrelucueisd@gmail.com) - Analyse complète avec données raw
INSERT INTO express_analysis_report (
  plant_id,
  analysis_type,
  soil_humidity_mean,
  lumens_mean,
  air_humidity_mean,
  temperature_mean,
  soil_humidity_data,
  lumens_data,
  air_humidity_data,
  temperature_data,
  created_at
) VALUES (
  3,
  'express',
  18.7,
  12350.2,
  34.1,
  26.8,
  '[20,19,18,17,16,15,14,15,16,17,18,19,20,21,22,21,20,19,18,17,16,15,14,13,12,13,14,15,16,17]',
  '[12000,12100,12200,12300,12400,12500,12600,12700,12800,12900,13000,13100,13200,13300,13400,13500,13600,13700,13800,13900,14000,14100,14200,14300,14400,14500,14600,14700,14800,14900]',
  '[30,31,32,33,34,35,36,35,34,33,32,31,30,29,28,27,26,27,28,29,30,31,32,33,34,35,36,37,38,39]',
  '[26.0,26.1,26.2,26.3,26.4,26.5,26.6,26.7,26.8,26.9,27.0,27.1,27.2,27.3,27.4,27.5,27.6,27.7,27.8,27.9,28.0,28.1,28.2,28.3,28.4,28.5,28.6,28.7,28.8,28.9]'
    NOW() - INTERVAL '25 days'
);

-- Plant ID 5: Pothos (pierrelucueisd@gmail.com) - Analyse complète avec données raw
INSERT INTO express_analysis_report (
  plant_id,
  analysis_type,
  soil_humidity_mean,
  lumens_mean,
  air_humidity_mean,
  temperature_mean,
  soil_humidity_data,
  lumens_data,
  air_humidity_data,
  temperature_data
) VALUES (
  5,
  'express',
  61.5,
  4200.0,
  72.3,
  21.2,
  '[60,61,62,63,64,65,66,65,64,63,62,61,60,59,58,57,56,57,58,59,60,61,62,63,64,65,66,67,68,69]',
  '[4000,4050,4100,4150,4200,4250,4300,4350,4400,4450,4500,4550,4600,4650,4700,4750,4800,4850,4900,4950,5000,5050,5100,5150,5200,5250,5300,5350,5400,5450]',
  '[70,71,72,73,74,75,76,75,74,73,72,71,70,69,68,67,66,67,68,69,70,71,72,73,74,75,76,77,78,79]',
  '[20.5,20.6,20.7,20.8,20.9,21.0,21.1,21.2,21.3,21.4,21.5,21.6,21.7,21.8,21.9,22.0,22.1,22.2,22.3,22.4,22.5,22.6,22.7,22.8,22.9,23.0,23.1,23.2,23.3,23.4]'
);

-- Analyses express supplémentaires pour pierrelucueisd@gmail.com
-- Plant ID 3: Snake Plant (Dracaena trifasciata) - Analyse 1
INSERT INTO express_analysis_report (
  plant_id,
  analysis_type,
  soil_humidity_mean,
  lumens_mean,
  air_humidity_mean,
  temperature_mean,
  soil_humidity_data,
  lumens_data,
  air_humidity_data,
  temperature_data
) VALUES (
  3,
  'express',
  1.5862,
  NULL,
  37.082268,
  18.7578,
  '[1.859,1.115,1.859,1.487,1.487,1.487,1.859,1.487,1.487,1.487,1.487,1.487,1.859,1.487,1.859]',
  NULL,
  '[37.051,37.042,37.039,37.054,37.05,37.093,37.104,37.137,37.082,37.097,37.08,37.1,37.109,37.091,37.105]',
  '[18.83,18.752,18.749,18.752,18.734,18.745,18.756,18.754,18.766,18.741,18.771,18.763,18.758,18.753,18.743]'
);

-- Plant ID 3: Snake Plant - Analyse 2
INSERT INTO express_analysis_report (
  plant_id,
  analysis_type,
  soil_humidity_mean,
  lumens_mean,
  air_humidity_mean,
  temperature_mean,
  soil_humidity_data,
  lumens_data,
  air_humidity_data,
  temperature_data,
  created_at
) VALUES (
  3,
  'express',
  35.910732,
  NULL,
  36.6902,
  18.712534,
  '[29.74,31.227,31.97,31.97,32.342,32.342,32.342,31.97,36.803,40.149,42.007,42.007,41.264,41.264,41.264]',
  NULL,
  '[36.87,36.819,36.824,36.783,36.767,36.744,36.701,36.684,36.659,36.632,36.599,36.611,36.573,36.558,36.529]',
  '[18.724,18.712,18.72,18.74,18.714,18.7,18.713,18.717,18.703,18.681,18.696,18.715,18.713,18.717,18.723]',
  NOW() - INTERVAL '20 days'
);

-- Plant ID 4: Pilea (user 2 - pierrelucueisd@gmail.com) - Analyse avec données cohérentes
INSERT INTO express_analysis_report (
  plant_id,
  analysis_type,
  soil_humidity_mean,
  lumens_mean,
  air_humidity_mean,
  temperature_mean,
  soil_humidity_data,
  lumens_data,
  air_humidity_data,
  temperature_data,
  created_at
) VALUES (
  4,
  'express',
  46.8,
  675.5,
  56.3,
  19.8,
  '[44,45,46,47,48,49,48,47,46,45,44,45,46,47,48,49,50,49,48,47,46,45,44,45,46,47,48,49,50,51]',
  '[650,660,670,680,690,700,710,720,680,670,660,650,640,630,640,650,660,670,680,690,700,710,720,680,670,660,650,655,665,675]',
  '[54,55,56,57,58,59,60,59,58,57,56,55,54,53,54,55,56,57,58,59,60,61,60,59,58,57,56,55,54,53]',
  '[19.0,19.2,19.4,19.5,19.6,19.7,19.8,19.9,20.0,20.1,20.0,19.9,19.8,19.7,19.6,19.7,19.8,19.9,20.0,20.1,20.2,20.1,20.0,19.9,19.8,19.7,19.6,19.5,19.4,19.3]',
  NOW() - INTERVAL '3 days'
);

-- Plant ID 5: Pothos (user 2 - pierrelucueisd@gmail.com) - Analyse supplémentaire
INSERT INTO express_analysis_report (
  plant_id,
  analysis_type,
  soil_humidity_mean,
  lumens_mean,
  air_humidity_mean,
  temperature_mean,
  soil_humidity_data,
  lumens_data,
  air_humidity_data,
  temperature_data,
  created_at
) VALUES (
  5,
  'express',
  43.2,
  850.0,
  53.7,
  20.5,
  '[41,42,43,44,45,46,45,44,43,42,41,42,43,44,45,46,47,46,45,44,43,42,41,40,41,42,43,44,45,46]',
  '[800,810,820,830,840,850,860,870,880,890,900,890,880,870,860,850,840,830,820,810,800,790,800,810,820,830,840,850,860,870]',
  '[51,52,53,54,55,56,57,56,55,54,53,52,51,50,51,52,53,54,55,56,57,58,57,56,55,54,53,52,51,50]',
  '[19.5,19.7,19.9,20.0,20.1,20.2,20.3,20.4,20.5,20.6,20.7,20.8,20.9,21.0,20.9,20.8,20.7,20.6,20.5,20.4,20.3,20.2,20.1,20.0,19.9,19.8,19.7,19.8,19.9,20.0]',
  NOW() - INTERVAL '20 days'
);

-- Plant ID 1: Monstera (user 1 - alice@example.com) - Analyse avec données cohérentes
INSERT INTO express_analysis_report (
  plant_id,
  analysis_type,
  soil_humidity_mean,
  lumens_mean,
  air_humidity_mean,
  temperature_mean,
  soil_humidity_data,
  lumens_data,
  air_humidity_data,
  temperature_data
) VALUES (
  1,
  'express',
  36.5,
  1050.0,
  56.8,
  21.8,
  '[34,35,36,37,38,39,38,37,36,35,34,35,36,37,38,39,40,39,38,37,36,35,34,33,34,35,36,37,38,39]',
  '[1000,1010,1020,1030,1040,1050,1060,1070,1080,1090,1100,1090,1080,1070,1060,1050,1040,1030,1020,1010,1000,990,1000,1010,1020,1030,1040,1050,1060,1070]',
  '[54,55,56,57,58,59,60,59,58,57,56,55,54,55,56,57,58,59,60,61,60,59,58,57,56,55,54,55,56,57]',
  '[21.0,21.2,21.4,21.5,21.6,21.7,21.8,21.9,22.0,22.1,22.2,22.3,22.4,22.5,22.4,22.3,22.2,22.1,22.0,21.9,21.8,21.7,21.6,21.5,21.4,21.5,21.6,21.7,21.8,21.9]'
);

-- Plant ID 6: ZZ Plant (user 1 - alice@example.com) - Analyse avec données cohérentes
INSERT INTO express_analysis_report (
  plant_id,
  analysis_type,
  soil_humidity_mean,
  lumens_mean,
  air_humidity_mean,
  temperature_mean,
  soil_humidity_data,
  lumens_data,
  air_humidity_data,
  temperature_data
) VALUES (
  6,
  'express',
  26.3,
  490.0,
  46.2,
  19.5,
  '[24,25,26,27,28,29,28,27,26,25,24,25,26,27,28,29,30,29,28,27,26,25,24,23,24,25,26,27,28,29]',
  '[450,460,470,480,490,500,510,520,500,490,480,470,460,450,460,470,480,490,500,510,520,500,490,480,470,460,450,460,470,480]',
  '[44,45,46,47,48,49,48,47,46,45,44,45,46,47,48,49,50,49,48,47,46,45,44,43,44,45,46,47,48,49]',
  '[18.5,18.7,18.9,19.0,19.1,19.2,19.3,19.4,19.5,19.6,19.7,19.8,19.9,20.0,19.9,19.8,19.7,19.6,19.5,19.4,19.3,19.2,19.1,19.0,18.9,19.0,19.1,19.2,19.3,19.4]'
);

-- ========================================================
-- Watering Reports (Rapports d'arrosage)
-- ========================================================

-- Plant ID 3: Snake Plant (user 2 - pierrelucueisd@gmail.com) - Données du backup
INSERT INTO watering_report (
  plant_id,
  soil_humidity_mean,
  sigma3,
  target_humidity,
  soil_humidity_data,
  pump_data,
  created_at
) VALUES (
  3,
  41.8835,
  0,
  17.5,
  '[41.636,42.007,42.007]',
  '[null,null,null]',
  NOW() - INTERVAL '45 days'
);

INSERT INTO watering_report (
  plant_id,
  soil_humidity_mean,
  sigma3,
  target_humidity,
  soil_humidity_data,
  pump_data,
  created_at
) VALUES (
  3,
  34.4486,
  0,
  17.5,
  '[37.546,25.279,40.52]',
  '[null,null,null]',
  NOW() - INTERVAL '35 days'
);