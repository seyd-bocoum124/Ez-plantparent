# 📱 Déploiement sur les Stores - EzPlantParent

## 🎯 Checklist avant publication

### Obligatoire
- [ ] Build en mode production testé
- [ ] Toutes les fonctionnalités testées sur appareil réel
- [ ] Permissions justifiées (caméra, stockage, réseau)
- [ ] Icône de l'app créée (toutes résolutions)
- [ ] Splash screen créé
- [ ] Privacy Policy et Terms of Service rédigés
- [ ] Screenshots de l'app pris (différentes tailles d'écran)
- [ ] Description de l'app rédigée (français + anglais)
- [ ] Version number définie (ex: 1.0.0)
- [ ] Build number incrémenté

---

## 🤖 Google Play Store (Android)

### 1. Préparation du build

#### Créer un keystore de signature

```bash
keytool -genkey -v -keystore ezplantparent-release.keystore -alias ezplantparent -keyalg RSA -keysize 2048 -validity 10000
```

**⚠️ Important** : Conserver ce fichier et le mot de passe en sécurité ! Vous en aurez besoin pour toutes les mises à jour futures.

#### Configurer Gradle pour la signature

Créer `frontend/android/key.properties` :
```properties
storePassword=VOTRE_MOT_DE_PASSE
keyPassword=VOTRE_MOT_DE_PASSE
keyAlias=ezplantparent
storeFile=../ezplantparent-release.keystore
```

**⚠️ Ajouter ce fichier à `.gitignore` !**

Modifier `frontend/android/app/build.gradle` :

```gradle
// Avant android {
def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}

android {
    // ... configuration existante ...
    
    signingConfigs {
        release {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile file(keystoreProperties['storeFile'])
            storePassword keystoreProperties['storePassword']
        }
    }
    
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

#### Générer l'AAB signé

```bash
cd frontend
npm run build:mobile
npx cap sync android
cd android
./gradlew bundleRelease
```

L'AAB sera généré dans:
`android/app/build/outputs/bundle/release/app-release.aab`

### 2. Créer un compte développeur

1. Aller sur [Google Play Console](https://play.google.com/console)
2. Payer les frais d'inscription (25 USD, une seule fois)
3. Remplir les informations du compte développeur

### 3. Créer l'application

1. **Créer une nouvelle app**:
   - Nom : `EzPlantParent`
   - Langue par défaut : Français
   - Type : Application
   - Gratuite ou payante : Gratuite

2. **Store listing** (Fiche du store):
   - Titre court (30 caractères max)
   - Description complète (4000 caractères max)
   - Description courte (80 caractères)
   - Icône de l'application (512x512 px)
   - Bannière graphique (1024x500 px)
   - Screenshots (minimum 2, max 8):
     - Téléphone : 16:9 ou 9:16
     - Tablette 7" : recommandé
     - Tablette 10" : recommandé

3. **Catégorie**:
   - Type : Applications
   - Catégorie : Lifestyle ou Productivity
   - Tags : Plantes, Jardinage, IoT, Maison connectée

4. **Contenu**:
   - Groupe cible : Tous âges
   - Politique de confidentialité : URL vers votre Privacy Policy
   - Contact du développeur

5. **Upload de l'AAB**:
   - Aller dans "Production" > "Créer une version"
   - Upload `app-release.aab`
   - Remplir les notes de version

6. **Vérifications**:
   - Compléter le questionnaire sur le contenu
   - Déclarer les permissions utilisées
   - Classification du contenu (PEGI/ESRB)

7. **Soumettre pour révision**:
   - Vérifier toutes les sections (icône vert ✓)
   - Cliquer sur "Soumettre pour révision"
   - Délai : 1-7 jours

### Mises à jour futures

1. Incrémenter le `versionCode` et `versionName` dans `android/app/build.gradle`:
   ```gradle
   versionCode 2  // Incrémenter à chaque build
   versionName "1.0.1"  // Version visible par les utilisateurs
   ```

2. Générer un nouvel AAB signé

3. Dans Play Console > Production > "Créer une version"

4. Upload du nouvel AAB avec les notes de version

---

## 🍎 Apple App Store (iOS)

### 1. Prérequis

- **Mac** avec macOS 12+
- **Xcode 15+** installé
- **Compte Apple Developer** (99 USD/an)

### 2. Configuration du compte développeur

1. S'inscrire sur [Apple Developer](https://developer.apple.com)
2. Payer l'abonnement annuel (99 USD)
3. Accepter les accords de licence

### 3. Configurer les identifiants

#### Dans le portail développeur

1. Aller sur [Certificates, Identifiers & Profiles](https://developer.apple.com/account/resources)

2. **Créer un App ID**:
   - Identifiers > App IDs > "+"
   - Description : EzPlantParent
   - Bundle ID : `com.ezplantparent.app` (doit correspondre à capacitor.config.ts)
   - Capabilities : Cocher celles utilisées (Camera, Push Notifications, etc.)

3. **Créer un certificat de distribution**:
   - Certificates > "+"
   - Type : iOS Distribution (App Store and Ad Hoc)
   - Suivre les instructions pour générer le certificat

4. **Créer un profil de provisioning**:
   - Profiles > "+"
   - Type : App Store
   - App ID : Sélectionner `com.ezplantparent.app`
   - Certificat : Sélectionner votre certificat de distribution

#### Dans Xcode

1. Ouvrir le projet:
   ```bash
   npm run cap:open:ios
   ```

2. Sélectionner le projet "App" dans la barre latérale

3. **Signing & Capabilities**:
   - Team : Sélectionner votre compte développeur
   - Bundle Identifier : `com.ezplantparent.app`
   - Provisioning Profile : Automatic (ou sélectionner le profil créé)

4. **General**:
   - Display Name : `EzPlantParent`
   - Bundle Identifier : `com.ezplantparent.app`
   - Version : `1.0.0`
   - Build : `1`

### 4. Préparer l'app

#### Icône de l'app

1. Créer un fichier PNG 1024x1024 px
2. Dans Xcode : `App/Assets.xcassets/AppIcon`
3. Glisser l'icône ou utiliser un outil comme [AppIcon.co](https://appicon.co)

#### Launch Screen (Splash)

Modifier `App/Base.lproj/LaunchScreen.storyboard` dans Xcode

#### Info.plist - Descriptions des permissions

Ajouter dans `ios/App/App/Info.plist` :

```xml
<key>NSCameraUsageDescription</key>
<string>EzPlantParent utilise la caméra pour identifier vos plantes et suivre leur croissance</string>

<key>NSPhotoLibraryUsageDescription</key>
<string>EzPlantParent accède à vos photos pour identifier vos plantes</string>

<key>NSPhotoLibraryAddUsageDescription</key>
<string>EzPlantParent souhaite sauvegarder des photos de vos plantes</string>
```

### 5. Build et archive

1. Dans Xcode:
   - Sélectionner **Generic iOS Device** ou **Any iOS Device (arm64)**
   - Menu : `Product > Archive`
   - Attendre la fin du build (5-10 min)

2. Fenêtre Archives:
   - Sélectionner l'archive créée
   - Cliquer sur **Distribute App**

3. Assistant de distribution:
   - Méthode : **App Store Connect**
   - Options : **Upload** (pas seulement Export)
   - Signing : **Automatically manage signing**
   - Confirmer et uploader

### 6. App Store Connect

1. Aller sur [App Store Connect](https://appstoreconnect.apple.com)

2. **Créer une nouvelle app**:
   - Mes Apps > "+" > Nouvelle app
   - Plateformes : iOS
   - Nom : `EzPlantParent`
   - Langue principale : Français
   - Bundle ID : `com.ezplantparent.app`
   - SKU : `ezplantparent001` (identifiant unique)

3. **Informations de l'app**:
   - Catégorie : Lifestyle ou Productivity
   - Sous-catégorie : Home & Garden
   - Contenu : Tous âges
   - Prix : Gratuit

4. **Version 1.0.0**:
   
   **Captures d'écran** (obligatoire):
   - iPhone 6.7" (1290x2796 px) : 3-10 screenshots
   - iPhone 6.5" (1242x2688 px) : 3-10 screenshots
   - iPad Pro 12.9" (2048x2732 px) : 3-10 screenshots
   
   **Informations**:
   - Titre promotionnel (30 caractères max)
   - Description (4000 caractères max)
   - Mots-clés (100 caractères, séparés par virgules)
   - URL du support technique
   - URL marketing (optionnel)
   
   **Build**:
   - Sélectionner le build uploadé depuis Xcode
   
   **Général**:
   - Icône de l'app (1024x1024 px)
   - Classification du contenu (questionnaire)
   - Informations de copyright
   - Coordonnées du développeur
   - Privacy Policy URL (obligatoire)

5. **Informations de révision**:
   - Coordonnées de la personne à contacter pour la révision
   - Informations de connexion (si l'app nécessite un compte)
   - Notes pour les réviseurs (optionnel)

6. **Soumettre pour révision**:
   - Vérifier toutes les sections
   - Cliquer sur **Ajouter pour révision**
   - Cliquer sur **Soumettre à App Review**
   - Délai : 24-48h généralement (parfois plus)

### Mises à jour futures

1. Incrémenter la version dans Xcode:
   - Version : `1.0.1`, `1.1.0`, `2.0.0`, etc.
   - Build : `2`, `3`, `4`, etc.

2. Archive et upload vers App Store Connect

3. Dans App Store Connect:
   - Créer une nouvelle version
   - Ajouter les notes de mise à jour
   - Soumettre pour révision

---

## 📊 Après publication

### Analytics

Suivre les téléchargements et l'utilisation:
- **Google Play Console** : Statistiques détaillées
- **App Store Connect** : Analytics, Sales and Trends
- Intégrer Firebase Analytics ou Google Analytics

### Mises à jour régulières

- **Corrections de bugs** : Version patch (1.0.1)
- **Nouvelles fonctionnalités mineures** : Version minor (1.1.0)
- **Changements majeurs** : Version major (2.0.0)

### Répondre aux avis

- Répondre aux commentaires des utilisateurs
- Prendre en compte les suggestions
- Corriger les bugs signalés

### Marketing

- Créer une page web pour l'app
- Réseaux sociaux
- Communiqué de presse
- Partager dans les communautés de jardinage

---

## 🔐 Sécurité

### Variables d'environnement sensibles

**Ne jamais commit** :
- Keystores (`.keystore`, `.jks`)
- `key.properties`
- Certificats iOS (`.p12`, `.cer`)
- Profils de provisioning (`.mobileprovision`)
- Clés API dans le code

### Utiliser des secrets

```typescript
// ❌ Mauvais
const API_KEY = 'sk_live_123456789';

// ✅ Bon - Variables d'environnement
const API_KEY = environment.apiKey;
```

### Obfuscation du code (Android)

Le fichier `proguard-rules.pro` permet de minimiser et obfusquer le code pour rendre la rétro-ingénierie plus difficile.

---

## 📚 Ressources utiles

### Documentation officielle
- [Google Play Console Help](https://support.google.com/googleplay/android-developer)
- [App Store Connect Help](https://help.apple.com/app-store-connect/)
- [Capacitor Deployment](https://capacitorjs.com/docs/deployment)

### Outils de génération d'assets
- [AppIcon.co](https://appicon.co) - Générateur d'icônes iOS/Android
- [Icon Kitchen](https://icon.kitchen) - Générateur d'assets Capacitor
- [LaunchScreen](https://apetools.webprofusion.com) - Générateur de splash screens

### Design Guidelines
- [Material Design](https://m3.material.io) - Android
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) - iOS

### Support
- [Stack Overflow](https://stackoverflow.com/questions/tagged/capacitor)
- [Ionic Forum](https://forum.ionicframework.com)
- [Capacitor Discord](https://ionic.link/discord)

---

## ✅ Checklist finale

Avant de soumettre:

### Android (Google Play)
- [ ] AAB signé avec le keystore de production
- [ ] `versionCode` et `versionName` corrects
- [ ] Toutes les permissions justifiées
- [ ] Screenshots (min 2, toutes orientations)
- [ ] Icône 512x512 px
- [ ] Bannière 1024x500 px
- [ ] Description complète
- [ ] Privacy Policy URL
- [ ] Catégorie sélectionnée
- [ ] Classification du contenu complétée

### iOS (App Store)
- [ ] Build archivé et uploadé depuis Xcode
- [ ] Version et build corrects
- [ ] Toutes les permissions avec descriptions
- [ ] Screenshots pour toutes les tailles d'écran
- [ ] Icône 1024x1024 px
- [ ] Description complète
- [ ] Mots-clés optimisés
- [ ] Privacy Policy URL
- [ ] Informations de support
- [ ] Classification complétée

**Bonne chance pour le lancement ! 🚀**
