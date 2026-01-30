# Guide Capacitor - EzPlantParent Mobile

## 🚀 Configuration initiale (Déjà fait)

Capacitor a été configuré avec :
- **App ID**: `com.ezplantparent.app`
- **App Name**: `EzPlantParent`
- **Plateformes**: Android & iOS

## 📦 Plugins installés

- `@capacitor/camera` - Accès à la caméra et galerie photo
- `@capacitor/network` - Détection de l'état réseau
- `@capacitor/splash-screen` - Écran de démarrage
- `@capacitor/status-bar` - Personnalisation de la barre d'état
- `@capacitor/app` - Gestion du cycle de vie de l'app
- `@capacitor/preferences` - Stockage clé-valeur persistant

## 🛠️ Scripts disponibles

### Build et synchronisation
```bash
npm run build:mobile        # Build Angular en mode production
npm run cap:sync           # Build + sync avec Android/iOS
```

### Développement Android
```bash
npm run cap:open:android   # Ouvre Android Studio
npm run cap:run:android    # Build + lance sur émulateur/appareil
```

### Développement iOS (Mac uniquement)
```bash
npm run cap:open:ios       # Ouvre Xcode
npm run cap:run:ios        # Build + lance sur simulateur/appareil
```

## 📱 Développement Android

### Prérequis
1. **Android Studio** installé
2. **JDK 17** configuré
3. **Android SDK** avec API Level 33+
4. **Émulateur Android** ou appareil physique en mode développeur

### Premier lancement
```bash
# 1. Build l'application web
npm run build:mobile

# 2. Synchroniser avec les projets natifs
npx cap sync

# 3. Ouvrir dans Android Studio
npm run cap:open:android
```

Dans Android Studio :
1. Attendre l'indexation Gradle
2. Sélectionner un appareil/émulateur
3. Cliquer sur "Run" (▶️)

### Rechargement en direct (Live Reload)

Pour le développement avec rechargement automatique :

1. Démarrer le serveur Angular :
```bash
npm start
```

2. Modifier `capacitor.config.ts` temporairement :
```typescript
server: {
  url: 'http://192.168.x.x:4200',  // Votre IP locale
  cleartext: true
}
```

3. Synchroniser et relancer :
```bash
npx cap sync android
npm run cap:open:android
```

**⚠️ Important** : Retirer la configuration `server.url` avant le build de production !

## 🍎 Développement iOS

### Prérequis (Mac uniquement)
1. **Xcode 15+** installé
2. **CocoaPods** : `sudo gem install cocoapods`
3. **Simulateur iOS** ou iPhone en mode développeur
4. **Compte Apple Developer** (pour tester sur appareil réel)

### Premier lancement
```bash
# 1. Build l'application web
npm run build:mobile

# 2. Synchroniser avec iOS
npx cap sync ios

# 3. Ouvrir dans Xcode
npm run cap:open:ios
```

Dans Xcode :
1. Sélectionner un simulateur ou appareil
2. Configurer le "Signing & Capabilities" avec votre compte Apple
3. Cliquer sur "Run" (▶️)

## 🔧 Configuration de l'API Backend

Pour que l'application mobile communique avec votre backend, modifiez les URLs dans vos services Angular :

### Option 1 : Variable d'environnement (Recommandé)

`src/environments/environment.ts` :
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:3000/api'  // Dev local
};
```

`src/environments/environment.prod.ts` :
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://ezplantparent.com/api'  // Production
};
```

### Option 2 : Configuration Capacitor

`capacitor.config.ts` :
```typescript
server: {
  url: 'https://ezplantparent.com',
  androidScheme: 'https',
  iosScheme: 'https'
}
```

## 🔐 Permissions

### Android
Les permissions sont configurées dans `android/app/src/main/AndroidManifest.xml` :
- ✅ Internet
- ✅ Caméra
- ✅ Lecture/Écriture stockage
- ✅ État réseau

### iOS
Les permissions doivent être ajoutées manuellement dans `ios/App/App/Info.plist` :

```xml
<key>NSCameraUsageDescription</key>
<string>Nous avons besoin de la caméra pour identifier vos plantes</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>Nous avons besoin d'accéder à vos photos</string>
<key>NSPhotoLibraryAddUsageDescription</key>
<string>Nous souhaitons enregistrer des photos de vos plantes</string>
```

## 📸 Utilisation de la caméra dans le code

Exemple d'intégration dans un composant Angular :

```typescript
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';

async takePicture() {
  try {
    const image = await Camera.getPhoto({
      quality: 90,
      allowEditing: false,
      resultType: CameraResultType.Base64,
      source: CameraSource.Camera
    });

    const base64Image = `data:image/jpeg;base64,${image.base64String}`;
    // Utiliser l'image...
  } catch (error) {
    console.error('Erreur caméra:', error);
  }
}
```

## 🌐 Détection réseau

```typescript
import { Network } from '@capacitor/network';

async checkNetworkStatus() {
  const status = await Network.getStatus();
  console.log('Network status:', status);
}

// Écouter les changements
Network.addListener('networkStatusChange', status => {
  console.log('Network status changed', status);
});
```

## 🚀 Build de production

### Android APK
```bash
# 1. Build optimisé
npm run build:mobile

# 2. Sync
npx cap sync android

# 3. Ouvrir Android Studio
npm run cap:open:android

# 4. Dans Android Studio : Build > Build Bundle(s) / APK(s) > Build APK(s)
```

### Android AAB (Google Play)
Dans Android Studio : `Build > Generate Signed Bundle / APK`

### iOS App Store
Dans Xcode : `Product > Archive`, puis `Distribute App`

## 🐛 Débogage

### Logs Android
```bash
npx cap run android --livereload --external
adb logcat | grep Capacitor
```

### Logs iOS
Dans Xcode : ouvrir le Console pendant l'exécution

### Chrome DevTools (Android)
1. Appareil Android connecté en USB
2. Chrome : `chrome://inspect`
3. Sélectionner votre app

### Safari DevTools (iOS)
1. Sur Mac, activer le menu Develop dans Safari
2. Connecter l'iPhone
3. `Develop > [Votre iPhone] > [Votre App]`

## 📚 Ressources

- [Documentation Capacitor](https://capacitorjs.com/docs)
- [Plugins officiels](https://capacitorjs.com/docs/apis)
- [Communauté](https://ionic.link/discord)

## 🔄 Workflow type

1. **Développement** : `npm start` (web browser)
2. **Test mobile** : `npm run cap:sync` + Android Studio/Xcode
3. **Build prod** : `npm run build:mobile` + génération APK/IPA
4. **Déploiement** : Google Play Store / Apple App Store
