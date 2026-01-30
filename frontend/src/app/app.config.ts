import {
  ApplicationConfig, inject, provideAppInitializer,
  provideBrowserGlobalErrorListeners,
  provideZonelessChangeDetection
} from '@angular/core';
import { provideRouter } from '@angular/router';
import {provideHttpClient, withInterceptorsFromDi} from '@angular/common/http';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { routes } from './app.routes';
import {AuthInterceptor} from './services/auth/auth-interceptor';

function withResolveTimeout<T>(p: Promise<T>, ms = 2000): Promise<T | undefined> {
  return Promise.race([
    p.then(r => r).catch(() => undefined),
    new Promise<T | undefined>(resolve => setTimeout(() => resolve(undefined), ms))
  ]);
}



export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideZonelessChangeDetection(),
    provideRouter(routes),
    provideHttpClient(
      withInterceptorsFromDi(),
    ),
    { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }
  ]
};
