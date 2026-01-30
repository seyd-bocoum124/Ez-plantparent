import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.ezplantparent.mobile',
  appName: 'EzPlantParent',
  webDir: 'dist/frontend/browser',
  server: {
    // Configuration pour utiliser HTTPS avec backend production
    androidScheme: 'https',
    allowNavigation: ['https://ezplantparent.com']
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#4CAF50',
      showSpinner: false
    },
    GoogleAuth: {
      scopes: ['profile', 'email'],
      serverClientId: '277969973394-5kmjs69fmrbc1p6d39d7900mmedim2ur.apps.googleusercontent.com',
      forceCodeForRefreshToken: true
    }
  }
};

export default config;
