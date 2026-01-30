import { Injectable, OnDestroy, NgZone } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { Observable, Subject, timer, BehaviorSubject, Subscription } from 'rxjs';
import { retryWhen, switchMap, finalize } from 'rxjs/operators';

import { environment } from '../../environments/environment';
import {AuthService} from './auth/auth.service';

@Injectable({ providedIn: 'root' })
export class WebsocketService implements OnDestroy {
  private socket$: WebSocketSubject<any> | null = null;
  private socketSubscription: Subscription | null = null;

  // Public observable: consumers subscribe() to receive backend messages
  private incoming$ = new Subject<any>();
  private connectedSubject = new BehaviorSubject<boolean>(false);
  public connected$ = this.connectedSubject.asObservable();

  private url = '/ws';

  setStationId(stationId: number | string) {
    this.url = `/ws/stations/${stationId}`;
  }


  private reconnectInitial = 1000; // ms
  private maxReconnect = 30000; // ms

  constructor(private ngZone: NgZone, private auth: AuthService) {}

  /**
   * Connect and return an observable of incoming messages.
   * Reuses the existing socket if already open.
   */
  connect(): Observable<any> {
    // Vérifier si la connexion existante est morte ou fermée
    if (!this.socket$ || (this.socket$ as any).closed || !this.connectedSubject.value) {
      console.log('[WS] Opening new socket connection');
      this.close(); // Nettoyer l'ancienne connexion si elle existe
      this.openSocket();
    } else {
      console.log('[WS] Reusing existing socket connection');
    }
    return this.incoming$.asObservable();
  }

  setUrl(url: string) {
    this.url = url;
  }

  private openSocket() {
    try { this.socketSubscription?.unsubscribe(); } catch {}
    try { this.socket$?.complete(); } catch {}

    const token = this.auth.getAccessToken();
    let fullUrl: string;

    if (this.url.startsWith('ws')) {
      fullUrl = `${this.url}?token=${token}`;
    } else if (environment.wsUrl && environment.enableMobileFeatures) {
      // Mobile: utiliser l'URL absolue du backend
      fullUrl = `${environment.wsUrl}${this.url}?token=${token}`;
    } else {
      // Web: utiliser location.host
      const scheme = location.protocol === 'https:' ? 'wss' : 'ws';
      fullUrl = `${scheme}://${location.host}${this.url}?token=${token}`;
    }

    console.log('[WS] Connecting to:', fullUrl);

    this.socket$ = webSocket({
      url: fullUrl,
      deserializer: ({ data }) => {
        try { return JSON.parse(data); } catch { return data; }
      },
      serializer: msg => JSON.stringify(msg),
      openObserver: {
        next: () => {
          console.log('[WS] ✅ Connected');
        }
      },
      closeObserver: {
        next: () => {
          console.log('[WS] ❌ Closed');
        }
      }
    });

    // Subscribe and forward messages into Angular zone so UI updates are detected
    this.socketSubscription = this.socket$
      .pipe(
        retryWhen(errors =>
          errors.pipe(
            switchMap((err, i) =>
              timer(Math.min(this.maxReconnect, Math.floor(this.reconnectInitial * Math.pow(1.5, i))))
            )
          )
        ),
        finalize(() => {
          // finalize runs outside NgZone; ensure next executes inside zone
          this.ngZone.run(() => this.connectedSubject.next(false));
        })
      )
      .subscribe({
        next: (msg) => {
          // forward inside Angular zone to trigger change detection in subscribers
          this.ngZone.run(() => {
            try { this.incoming$.next(msg); } catch (e) { console.debug('[WS] forward error', e); }
            this.connectedSubject.next(true);
          });
        },
        error: (err) => {
          console.error('[WS] ❌ WebSocket ERROR:', err);
          console.error('[WS] Error details:', {
            message: err.message,
            type: err.type,
            target: err.target
          });
          this.ngZone.run(() => this.connectedSubject.next(false));
        },
        complete: () => {
          console.log('[WS] WebSocket connection completed');
          this.ngZone.run(() => this.connectedSubject.next(false));
        }
      });
  }

  /**
   * Send an object to the server. If socket is not ready it opens it and retries shortly after.
   */
  send(obj: any) {
    if (this.socket$ && !(this.socket$ as any).closed) {
      try { this.socket$.next(obj); } catch (e) { console.debug('[WS] send error', e); }
      return;
    }

    this.openSocket();
    setTimeout(() => {
      if (this.socket$ && !(this.socket$ as any).closed) {
        try { this.socket$.next(obj); } catch (e) { console.debug('[WS] delayed send error', e); }
      }
    }, 200);
  }

  close() {
    try { this.socketSubscription?.unsubscribe(); } catch {}
    try { this.socket$?.complete(); } catch {}
    this.socketSubscription = null;
    this.socket$ = null;
    this.connectedSubject.next(false);
  }

  ngOnDestroy(): void {
    this.close();
    try { this.incoming$.complete(); } catch {}
    try { this.connectedSubject.complete(); } catch {}
  }
}
