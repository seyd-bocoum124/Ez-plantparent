import {Injectable, signal} from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {firstValueFrom} from 'rxjs';

export interface MaintenanceSheet {
  id: number;
  user_id: number;

  name: string;
  scientific_name: string;
  common_name: string;

  taxonkey: string;
  taxon_rank: string;
  identification_source: string;
  confidence_score: number;

  min_soil_humidity: number;
  max_soil_humidity: number;

  min_lumens: number;
  max_lumens: number;
  lumens_unit: string;

  min_air_humidity: number;
  max_air_humidity: number;

  min_temperature: number;
  max_temperature: number;

  min_watering_days_frequency: number;
  max_watering_days_frequency: number;

  ideal_soil_humidity_after_watering?: number;
  ideal_air_humidity?: number;
  ideal_lumens?: number;
  ideal_temperature?: number;
  ideal_watering_days_frequency?: number;

  photo_base64?: string;

  created_at: string;
  updated_at: string;
}

export interface MaintenanceSummary {
  id: number;
  plant_id: number;
  type: 'express' | 'watering';

  soil_humidity_mean?: number;
  lumens_mean?: number;
  air_humidity_mean?: number;
  temperature_mean?: number;

  created_at: string;
}


import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
      export class MaintenanceSheetService {
        private apiUrl = `${environment.apiUrl}/maintenance-sheets`;

        sheets = signal<MaintenanceSheet[]>([]);
        summaries = signal<MaintenanceSummary[]>([]);
        errors = signal<{ load?: any; delete?: any; create?: any }>({});


        constructor(private http: HttpClient) {}

        async loadSummaries(plantId:number): Promise<void> {
          const url = `${environment.apiUrl}/plants/${plantId}/reports/resumes`;
          try {
            const data = await firstValueFrom(
              this.http.get<MaintenanceSummary[]>(url)
            );
            this.summaries.set(data);
            this.errors.update(e => ({ ...e, load: null }));
          } catch (err) {
            console.error('Erreur lors du chargement des résumés', err);
            this.errors.update(e => ({ ...e, load: err }));
          }
        }

        async loadMaintenanceSheets(): Promise<void> {
          try {
            const data = await firstValueFrom(
              this.http.get<MaintenanceSheet[]>(this.apiUrl)
            );
            this.sheets.set(data);
            this.errors.update(e => ({ ...e, load: null }));
          } catch (err) {
            console.error('Erreur lors du chargement des feuilles', err);
            this.errors.update(e => ({ ...e, load: err }));
          }
        }

        async deleteMaintenanceSheet(id: number): Promise<void> {
          try {
            await firstValueFrom(this.http.delete(`${this.apiUrl}/${id}`));
            await this.loadMaintenanceSheets();
            this.errors.update(e => ({ ...e, delete: null }));
          } catch (err) {
            console.error('Erreur lors de la suppression', err);
            this.errors.update(e => ({ ...e, delete: err }));
          }
        }

        createMaintenanceSheet(data: any) {
          return this.http.post<MaintenanceSheet>(this.apiUrl, data);
        }

        identifyPlantFromBlobs(photos: Blob[]) {
          const formData = new FormData();
          photos.forEach((photo, index) => {
            formData.append('files', photo, `photo_${index + 1}.png`);
          });

          const url = `${environment.apiUrl}/plant-identifications`;

          return this.http.post<any>(url, formData);
        }

      }


