import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export type SeriesPoint = number | null;
export type Series = { name: string; data: SeriesPoint[] };

@Injectable({ providedIn: 'root' })
export class ReportSeriesService {
  private readonly MAX_POINTS = 200;

  private _series$ = new BehaviorSubject<Series[]>([
    { name: 'Soil humidity', data: [] },
    { name: 'Air humidity', data: [] },
    { name: 'Temperature', data: [] }
  ]);
  public readonly series$ = this._series$.asObservable();

  // remplace l'état complet ; accepte déjà des nulls
  setInitialSeries(series: Series[]) {
    const trimmed = series.map(s => ({
      name: s.name,
      data: (s.data || []).slice(-this.MAX_POINTS).map(v => (v === undefined ? null : v))
    }));
    this._series$.next(trimmed);
  }


  addPoints(soil?: number | null, air?: number | null, temp?: number | null, pump?: number | null, target_humidity?: number | null) {
    const cur = this._series$.getValue().map(s => ({ name: s.name, data: s.data.slice() }));

    for (const s of cur) {
      if (s.name === 'Soil humidity') s.data.push(soil === undefined ? null : (soil === null ? null : Number(soil)));
      if (s.name === 'Air humidity') s.data.push(air === undefined ? null : (air === null ? null : Number(air)));
      if (s.name === 'Temperature') s.data.push(temp === undefined ? null : (temp === null ? null : Number(temp)));
      if (s.name === 'Pump') s.data.push(temp === undefined ? null : (pump === null ? null : Number(pump)));
      if (s.name === 'Target Humidity') s.data.push(target_humidity === undefined ? null : (target_humidity === null ? null : Number(target_humidity)));

      if (s.data.length > this.MAX_POINTS) s.data.splice(0, s.data.length - this.MAX_POINTS);
    }

    this._series$.next(cur);
  }
}
