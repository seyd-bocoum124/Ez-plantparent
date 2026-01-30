import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface GbifMatchResult {
  usageKey: number;
  scientificName: string;
  matchType: string;
  confidence: number;
  status: string;
  note?: string;
}

@Injectable({
  providedIn: 'root'
})
export class GbifService {
  private apiUrl = 'https://api.gbif.org';

  constructor(private http: HttpClient) {}

  matchPlantName(name: string): Observable<GbifMatchResult> {
    const params = new HttpParams().set('q', name);
    return this.http.get<GbifMatchResult>(this.apiUrl + '/v1/species/match', { params });
  }

  speciesSearch(name: string): Observable<GbifMatchResult> {
    const params = new HttpParams().set('q', name).set("limit", 5);
    return this.http.get<GbifMatchResult>(this.apiUrl + '/v1/species/search', { params });
  }


}

