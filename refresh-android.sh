#!/bin/bash

echo "🔄 Refreshing Android project..."
echo ""

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

echo ""
echo "✅ Done! Android Studio should detect changes."
echo "   Click 'Sync Now' if prompted in Android Studio"
