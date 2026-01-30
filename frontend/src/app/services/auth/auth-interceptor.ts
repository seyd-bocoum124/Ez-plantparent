import { Injectable, Injector } from '@angular/core';
import {
  HttpInterceptor,
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, from, throwError, firstValueFrom } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthService } from './auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  private refreshInProgress: Promise<boolean> | null = null;

  constructor(private injector: Injector) {}

  private get auth(): AuthService {
    return this.injector.get(AuthService);
  }

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    console.log('[INTERCEPT] entering intercept for', req.method, req.urlWithParams);

    const isGbif = req.url.startsWith('https://api.gbif.org');

    if (isGbif) {
      return next.handle(req);
    }



    const token = this.auth.getAccessToken();
    console.log('[INTERCEPT] current access token present:', !!token);

    const authReq = token
      ? req.clone({ headers: req.headers.set('Authorization', `Bearer ${token}`) })
      : req;

    return next.handle(authReq).pipe(
      catchError((err: HttpErrorResponse) => {
        console.log('[INTERCEPT] caught error', err.status, 'for', req.urlWithParams);
        if (err.status === 401) {
          return from(this.handle401(req, next));
        }
        return throwError(() => err);
      })
    );
  }

  private async handle401(req: HttpRequest<any>, next: HttpHandler): Promise<HttpEvent<any>> {
    if (!this.refreshInProgress) {
      this.refreshInProgress = this.auth.silentRefresh().finally(() => (this.refreshInProgress = null));
    }

    try {
      await this.refreshInProgress;
      const newToken = this.auth.getAccessToken();
      const retryReq = newToken
        ? req.clone({ headers: req.headers.set('Authorization', `Bearer ${newToken}`) })
        : req;

      return await firstValueFrom(next.handle(retryReq));
    } catch (e) {
      this.auth.clearAuthLocal();
      throw e;
    }
  }
}


