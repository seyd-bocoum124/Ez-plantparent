from typing import List, Optional

from infrastructure.database import get_db, Database
from entities.models import Station, MaintenanceSheet, ExpressAnalysisReport, RefreshToken, User, WateringReport, \
    MaintenanceSummary, LastFeeledHumidity
from datetime import datetime, timezone


class Repository:

    def __init__(self, db: Optional[Database] = None):
        self._db = db if db is not None else get_db()


    def list_all_stations(self) -> List[Station]:
        db = self._db
        rows = db.query("SELECT id, user_id, name, location, created_at, pairing_code, mac_adress, pairing_timeout FROM station ORDER BY id;")
        return [Station(*row) for row in rows]

    def list_stations_by_user_id(self, user_id: int) -> List[Station]:
        db = self._db
        rows = db.query(
            "SELECT id, user_id, name, location, created_at, pairing_code, mac_adress, pairing_timeout FROM station WHERE user_id = %s ORDER BY id;",
            (user_id,)
        )
        return [Station(*row) for row in rows]

    def create_station(self, station: Station) -> int:
        db = self._db
        row = db.query(
            "INSERT INTO station (user_id, name, location, pairing_code, mac_adress, pairing_timeout) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
            (station.user_id, station.name, station.location, station.pairing_code, station.mac_adress, station.pairing_timeout)
        )
        station.id = row[0][0]
        return station.id


    def get_station_by_id(self, id_):
        db = self._db
        row = db.query(
            "SELECT id, user_id, name, location, created_at, pairing_code, mac_adress, pairing_timeout FROM station WHERE id = %s;", (id_,)
        )
        if not row:
            return None
        r = row[0]
        return Station(id=r[0], user_id=r[1], name=r[2], location=r[3], created_at=r[4], pairing_code=r[5], mac_adress=r[6], pairing_timeout=r[7])

    def get_station_by_mac_address(self, mac_adress: str):
        db = self._db
        row = db.query(
            """
            SELECT id, user_id, name, location, created_at, pairing_code, mac_adress, pairing_timeout
            FROM station
            WHERE mac_adress = %s;
            """,
            (mac_adress,)
        )
        if not row:
            return None
        r = row[0]
        return Station(
            id=r[0],
            user_id=r[1],
            name=r[2],
            location=r[3],
            created_at=r[4],
            pairing_code=r[5],
            mac_adress=r[6],
            pairing_timeout=r[7]
        )

    def get_station_by_pairing_code(self, pairing_code: str):
        db = self._db
        row = db.query(
            """
            SELECT id, user_id, name, location, created_at, pairing_code, mac_adress, pairing_timeout
            FROM station
            WHERE pairing_code = %s;
            """,
            (pairing_code,)
        )
        if not row:
            return None
        r = row[0]
        return Station(
            id=r[0],
            user_id=r[1],
            name=r[2],
            location=r[3],
            created_at=r[4],
            pairing_code=r[5],
            mac_adress=r[6],
            pairing_timeout=r[7]
        )

    def update_station(self, station: Station) -> bool:
        db = self._db
        result = db.execute(
            "UPDATE station SET user_id=%s, name=%s, location=%s, pairing_code=%s, mac_adress=%s, pairing_timeout=%s WHERE id=%s;",
            (station.user_id, station.name, station.location, station.pairing_code, station.mac_adress, station.pairing_timeout, station.id)
        )
        return result.rowcount > 0

    def delete_other_user_stations(self, user_id: int, keep_station_id: int) -> int:
        """Supprime toutes les stations d'un utilisateur sauf celle spécifiée"""
        db = self._db
        result = db.execute(
            "DELETE FROM station WHERE user_id = %s AND id != %s;",
            (user_id, keep_station_id)
        )
        return result.rowcount

    ## Maintenance sheets

    def list_all_maintenance_sheets_by_user_id(self, user_id: int) -> List[MaintenanceSheet]:
        db = self._db
        rows = db.query("""
            SELECT
              id,
              user_id,
              name,
              scientific_name,
              common_name,
              taxonkey,
              taxon_rank,
              gbif_id,
              identification_source,
              confidence_score,
              min_soil_humidity,
              max_soil_humidity,
              min_lumens,
              max_lumens,
              lumens_unit,
              min_air_humidity,
              max_air_humidity,
              min_temperature,
              max_temperature,
              min_watering_days_frequency,
              max_watering_days_frequency,
              ideal_soil_humidity_after_watering,
              ideal_air_humidity,
              ideal_lumens,
              ideal_temperature,
              ideal_watering_days_frequency,
              photo,
              created_at,
              updated_at
            FROM maintenance_sheet
            WHERE user_id = %s
            ORDER BY id ASC;
        """, (user_id,))
        return [MaintenanceSheet(*row) for row in rows]

    def get_maintenance_sheet_by_id(self, id_: int) -> Optional[MaintenanceSheet]:
        row = self._db.query_one_dict(
            """
            SELECT
              id,
              user_id,
              name,
              scientific_name,
              common_name,
              taxonkey,
              taxon_rank,
              gbif_id,
              identification_source,
              confidence_score,
              min_soil_humidity,
              max_soil_humidity,
              min_lumens,
              max_lumens,
              lumens_unit,
              min_air_humidity,
              max_air_humidity,
              min_temperature,
              max_temperature,
              min_watering_days_frequency,
              max_watering_days_frequency,
              ideal_soil_humidity_after_watering,
              ideal_air_humidity,
              ideal_lumens,
              ideal_temperature,
              ideal_watering_days_frequency,
              photo,
              created_at,
              updated_at
            FROM maintenance_sheet
            WHERE id = %s
            LIMIT 1;
            """,
            (id_,)
        )
        if row is None:
            return None
        return MaintenanceSheet(**row)

    def create_maintenance_sheet(self, sheet: MaintenanceSheet) -> int:
        db = self._db
        row = db.query(
            """
            INSERT INTO maintenance_sheet (
              user_id, name, scientific_name, common_name, taxonkey, taxon_rank, gbif_id,
              identification_source, confidence_score,
              min_soil_humidity, max_soil_humidity,
              min_lumens, max_lumens, lumens_unit,
              min_air_humidity, max_air_humidity,
              min_temperature, max_temperature,
              min_watering_days_frequency,
              max_watering_days_frequency,
              ideal_soil_humidity_after_watering,
              ideal_air_humidity,
              ideal_lumens,
              ideal_temperature,
              ideal_watering_days_frequency,
              photo,
              created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (
                sheet.user_id,
                sheet.name,
                sheet.scientific_name,
                sheet.common_name,
                sheet.taxonkey,
                sheet.taxon_rank,
                sheet.gbif_id,
                sheet.identification_source,
                sheet.confidence_score,
                sheet.min_soil_humidity,
                sheet.max_soil_humidity,
                sheet.min_lumens,
                sheet.max_lumens,
                sheet.lumens_unit,
                sheet.min_air_humidity,
                sheet.max_air_humidity,
                sheet.min_temperature,
                sheet.max_temperature,
                sheet.min_watering_days_frequency,
                sheet.max_watering_days_frequency,
                sheet.ideal_soil_humidity_after_watering,
                sheet.ideal_air_humidity,
                sheet.ideal_lumens,
                sheet.ideal_temperature,
                sheet.ideal_watering_days_frequency,
                sheet.photo,
                sheet.created_at or None,
                sheet.updated_at or None,
            )
        )
        sheet.id = row[0][0]
        return sheet.id

    def create_express_analysis_report(
            self,
            plant_id: int,
            soil_humidity_mean: float | None,
            temperature_mean: float | None,
            air_humidity_mean: float | None,
            lumens_mean: float | None,
            soil_humidity_data: str | None,
            temperature_data: str | None,
            air_humidity_data: str | None,
            lumens_data: str | None,
            analysis_type: str = "express",
    ) -> int:
        row = self._db.query(
            """
            INSERT INTO express_analysis_report (
                plant_id,
                analysis_type,
                soil_humidity_mean, lumens_mean, air_humidity_mean, temperature_mean,
                soil_humidity_data, lumens_data, air_humidity_data, temperature_data
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (
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
            )
        )
        return row[0][0]

    def list_all_express_reports(self, user_id: int) -> List[ExpressAnalysisReport]:
        db = self._db
        rows = db.query("""
            SELECT
              ear.id,
              ear.plant_id,
              ear.analysis_type,
              ear.soil_humidity_mean,
              ear.lumens_mean,
              ear.air_humidity_mean,
              ear.temperature_mean,
              ear.soil_humidity_data,
              ear.lumens_data,
              ear.air_humidity_data,
              ear.temperature_data,
              ear.created_at
            FROM express_analysis_report ear
            JOIN maintenance_sheet ms ON ear.plant_id = ms.id
            WHERE ms.user_id = %s
            ORDER BY ear.id;
        """, (user_id,))
        return [ExpressAnalysisReport(*row) for row in rows]

    def get_express_analysis_report_by_id(self, report_id: int) -> Optional[ExpressAnalysisReport]:
        rows = self._db.query(
            """
            SELECT
              id,
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
            FROM express_analysis_report
            WHERE id = %s
            """,
            (report_id,)
        )
        if not rows:
            return None
        return ExpressAnalysisReport(*rows[0])

    def delete_express_analysis_report_by_id(self, report_id: int) -> bool:
        result = self._db.execute(
            """
            DELETE FROM express_analysis_report
            WHERE id = %s
            """,
            (report_id,)
        )
        return result.rowcount > 0

    def create_watering_report(
            self,
            plant_id: int,
            soil_humidity_mean: float,
            sigma3: float,
            target_humidity: float,
            soil_humidity_data: str | None,
            pump_data: str | None,
    ) -> int:
        row = self._db.query(
            """
            INSERT INTO watering_report (
                plant_id,
                soil_humidity_mean,
                sigma3,
                target_humidity,
                soil_humidity_data,
                pump_data
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (
                plant_id,
                soil_humidity_mean,
                sigma3,
                target_humidity,
                soil_humidity_data,
                pump_data,
            )
        )
        return row[0][0]

    def get_watering_report_by_id(self, report_id: int) -> Optional[WateringReport]:
        rows = self._db.query(
            """
            SELECT
              id,
              plant_id,
              soil_humidity_mean,
              sigma3,
              target_humidity,
              soil_humidity_data,
              pump_data,
              created_at
            FROM watering_report
            WHERE id = %s
            """,
            (report_id,)
        )
        if not rows:
            return None
        return WateringReport(*rows[0])

    def delete_watering_report_by_id(self, report_id: int) -> bool:
        result = self._db.execute(
            """
            DELETE FROM watering_report
            WHERE id = %s
            """,
            (report_id,)
        )
        return result.rowcount > 0



    def list_maintenance_summaries(
        self,
        plant_id: int,
        user_id: int,
        limit: int = 20,
        before: Optional[datetime] = None
    ) -> List[MaintenanceSummary]:
        db = self._db

        if before is None:
            before = datetime.now(timezone.utc)

        rows = db.query(
            """
            SELECT *
            FROM (
                SELECT
                    ear.id,
                    ear.plant_id,
                    ear.created_at,
                    'express' AS type,
                    ear.soil_humidity_mean,
                    ear.lumens_mean,
                    ear.air_humidity_mean,
                    ear.temperature_mean
                FROM express_analysis_report ear
                JOIN maintenance_sheet ms ON ear.plant_id = ms.id
                WHERE ear.created_at < %s
                    AND ear.plant_id = %s
                    AND ms.user_id = %s

                UNION ALL

                SELECT
                    wr.id,
                    wr.plant_id,
                    wr.created_at,
                    'watering' AS type,
                    wr.soil_humidity_mean,
                    NULL AS lumens_mean,
                    NULL AS air_humidity_mean,
                    NULL AS temperature_mean
                FROM watering_report wr
                JOIN maintenance_sheet ms ON wr.plant_id = ms.id
                WHERE wr.created_at < %s
                    AND wr.plant_id = %s
                    AND ms.user_id = %s
            ) AS merged
            ORDER BY created_at DESC
            LIMIT %s;
            """,
            (before, plant_id, user_id, before, plant_id, user_id, limit)
        )

        return [MaintenanceSummary(*row) for row in rows]

    def list_all_tokens(self) -> List[RefreshToken]:
        db = self._db
        rows = db.query(
            "SELECT id, user_id, email, expires_at, revoked "
            "FROM refresh_tokens ORDER BY expires_at DESC;"
        )
        return [RefreshToken(*row) for row in rows]

    def create_token(self, token: RefreshToken) -> int:
        db = self._db
        row = db.query(
            "INSERT INTO refresh_tokens (user_id, email, expires_at, revoked) "
            "VALUES (%s, %s, %s, %s) RETURNING id;",
            (token.user_id, token.email, token.expires_at, token.revoked),
        )
        token.id = row[0][0]
        return token.id

    def get_token_by_id(self, id_: str) -> Optional[RefreshToken]:
        db = self._db
        row = db.query(
            "SELECT id, user_id, email, expires_at, revoked "
            "FROM refresh_tokens WHERE id = %s;", (id_,)
        )
        if not row:
            return None
        return RefreshToken(*row[0])

    def delete_token(self, id_: str) -> bool:
        db = self._db
        row = db.query("DELETE FROM refresh_tokens WHERE id = %s RETURNING id;", (id_,))
        return bool(row)

    def revoke_token(self, id_: str) -> bool:
        db = self._db
        row = db.query(
            "UPDATE refresh_tokens SET revoked = TRUE WHERE id = %s RETURNING id;", (id_,)
        )
        return bool(row)

    def rotate_token(self, old_id: str, new_token: RefreshToken) -> int:
        self.delete_token(old_id)
        return self.create_token(new_token)

    def get_or_create_user(self, email: str, google_sub: str) -> User:
        db = self._db

        # 1. Lookup par email
        row = db.query(
            "SELECT id, google_sub, email, created_at FROM users WHERE email = %s;",
            (email,)
        )
        if row:
            r = row[0]
            return User(id=r[0], google_sub=r[1], email=r[2], created_at=r[3])

        # 2. Insert si inexistant
        row = db.query(
            "INSERT INTO users (google_sub, email) VALUES (%s, %s) "
            "RETURNING id, google_sub, email, created_at;",
            (google_sub, email)
        )
        r = row[0]
        return User(id=r[0], google_sub=r[1], email=r[2], created_at=r[3])

    def get_user_by_email(self, email: str) -> Optional[User]:
        db = self._db
        row = db.query(
            "SELECT id, google_sub, email, created_at FROM users WHERE email = %s;",
            (email,)
        )
        if not row:
            return None

        r = row[0]
        return User(
            id=r[0],
            google_sub=r[1],
            email=r[2],
            created_at=r[3]
        )

    def delete_maintenance_sheet_for_user(self, sheet_id: int) -> bool:
        result = self._db.execute(
            "DELETE FROM maintenance_sheet WHERE id = %s;",
            (sheet_id,)
        )
        return result.rowcount > 0

    def get_last_feeled_humidity(self, user_id: int) -> List[LastFeeledHumidity]:
        """
        Récupère pour chaque plante de l'utilisateur:
        - Le dernier watering avec humidité > cible
        - La dernière analyse express avec humidité > cible
        - Les valeurs cibles (humidité et fréquence d'arrosage)
        
        Les cibles sont calculées:
        - ideal_soil_humidity_after_watering si présent, sinon moyenne min/max
        - ideal_watering_days_frequency si présent, sinon moyenne min/max
        """
        rows = self._db.query(
            """
            WITH plant_targets AS (
                SELECT 
                    ms.id as plant_id,
                    ms.name as plant_name,
                    ms.photo,
                    ms.ideal_soil_humidity_after_watering,
                    ms.min_soil_humidity,
                    ms.max_soil_humidity,
                    ms.ideal_air_humidity,
                    ms.min_air_humidity,
                    ms.max_air_humidity,
                    ms.ideal_temperature,
                    ms.min_temperature,
                    ms.max_temperature,
                    ms.ideal_watering_days_frequency,
                    ms.min_watering_days_frequency,
                    ms.max_watering_days_frequency,
                    COALESCE(
                        ms.ideal_soil_humidity_after_watering::float,
                        (ms.min_soil_humidity + ms.max_soil_humidity) / 2.0
                    ) as target_humidity,
                    COALESCE(
                        ms.ideal_air_humidity::float,
                        (ms.min_air_humidity + ms.max_air_humidity) / 2.0
                    ) as target_air_humidity,
                    COALESCE(
                        ms.ideal_temperature::float,
                        (ms.min_temperature + ms.max_temperature) / 2.0
                    ) as target_temperature,
                    COALESCE(
                        ms.ideal_watering_days_frequency::float,
                        (ms.min_watering_days_frequency + ms.max_watering_days_frequency) / 2.0
                    ) as target_watering_days
                FROM maintenance_sheet ms
                WHERE ms.user_id = %s
            ),
            ranked_watering_above_target AS (
                SELECT 
                    wr.plant_id,
                    wr.id,
                    wr.created_at,
                    wr.soil_humidity_mean,
                    pt.target_humidity,
                    ROW_NUMBER() OVER (
                        PARTITION BY wr.plant_id 
                        ORDER BY wr.created_at DESC
                    ) as rn
                FROM watering_report wr
                INNER JOIN plant_targets pt ON wr.plant_id = pt.plant_id
                WHERE wr.soil_humidity_mean > pt.target_humidity
            ),
            ranked_express_above_target AS (
                SELECT 
                    ear.plant_id,
                    ear.id,
                    ear.created_at,
                    ear.soil_humidity_mean,
                    pt.target_humidity,
                    ROW_NUMBER() OVER (
                        PARTITION BY ear.plant_id 
                        ORDER BY ear.created_at DESC
                    ) as rn
                FROM express_analysis_report ear
                INNER JOIN plant_targets pt ON ear.plant_id = pt.plant_id
                WHERE ear.soil_humidity_mean > pt.target_humidity
            ),
            ranked_watering_all AS (
                SELECT 
                    wr.plant_id,
                    wr.id,
                    wr.created_at,
                    wr.soil_humidity_mean,
                    ROW_NUMBER() OVER (
                        PARTITION BY wr.plant_id 
                        ORDER BY wr.created_at DESC
                    ) as rn
                FROM watering_report wr
                INNER JOIN plant_targets pt ON wr.plant_id = pt.plant_id
            ),
            ranked_express_all AS (
                SELECT 
                    ear.plant_id,
                    ear.id,
                    ear.created_at,
                    ear.soil_humidity_mean,
                    ear.air_humidity_mean,
                    ear.temperature_mean,
                    ROW_NUMBER() OVER (
                        PARTITION BY ear.plant_id 
                        ORDER BY ear.created_at DESC
                    ) as rn
                FROM express_analysis_report ear
                INNER JOIN plant_targets pt ON ear.plant_id = pt.plant_id
            )
            SELECT 
                pt.plant_id,
                pt.plant_name,
                pt.photo,
                pt.ideal_soil_humidity_after_watering,
                pt.min_soil_humidity,
                pt.max_soil_humidity,
                pt.target_humidity,
                pt.ideal_air_humidity,
                pt.min_air_humidity,
                pt.max_air_humidity,
                pt.target_air_humidity,
                pt.ideal_temperature,
                pt.min_temperature,
                pt.max_temperature,
                pt.target_temperature,
                pt.ideal_watering_days_frequency,
                pt.min_watering_days_frequency,
                pt.max_watering_days_frequency,
                pt.target_watering_days,
                rwat.id as last_watering_above_target_id,
                rwat.created_at as last_watering_above_target_date,
                rwat.soil_humidity_mean as last_watering_above_target_humidity,
                reat.id as last_express_above_target_id,
                reat.created_at as last_express_above_target_date,
                reat.soil_humidity_mean as last_express_above_target_humidity,
                rwa.id as last_watering_id,
                rwa.created_at as last_watering_date,
                rwa.soil_humidity_mean as last_watering_humidity,
                rea.id as last_express_id,
                rea.created_at as last_express_date,
                rea.soil_humidity_mean as last_express_soil_humidity,
                rea.air_humidity_mean as last_express_air_humidity,
                rea.temperature_mean as last_express_temperature
            FROM plant_targets pt
            LEFT JOIN ranked_watering_above_target rwat ON rwat.plant_id = pt.plant_id AND rwat.rn = 1
            LEFT JOIN ranked_express_above_target reat ON reat.plant_id = pt.plant_id AND reat.rn = 1
            LEFT JOIN ranked_watering_all rwa ON rwa.plant_id = pt.plant_id AND rwa.rn = 1
            LEFT JOIN ranked_express_all rea ON rea.plant_id = pt.plant_id AND rea.rn = 1
            ORDER BY pt.plant_id;
            """,
            (user_id,)
        )
        
        return [
            LastFeeledHumidity(
                plant_id=row[0],
                plant_name=row[1],
                photo=row[2],
                ideal_soil_humidity_after_watering=row[3],
                min_soil_humidity=row[4],
                max_soil_humidity=row[5],
                target_humidity=row[6],
                ideal_air_humidity=row[7],
                min_air_humidity=row[8],
                max_air_humidity=row[9],
                target_air_humidity=row[10],
                ideal_temperature=row[11],
                min_temperature=row[12],
                max_temperature=row[13],
                target_temperature=row[14],
                ideal_watering_days_frequency=row[15],
                min_watering_days_frequency=row[16],
                max_watering_days_frequency=row[17],
                target_watering_days=row[18],
                last_watering_above_target_id=row[19],
                last_watering_above_target_date=row[20],
                last_watering_above_target_humidity=row[21],
                last_express_above_target_id=row[22],
                last_express_above_target_date=row[23],
                last_express_above_target_humidity=row[24],
                last_watering_id=row[25],
                last_watering_date=row[26],
                last_watering_humidity=row[27],
                last_express_id=row[28],
                last_express_date=row[29],
                last_express_soil_humidity=row[30],
                last_express_air_humidity=row[31],
                last_express_temperature=row[32]
            )
            for row in rows
        ]









