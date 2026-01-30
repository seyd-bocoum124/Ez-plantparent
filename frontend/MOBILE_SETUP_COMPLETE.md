# ✅ Configuration Capacitor Terminée - EzPlantParent Mobile

## 🎉 Ce qui a été fait

### 1. **Installation de Capacitor** ✅
- `@capacitor/core` v7.4.4
- `@capacitor/cli` v7.4.4
- `@capacitor/android` v7.4.4
- `@capacitor/ios` v7.4.4

### 2. **Plugins installés** ✅
- `@capacitor/camera` - Caméra et galerie photo
- `@capacitor/network` - Détection réseau
- `@capacitor/splash-screen` - Écran de démarrage
- `@capacitor/status-bar` - Barre d'état
- `@capacitor/app` - Cycle de vie app
- `@capacitor/preferences` - Stockage local

### 3. **Plateformes créées** ✅
- **Android** : Projet dans `/frontend/android/`
- **iOS** : Projet dans `/frontend/ios/`

### 4. **Configuration** ✅
- `capacitor.config.ts` configuré avec:
  - App ID: `com.ezplantparent.app`
  - App Name: `EzPlantParent`
  - Web Dir: `dist/frontend/browser`
  - Splash screen personnalisé (vert #4CAF50)

### 5. **Permissions Android** ✅
Dans `android/app/src/main/AndroidManifest.xml`:
- ✅ Internet
- ✅ Caméra
- ✅ Lecture/Écriture stockage (images)
- ✅ État réseau

### 6. **Scripts npm ajoutés** ✅
```json
"build:mobile": "ng build --configuration production",
"cap:sync": "npm run build:mobile && npx cap sync",
"cap:open:android": "npx cap open android",
"cap:open:ios": "npx cap open ios",
"cap:run:android": "npm run cap:sync && npx cap run android",
"cap:run:ios": "npm run cap:sync && npx cap run ios"
```

### 7. **Service natif créé** ✅
`src/app/services/native.service.ts` avec:
- Détection de plateforme (web/android/ios)
- Gestion caméra (photo + galerie)
- Monitoring réseau
- Stockage persistant
- Informations app
- Barre d'état et splash screen

### 8. **Environnements configurés** ✅
- `environment.ts` : Dev avec localhost
- `environment.prod.ts` : Production avec support mobile

### 9. **Documentation créée** ✅
- `CAPACITOR.md` : Guide complet Capacitor
- `NATIVE_SERVICE_USAGE.md` : Exemples d'utilisation

### 10. **.gitignore mis à jour** ✅
Ignore les assets générés:
```
android/app/src/main/assets/public
ios/App/App/public
```

---

## 🚀 Prochaines étapes

### Pour tester sur Android (maintenant):

1. **Build l'application**:
   ```bash
   cd frontend
   npm run build:mobile
   ```

2. **Synchroniser**:
   ```bash
   npx cap sync android
   ```

3. **Ouvrir dans Android Studio**:
   ```bash
   npm run cap:open:android
   ```

4. Dans Android Studio:
   - Attendre l'indexation Gradle (première fois: 2-5 min)
   - Créer un émulateur Android si besoin (AVD Manager)
   - Cliquer sur Run ▶️

### Pour tester sur iOS (Mac uniquement):

1. **Installer CocoaPods**:
   ```bash
   sudo gem install cocoapods
   ```

2. **Build et sync**:
   ```bash
   npm run build:mobile
   npx cap sync ios
   ```

3. **Ouvrir dans Xcode**:
   ```bash
   npm run cap:open:ios
   ```

4. Dans Xcode:
   - Configurer le Signing avec votre compte Apple
   - Sélectionner un simulateur
   - Cliquer sur Run ▶️

---

## 📝 Adaptations recommandées

### 1. Adapter les composants existants

**Composant Camera** (`src/app/pages/maintenance-sheets-management/camera/`):
```typescript
import { NativeService } from '../../../services/native.service';

constructor(private nativeService: NativeService) {}

async capturePhoto() {
  if (this.nativeService.isNative()) {
    // Version mobile native
    const photo = await this.nativeService.takePicture();
    if (photo) {
      const base64 = this.nativeService.getBase64FromPhoto(photo);
      this.onPhotoCapture(base64);
    }
  } else {
    // Version web existante
    // ... votre code actuel
  }
}
```

### 2. Auth Interceptor avec stockage natif

Modifier `src/app/auth/auth-interceptor.ts`:
```typescript
import { NativeService } from '../services/native.service';

async getToken(): Promise<string | null> {
  if (this.nativeService.isNative()) {
    return await this.nativeService.getStorage('auth_token');
  }
  return localStorage.getItem('auth_token');
}
```

### 3. Monitoring réseau

Dans `app.component.ts`:
```typescript
import { NativeService } from './services/native.service';

constructor(private nativeService: NativeService) {
  this.nativeService.onNetworkChange((connected) => {
    if (!connected) {
      this.showOfflineMessage();
    }
  });
}
```

### 4. Configuration API pour mobile

Pour tester l'app mobile avec votre backend local:

1. Obtenir votre IP locale:
   ```powershell
   ipconfig
   # Chercher "Adresse IPv4"
   ```

2. Modifier temporairement `environment.ts`:
   ```typescript
   apiUrl: 'http://192.168.x.x:3000/api'  // Votre IP
   ```

3. Rebuild et sync:
   ```bash
   npm run cap:sync
   ```

---

## 🔧 Configuration avancée

### Live Reload (dev mobile)

Pour le rechargement en direct sur appareil:

1. Démarrer le serveur Angular:
   ```bash
   npm start
   ```

2. Obtenir votre IP locale (ex: 192.168.1.10)

3. Modifier `capacitor.config.ts`:
   ```typescript
   server: {
     url: 'http://192.168.1.10:4200',
     cleartext: true
   }
   ```

4. Sync et relancer:
   ```bash
   npx cap sync
   npm run cap:open:android
   ```

**⚠️ Retirer cette config avant le build de production !**

### Icône et Splash Screen personnalisés

1. Créer les assets:
   - Icône: `frontend/android/app/src/main/res/mipmap-*/ic_launcher.png`
   - Splash: `frontend/android/app/src/main/res/drawable/splash.png`

2. Utiliser un générateur:
   - [Icon Generator](https://icon.kitchen/)
   - [Capacitor Assets](https://github.com/ionic-team/capacitor-assets)

---

## 📦 Build de production

### Android APK (test)

```bash
# 1. Build production
npm run build:mobile

# 2. Sync
npx cap sync android

# 3. Ouvrir Android Studio
npm run cap:open:android

# 4. Build > Build Bundle(s) / APK(s) > Build APK(s)
```

APK généré dans: `android/app/build/outputs/apk/debug/`

### Android AAB (Google Play)

Dans Android Studio:
1. `Build > Generate Signed Bundle / APK`
2. Choisir `Android App Bundle`
3. Créer/utiliser un keystore
4. Générer l'AAB signé

### iOS (App Store)

Dans Xcode:
1. `Product > Archive`
2. Attendre la fin de l'archivage
3. `Distribute App`
4. Suivre l'assistant App Store Connect

---

## 🐛 Dépannage

### Build échoue

```bash
# Nettoyer et rebuild
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run cap:sync
```

### Gradle sync échoue (Android)

Dans Android Studio:
- `File > Invalidate Caches / Restart`
- Vérifier la version JDK (doit être 17)

### CocoaPods errors (iOS)

```bash
cd ios/App
pod repo update
pod install
```

### App ne démarre pas

Vérifier les logs:
```bash
# Android
adb logcat | grep Capacitor

# iOS (dans Xcode)
# Ouvrir Window > Devices and Simulators > View Device Logs
```

---

## 📚 Ressources

- [Capacitor Docs](https://capacitorjs.com/docs)
- [Capacitor Plugins](https://capacitorjs.com/docs/plugins)
- [Angular + Capacitor](https://capacitorjs.com/docs/getting-started/with-ionic)
- [Android Studio](https://developer.android.com/studio)
- [Xcode](https://developer.apple.com/xcode/)

---

## ✨ Fonctionnalités prêtes à utiliser

Votre app peut maintenant:
- ✅ Prendre des photos avec la caméra native
- ✅ Sélectionner des images depuis la galerie
- ✅ Détecter l'état de la connexion réseau
- ✅ Stocker des données localement de manière persistante
- ✅ Afficher un splash screen au démarrage
- ✅ Personnaliser la barre d'état
- ✅ Détecter si elle tourne en mode natif ou web
- ✅ Communiquer avec votre API backend

**L'application est prête pour le développement mobile !** 🎉

Pour commencer, lancez simplement:
```bash
cd frontend
npm run cap:open:android
```
