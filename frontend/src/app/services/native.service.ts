import { Injectable } from '@angular/core';
import { Camera, CameraResultType, CameraSource, Photo } from '@capacitor/camera';
import { Network } from '@capacitor/network';
import { Preferences } from '@capacitor/preferences';
import { StatusBar, Style } from '@capacitor/status-bar';
import { SplashScreen } from '@capacitor/splash-screen';
import { App } from '@capacitor/app';
import { Capacitor } from '@capacitor/core';

@Injectable({
  providedIn: 'root'
})
export class NativeService {

  constructor() {
    this.initializeApp();
  }

  /**
   * Vérifie si l'application tourne en mode natif (Android/iOS)
   */
  isNative(): boolean {
    return Capacitor.isNativePlatform();
  }

  /**
   * Obtient la plateforme actuelle
   */
  getPlatform(): string {
    return Capacitor.getPlatform(); // 'web', 'android', ou 'ios'
  }

  /**
   * Initialise l'application native
   */
  private async initializeApp() {
    if (!this.isNative()) {
      return;
    }

    // Configuration de la barre d'état
    try {
      await StatusBar.setStyle({ style: Style.Light });
      await StatusBar.setBackgroundColor({ color: '#4CAF50' });
    } catch (error) {
      console.log('StatusBar non disponible:', error);
    }

    // Masquer le splash screen après initialisation
    try {
      await SplashScreen.hide();
    } catch (error) {
      console.log('SplashScreen non disponible:', error);
    }

    // Écouter les événements de l'application
    App.addListener('appStateChange', ({ isActive }) => {
      console.log('App state changed. Is active?', isActive);
    });

    App.addListener('backButton', ({ canGoBack }) => {
      console.log('Back button pressed. Can go back?', canGoBack);
    });
  }

  /**
   * Prendre une photo avec la caméra
   */
  async takePicture(): Promise<Photo | null> {
    try {
      const image = await Camera.getPhoto({
        quality: 90,
        allowEditing: false,
        resultType: CameraResultType.Base64,
        source: CameraSource.Camera,
        saveToGallery: false
      });
      return image;
    } catch (error) {
      console.error('Erreur lors de la prise de photo:', error);
      return null;
    }
  }

  /**
   * Sélectionner une photo depuis la galerie
   */
  async pickFromGallery(): Promise<Photo | null> {
    try {
      const image = await Camera.getPhoto({
        quality: 90,
        allowEditing: false,
        resultType: CameraResultType.Base64,
        source: CameraSource.Photos
      });
      return image;
    } catch (error) {
      console.error('Erreur lors de la sélection de photo:', error);
      return null;
    }
  }

  /**
   * Choisir entre caméra et galerie
   */
  async selectImage(): Promise<Photo | null> {
    try {
      const image = await Camera.getPhoto({
        quality: 90,
        allowEditing: false,
        resultType: CameraResultType.Base64,
        source: CameraSource.Prompt, // Demande à l'utilisateur
        promptLabelHeader: 'Sélectionner une source',
        promptLabelPhoto: 'Depuis la galerie',
        promptLabelPicture: 'Prendre une photo'
      });
      return image;
    } catch (error) {
      console.error('Erreur lors de la sélection d\'image:', error);
      return null;
    }
  }

  /**
   * Convertir une Photo en base64 pour l'upload
   */
  getBase64FromPhoto(photo: Photo): string | undefined {
    if (photo.base64String) {
      return `data:image/${photo.format};base64,${photo.base64String}`;
    }
    return undefined;
  }

  /**
   * Vérifier l'état de la connexion réseau
   */
  async getNetworkStatus() {
    try {
      const status = await Network.getStatus();
      return {
        connected: status.connected,
        connectionType: status.connectionType
      };
    } catch (error) {
      console.error('Erreur lors de la vérification du réseau:', error);
      return { connected: true, connectionType: 'unknown' };
    }
  }

  /**
   * Écouter les changements de connexion réseau
   */
  onNetworkChange(callback: (connected: boolean) => void) {
    Network.addListener('networkStatusChange', status => {
      callback(status.connected);
    });
  }

  /**
   * Sauvegarder une valeur dans le stockage persistant
   */
  async setStorage(key: string, value: string): Promise<void> {
    try {
      await Preferences.set({ key, value });
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error);
    }
  }

  /**
   * Récupérer une valeur du stockage persistant
   */
  async getStorage(key: string): Promise<string | null> {
    try {
      const { value } = await Preferences.get({ key });
      return value;
    } catch (error) {
      console.error('Erreur lors de la récupération:', error);
      return null;
    }
  }

  /**
   * Supprimer une valeur du stockage
   */
  async removeStorage(key: string): Promise<void> {
    try {
      await Preferences.remove({ key });
    } catch (error) {
      console.error('Erreur lors de la suppression:', error);
    }
  }

  /**
   * Vider tout le stockage
   */
  async clearStorage(): Promise<void> {
    try {
      await Preferences.clear();
    } catch (error) {
      console.error('Erreur lors du nettoyage:', error);
    }
  }

  /**
   * Obtenir les informations de l'application
   */
  async getAppInfo() {
    try {
      const info = await App.getInfo();
      return {
        name: info.name,
        id: info.id,
        build: info.build,
        version: info.version
      };
    } catch (error) {
      console.error('Erreur lors de la récupération des infos:', error);
      return null;
    }
  }

  /**
   * Quitter l'application (Android uniquement)
   */
  async exitApp(): Promise<void> {
    if (this.getPlatform() === 'android') {
      await App.exitApp();
    }
  }
}
