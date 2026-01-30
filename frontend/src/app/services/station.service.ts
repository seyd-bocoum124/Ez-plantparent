import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {firstValueFrom, Observable, tap} from 'rxjs';
import { environment } from '../../environments/environment';

export interface Station {
  id: number;
  name: string;
  location: string;
  created_at: string;
  mac_adress?: string;
}

export interface SendCommandBody {
  type: string;
  action: string;
  duration?: number;
}


@Injectable({
  providedIn: 'root'
})
      export class StationService {
        private apiUrl = `${environment.apiUrl}/stations`;

        // Signal pour la MAC address de la station active
        activeStationMacAddress = signal<string | null>(null);
        maintenanceSchedule = signal<any[]>([]);

        constructor(private http: HttpClient) {
          // Charger depuis localStorage au démarrage
          const savedMac = localStorage.getItem('active_station_mac');
          if (savedMac) this.activeStationMacAddress.set(savedMac);
        }

        getStations(): Observable<Station[]> {
          return this.http.get<Station[]>(this.apiUrl);
        }

        getDailyMaintenanceSchedules(): Observable<any[]> {
          return this.http.get<Station[]>(`${environment.apiUrl}/maintenance-schedule`);
        }

        getExpressAnalysisReportById(report_id: number): Observable<Station[]> {
          return this.http.get<Station[]>(`${environment.apiUrl}/reports/express-analysis/${report_id}`);
        }

        getWateringReportById(report_id: number): Observable<Station[]> {
          return this.http.get<Station[]>(`${environment.apiUrl}/reports/watering/${report_id}`);
        }

        deleteWateringReport(reportId: number): Promise<void> {
          return firstValueFrom(this.http.delete<void>(`${environment.apiUrl}/reports/watering/${reportId}`));
        }



        async deleteExpressAnalysisReport(reportId: number): Promise<void> {
          return firstValueFrom(this.http.delete<void>(`${environment.apiUrl}/reports/express-analysis/${reportId}`));
        }


        sendCommand(stationId: string, body: SendCommandBody): Observable<any> {
          const url = `${this.apiUrl}/${stationId}/command`;
          return this.http.post<any>(url, body);
        }

        pairStation(pairingCode: string): Observable<any> {
          const url = `${this.apiUrl}-pairing`;
          return this.http.put<any>(url, { pairing_code: pairingCode }).pipe(
            tap(() => {
              // Après le pairing, rafraîchir la station active
              this.refreshActiveStation();
            })
          );
        }

        /**
         * Rafraîchit la station active en récupérant la liste des stations
         * et en prenant la première (la plus récemment pairée)
         */
        refreshActiveStation(): void {
          this.getStations().subscribe({
            next: (stations) => {
              if (stations.length > 0) {
                console.log('nouvelle station active rafraîchie après login/pairing');
                const firstStation = stations[0];
                this.setActiveStation(firstStation);
              } else {
                this.clearActiveStation();
              }
            },
            error: (err) => {
              console.error('Erreur lors du rafraîchissement de la station active:', err);
              this.clearActiveStation();
            }
          });
        }

        /**
         * Définit la station active et persiste dans localStorage
         */
        private setActiveStation(station: Station): void {
          const macAddress = station.mac_adress || `station_${station.id}`;

          this.activeStationMacAddress.set(macAddress);
          localStorage.setItem('active_station_mac', macAddress);
        }

        /**
         * Efface la station active
         */
        private clearActiveStation(): void {
          this.activeStationMacAddress.set(null);
          localStorage.removeItem('active_station_mac');
        }

      }
