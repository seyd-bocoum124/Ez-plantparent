// src/app/auth/google-login.component.ts
import { Component, AfterViewInit, OnDestroy } from '@angular/core';
import { Capacitor } from '@capacitor/core';
import { GoogleAuth } from '@codetrix-studio/capacitor-google-auth';
import { environment } from '../../../environments/environment';
import {AuthService} from '../../services/auth/auth.service';


@Component({
  selector: 'app-google-login',
  template: `
    <div id="g_id_onload"></div>
    <div id="google-signin-button"></div>
  `,
  styles: [`
    #google-signin-button {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 40px;
    }
  `]
})
export class GoogleSigninComponent implements AfterViewInit, OnDestroy {
  private clientId = environment.googleClientId; // Utilise le bon Client ID selon l'environnement
  private isNative = Capacitor.isNativePlatform();

  constructor(private auth: AuthService) {
    // L'initialisation est gérée automatiquement par Capacitor via capacitor.config.ts
  }

  ngAfterViewInit(): void {
    if (this.isNative) {
      // Sur mobile, créer un bouton personnalisé
      this.renderNativeButton();
    } else {
      // Sur web, utiliser le SDK Google classique
      this.initWebGoogleSignIn();
    }
  }

  private renderNativeButton(): void {
    const buttonDiv = document.getElementById('google-signin-button');
    if (!buttonDiv) return;

    const button = document.createElement('button');
    button.innerHTML = `
      <div style="display: flex; align-items: center; gap: 8px; padding: 8px 16px; background: white; border: 1px solid #dadce0; border-radius: 4px; cursor: pointer; font-family: 'Roboto', sans-serif; font-size: 14px; font-weight: 500; color: #3c4043;">
        <svg width="18" height="18" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
          <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
          <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
          <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
          <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
        </svg>
        <span>Se connecter avec Google</span>
      </div>
    `;
    button.onclick = () => this.signInNative();
    button.style.border = 'none';
    button.style.background = 'transparent';
    button.style.cursor = 'pointer';
    button.style.padding = '0';

    buttonDiv.appendChild(button);
  }

  private async signInNative(): Promise<void> {
    try {
      console.log('Début du sign-in natif Google...');

      // Vérifier si l'utilisateur est déjà connecté et le déconnecter d'abord
      try {
        await GoogleAuth.signOut();
      } catch (e) {
        // Ignorer l'erreur si l'utilisateur n'était pas connecté
        console.log('Pas de session précédente à nettoyer');
      }

      // Lancer le flow d'authentification
      const result = await GoogleAuth.signIn();
      console.log('Google Sign-In natif réussi:', result);

      // Utiliser l'ID token pour l'authentification backend
      const idToken = result.authentication?.idToken;
      if (idToken) {
        console.log('ID Token reçu, authentification avec le backend...');
        await this.auth.loginWithGoogle(idToken);
      } else {
        console.error('Pas d\'ID token reçu dans la réponse');
        alert('Erreur: Impossible de récupérer les informations de connexion');
      }
    } catch (error: any) {
      console.error('Erreur Google Sign-In natif:', error);

      // Afficher un message d'erreur user-friendly
      if (error.error === 'popup_closed_by_user') {
        console.log('L\'utilisateur a annulé la connexion');
      } else {
        alert('Erreur de connexion Google: ' + (error.message || 'Erreur inconnue'));
      }
    }
  }

  private initWebGoogleSignIn(): void {
    // Attendre que le script Google soit chargé
    this.waitForGoogleScript().then(() => {
      try {
        // @ts-ignore global provided by the loaded GSI script
        google.accounts.id.initialize({
          client_id: this.clientId,
          callback: (resp: any) => this.handleCredentialResponse(resp)
        });

        const buttonDiv = document.getElementById('google-signin-button');
        if (buttonDiv) {
          // @ts-ignore
          google.accounts.id.renderButton(
            buttonDiv,
            { theme: 'outline', size: 'large', width: 250 }
          );
        }
      } catch (error) {
        console.error('Erreur initialisation Google Sign-In web:', error);
      }
    }).catch(err => {
      console.error('Script Google non chargé:', err);
    });
  }

  private waitForGoogleScript(): Promise<void> {
    return new Promise((resolve, reject) => {
      let attempts = 0;
      const maxAttempts = 50;

      const checkGoogle = () => {
        attempts++;
        // @ts-ignore
        if (typeof google !== 'undefined' && google.accounts?.id) {
          resolve();
        } else if (attempts >= maxAttempts) {
          reject(new Error('Script Google non disponible'));
        } else {
          setTimeout(checkGoogle, 100);
        }
      };

      checkGoogle();
    });
  }

  ngOnDestroy(): void {
    // cleanup if needed
  }

  private async handleCredentialResponse(resp: any) {
    const idToken = resp?.credential;
    if (!idToken) return;
    try {
      await this.auth.loginWithGoogle(idToken);
    } catch (err) {
      console.error('LoginWithGoogle failed', err);
    }
  }
}

