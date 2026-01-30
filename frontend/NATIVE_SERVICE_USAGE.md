# Exemple d'utilisation du NativeService

## Dans un composant Angular

```typescript
import { Component } from '@angular/core';
import { NativeService } from './services/native.service';

@Component({
  selector: 'app-my-component',
  templateUrl: './my-component.html'
})
export class MyComponent {
  isNativeApp = false;
  platform = 'web';
  networkStatus = { connected: true, connectionType: 'unknown' };

  constructor(private nativeService: NativeService) {
    this.checkPlatform();
    this.initializeNetworkMonitoring();
  }

  checkPlatform() {
    this.isNativeApp = this.nativeService.isNative();
    this.platform = this.nativeService.getPlatform();
    console.log('Platform:', this.platform);
  }

  async takePicture() {
    const photo = await this.nativeService.takePicture();
    if (photo) {
      const base64Image = this.nativeService.getBase64FromPhoto(photo);
      console.log('Photo prise:', base64Image);
      // Utiliser l'image pour l'upload vers l'API
      this.uploadImage(base64Image);
    }
  }

  async selectFromGallery() {
    const photo = await this.nativeService.pickFromGallery();
    if (photo) {
      const base64Image = this.nativeService.getBase64FromPhoto(photo);
      console.log('Photo sélectionnée:', base64Image);
    }
  }

  async chooseImageSource() {
    // L'utilisateur choisit entre caméra et galerie
    const photo = await this.nativeService.selectImage();
    if (photo) {
      const base64Image = this.nativeService.getBase64FromPhoto(photo);
      // Traiter l'image...
    }
  }

  async initializeNetworkMonitoring() {
    // Vérifier l'état initial
    this.networkStatus = await this.nativeService.getNetworkStatus();

    // Écouter les changements
    this.nativeService.onNetworkChange((connected) => {
      console.log('Réseau:', connected ? 'Connecté' : 'Déconnecté');
      if (!connected) {
        alert('Connexion perdue. Veuillez vérifier votre réseau.');
      }
    });
  }

  async saveUserPreference(key: string, value: string) {
    await this.nativeService.setStorage(key, value);
  }

  async loadUserPreference(key: string) {
    const value = await this.nativeService.getStorage(key);
    console.log('Préférence chargée:', value);
    return value;
  }

  async getAppVersion() {
    const info = await this.nativeService.getAppInfo();
    if (info) {
      console.log(`App: ${info.name} v${info.version} (build ${info.build})`);
    }
  }

  uploadImage(base64Image: string | undefined) {
    if (!base64Image) return;

    // Exemple d'upload vers votre API
    fetch('https://votre-api.com/upload', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_TOKEN'
      },
      body: JSON.stringify({ image: base64Image })
    })
    .then(response => response.json())
    .then(data => console.log('Image uploadée:', data))
    .catch(error => console.error('Erreur upload:', error));
  }
}
```

## Dans le template HTML

```html
<div *ngIf="isNativeApp">
  <h2>Application Native ({{ platform }})</h2>
  
  <button (click)="takePicture()">
    📷 Prendre une photo
  </button>
  
  <button (click)="selectFromGallery()">
    🖼️ Galerie
  </button>
  
  <button (click)="chooseImageSource()">
    📸 Choisir la source
  </button>

  <div [class.offline]="!networkStatus.connected">
    Réseau: {{ networkStatus.connected ? 'Connecté' : 'Déconnecté' }}
    ({{ networkStatus.connectionType }})
  </div>
</div>

<div *ngIf="!isNativeApp">
  <p>Mode Web - Fonctionnalités natives non disponibles</p>
</div>
```

## Adaptation du composant camera existant

Si vous avez déjà un composant `camera` dans votre projet, vous pouvez l'adapter :

```typescript
// Dans src/app/pages/maintenance-sheets-management/camera/...

import { NativeService } from '../../../services/native.service';

export class CameraComponent {
  constructor(private nativeService: NativeService) {}

  async capturePhoto() {
    if (this.nativeService.isNative()) {
      // Utiliser la caméra native
      const photo = await this.nativeService.takePicture();
      if (photo) {
        const base64 = this.nativeService.getBase64FromPhoto(photo);
        this.onPhotoTaken(base64);
      }
    } else {
      // Utiliser l'API web (navigator.mediaDevices.getUserMedia)
      // Votre code existant...
    }
  }

  onPhotoTaken(base64Image: string | undefined) {
    // Traiter l'image...
  }
}
```

## Configuration de l'environnement

Mettez à jour `src/environments/environment.ts` :

```typescript
export const environment = {
  production: false,
  apiUrl: window.location.hostname === 'localhost' 
    ? 'http://localhost:3000/api'
    : 'https://ezplantparent.com/api',
  enableMobileFeatures: true
};
```

## Auth Interceptor - Adaptation pour mobile

Modifiez `src/app/auth/auth-interceptor.ts` pour gérer le stockage natif :

```typescript
import { NativeService } from '../services/native.service';

export class AuthInterceptor {
  constructor(private nativeService: NativeService) {}

  async getToken(): Promise<string | null> {
    if (this.nativeService.isNative()) {
      // Utiliser le stockage natif sécurisé
      return await this.nativeService.getStorage('auth_token');
    } else {
      // Utiliser localStorage
      return localStorage.getItem('auth_token');
    }
  }

  async saveToken(token: string): Promise<void> {
    if (this.nativeService.isNative()) {
      await this.nativeService.setStorage('auth_token', token);
    } else {
      localStorage.setItem('auth_token', token);
    }
  }
}
```

## Permissions - Vérification dans le code

```typescript
async checkCameraPermission() {
  try {
    const permissions = await Camera.checkPermissions();
    if (permissions.camera !== 'granted') {
      const request = await Camera.requestPermissions({ permissions: ['camera'] });
      return request.camera === 'granted';
    }
    return true;
  } catch (error) {
    console.error('Erreur permissions caméra:', error);
    return false;
  }
}
```
