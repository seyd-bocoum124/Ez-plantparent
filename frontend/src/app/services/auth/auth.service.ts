import { Injectable, inject } from '@angular/core';
import {BehaviorSubject, firstValueFrom, timeout} from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import {StationService} from '../station.service';
import {environment} from '../../../environments/environment';

export type User = { id?: string; email?: string; [k: string]: any } | null;

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private stationService = inject(StationService);
  private accessToken: string | null = null;
  private userSubject = new BehaviorSubject<User>(null);
  user$ = this.userSubject.asObservable();
  private bc: BroadcastChannel | null = typeof BroadcastChannel !== 'undefined' ? new BroadcastChannel('auth') : null;

  constructor() {
    console.log('AuthService instantiated');
    if (this.bc) {
      this.bc.onmessage = (ev) => {
        if (ev.data === 'logout') this.clearAuthLocal();
        if (ev.data?.type === 'refresh') {
          // Don't call setAccessToken to avoid re-broadcasting
          this.accessToken = ev.data.token;
          this.userSubject.next(ev.data.user);
        }
      };
    }
  }

  getAccessToken(): string | null {
    return this.accessToken;
  }

  private lastTokenRefresh = 0;

  setAccessToken(token: string | null, user: User = null, shouldRefreshStation = true) {
    console.log("token set!")
    this.accessToken = token;
    this.userSubject.next(user);
    if (this.bc) this.bc.postMessage({ type: 'refresh', token, user });

    // Only refresh station once per minute to avoid loops
    if (token && shouldRefreshStation) {
      const now = Date.now();
      if (now - this.lastTokenRefresh > 60000) {
        this.lastTokenRefresh = now;
        this.stationService.refreshActiveStation();
      }
    }
  }

  clearAuthLocal() {
    this.accessToken = null;
    this.userSubject.next(null);
  }

  // @TODO debug
  async silentRefresh(): Promise<boolean> {
    try {
      const resp: any = await firstValueFrom(
        this.http.post(`${environment.apiUrl}/auth/refresh`, {}, { withCredentials: true }).pipe(timeout(3000))
      );
      // Don't refresh station on silent token refresh (only on explicit login)
      this.setAccessToken(resp?.access_token ?? null, resp?.user ?? null, false);
      return !!resp?.access_token;
    } catch (err) {
      this.clearAuthLocal();
      return false;
    }
  }


  async loginWithGoogle(idToken: string): Promise<void> {
    const resp: any = await firstValueFrom(
      this.http.post(`${environment.apiUrl}/auth/google`, {}, {
        headers: { Authorization: 'Bearer ' + idToken },
        withCredentials: true
      })
    );
    this.setAccessToken(resp?.access_token ?? null, resp?.user ?? null);
    await this.router.navigate(['/accueil']);
  }

  async logout(): Promise<void> {
    try {
      await firstValueFrom(this.http.post(`${environment.apiUrl}/auth/logout`, {}, { withCredentials: true }));
    } finally {
      this.clearAuthLocal();
      if (this.bc) this.bc.postMessage('logout');
    }
  }
}
