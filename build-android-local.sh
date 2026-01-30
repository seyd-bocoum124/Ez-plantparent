#!/bin/bash

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo "🔨 Building Angular app..."
npm run build

echo "⚡ Syncing Capacitor..."
npx cap sync android

echo "📱 Opening Android Studio..."
npx cap open android

echo "✅ Android Studio should now be open!"
echo "   You can build and run from Android Studio"
