# 📱 EzPlantParent - Application Mobile

## Vue d'ensemble

EzPlantParent est maintenant disponible en tant qu'application mobile native grâce à **Capacitor 7**. L'application Angular existante a été configurée pour être déployée sur **Android** et **iOS**.

## 🚀 Démarrage rapide

### Prérequis
- **Node.js 18+** et npm
- **Android Studio** (pour Android)
- **Xcode 15+** (pour iOS, Mac uniquement)

### Lancer l'app mobile

```bash
cd frontend

# Build l'application Angular
npm run build:mobile

# Synchroniser avec les plateformes natives
npx cap sync

# Ouvrir dans Android Studio
npm run cap:open:android

# OU ouvrir dans Xcode (Mac uniquement)
npm run cap:open:ios
```

## 📖 Documentation complète

Toute la documentation est dans le dossier `frontend/` :

### 🎯 Guides essentiels

1. **[MOBILE_SETUP_COMPLETE.md](frontend/MOBILE_SETUP_COMPLETE.md)**
   - ✅ Checklist de ce qui a été configuré
   - 🚀 Prochaines étapes pour tester
   - 📝 Adaptations recommandées du code existant

2. **[CAPACITOR.md](frontend/CAPACITOR.md)**
   - 📦 Plugins installés et leur usage
   - 🛠️ Scripts npm disponibles
   - 🔧 Configuration détaillée
   - 🐛 Débogage et troubleshooting

3. **[NATIVE_SERVICE_USAGE.md](frontend/NATIVE_SERVICE_USAGE.md)**
   - 💡 Exemples d'utilisation du NativeService
   - 📸 Intégration de la caméra native
   - 🌐 Détection réseau
   - 💾 Stockage persistant

4. **[STORE_DEPLOYMENT.md](frontend/STORE_DEPLOYMENT.md)**
   - 🤖 Publication sur Google Play Store
   - 🍎 Publication sur Apple App Store
   - 📊 Après publication et analytics
   - 🔐 Sécurité et bonnes pratiques

## 🎨 Fonctionnalités natives

Le service `NativeService` (`frontend/src/app/services/native.service.ts`) fournit :

- **📷 Caméra** : Prise de photo et sélection depuis la galerie
- **🌐 Réseau** : Détection de connectivité et monitoring
- **💾 Stockage** : Stockage local persistant et sécurisé
- **📱 App Info** : Version, build, nom de l'application
- **🎨 UI Native** : Barre d'état, splash screen
- **🔍 Détection** : Savoir si l'app tourne en mode natif ou web

## 🏗️ Structure du projet

```
frontend/
├── android/                    # Projet Android natif
│   ├── app/
│   │   ├── src/main/
│   │   │   ├── AndroidManifest.xml
│   │   │   └── java/.../MainActivity.java
│   │   └── build.gradle
│   └── build.gradle
├── ios/                        # Projet iOS natif
│   └── App/
│       ├── App.xcodeproj
│       ├── App/
│       │   ├── Info.plist
│       │   └── AppDelegate.swift
│       └── Podfile
├── src/
│   ├── app/
│   │   └── services/
│   │       └── native.service.ts    # Service pour fonctionnalités natives
│   └── environments/
│       ├── environment.ts           # Dev config
│       └── environment.prod.ts      # Prod config
├── capacitor.config.ts         # Configuration Capacitor
├── CAPACITOR.md               # Guide Capacitor complet
├── NATIVE_SERVICE_USAGE.md    # Exemples d'utilisation
├── MOBILE_SETUP_COMPLETE.md   # Setup checklist
└── STORE_DEPLOYMENT.md        # Guide de publication
```

## 🔌 Plugins Capacitor installés

- `@capacitor/camera` (v7.0.2) - Caméra et galerie
- `@capacitor/network` (v7.0.2) - État réseau
- `@capacitor/preferences` (v7.0.2) - Stockage local
- `@capacitor/splash-screen` (v7.0.3) - Écran de démarrage
- `@capacitor/status-bar` (v7.0.3) - Barre d'état
- `@capacitor/app` (v7.1.0) - Cycle de vie app

## 🎯 Scripts npm disponibles

```bash
# Développement
npm start                      # Serveur dev Angular (web)
npm run build:mobile          # Build production pour mobile

# Capacitor
npm run cap:sync              # Build + sync avec Android/iOS
npm run cap:open:android      # Ouvrir Android Studio
npm run cap:open:ios          # Ouvrir Xcode
npm run cap:run:android       # Build + lancer sur Android
npm run cap:run:ios           # Build + lancer sur iOS
```

## 📱 Configuration de l'app

- **App ID** : `com.ezplantparent.app`
- **App Name** : `EzPlantParent`
- **Platforms** : Android 13+ (API 33), iOS 13+
- **Couleur principale** : `#4CAF50` (vert plante)

## 🔐 Permissions configurées

### Android
- ✅ Internet (API backend)
- ✅ Caméra (identification plantes)
- ✅ Lecture/Écriture stockage (photos)
- ✅ État réseau (monitoring connectivité)

### iOS
À configurer manuellement dans `Info.plist` :
- NSCameraUsageDescription
- NSPhotoLibraryUsageDescription
- NSPhotoLibraryAddUsageDescription

## 🌐 Configuration API

### Développement local
```typescript
// frontend/src/environments/environment.ts
apiUrl: 'http://localhost:3000/api'
// Pour tester sur mobile : 'http://192.168.x.x:3000/api'
```

### Production
```typescript
// frontend/src/environments/environment.prod.ts
apiUrl: '/api'  // URL relative (Traefik)
// Pour mobile : 'https://ezplantparent.omg.lol/api'
```

## 🎓 Workflow de développement mobile

1. **Développement web** : `npm start` (navigateur)
2. **Test fonctionnalités natives** : Modifier le code Angular
3. **Build mobile** : `npm run build:mobile`
4. **Sync** : `npx cap sync`
5. **Test sur émulateur/appareil** : Android Studio ou Xcode
6. **Itération** : Retour à l'étape 2

## 🚢 Déploiement

### Test local
```bash
npm run cap:run:android  # Lance sur émulateur/appareil Android
npm run cap:run:ios      # Lance sur simulateur/iPhone
```

### Production
- **Android** : Générer AAB signé dans Android Studio
- **iOS** : Archiver dans Xcode et uploader vers App Store Connect

Voir [STORE_DEPLOYMENT.md](frontend/STORE_DEPLOYMENT.md) pour les détails complets.

## 🔄 Mises à jour

Après modification du code Angular :

```bash
# 1. Build
npm run build:mobile

# 2. Sync (copie les assets vers Android/iOS)
npx cap sync

# 3. Relancer l'app native
# Dans Android Studio ou Xcode : Run ▶️
```

## 📝 Notes importantes

### ⚠️ À ne PAS commit
- `android/app/src/main/assets/public/` (généré automatiquement)
- `ios/App/App/public/` (généré automatiquement)
- Keystores (`.keystore`, `.jks`)
- Certificats iOS (`.p12`, `.cer`)
- Fichiers de configuration avec secrets

### ✅ À commit
- Code source Angular
- Configuration Capacitor (`capacitor.config.ts`)
- Projets natifs (`android/`, `ios/`)
- Scripts npm
- Documentation

## 🐛 Problèmes courants

### "command not found: npx"
```bash
npm install -g npm@latest
```

### Gradle sync failed
Dans Android Studio : `File > Invalidate Caches / Restart`

### CocoaPods errors (iOS)
```bash
cd ios/App && pod repo update && pod install
```

### App ne démarre pas
Vérifier les logs :
- **Android** : `adb logcat | grep Capacitor`
- **iOS** : Console dans Xcode

## 📚 Ressources

- [Documentation Capacitor](https://capacitorjs.com/docs)
- [Plugins Capacitor](https://capacitorjs.com/docs/plugins)
- [Android Studio](https://developer.android.com/studio)
- [Xcode](https://developer.apple.com/xcode/)
- [Material Design](https://m3.material.io)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)

## 🤝 Support

Pour toute question sur la configuration mobile :
1. Consulter la documentation dans `frontend/`
2. Vérifier les logs de l'app native
3. Consulter la documentation Capacitor officielle

---

**🎉 L'application EzPlantParent est maintenant prête pour le mobile !**

Pour commencer : `cd frontend && npm run cap:open:android`
