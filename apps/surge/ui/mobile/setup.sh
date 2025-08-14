#!/bin/bash

# Surgify Mobile App Setup Script
# This script sets up the React Native development environment

set -e

echo "🚀 Setting up Surgify Mobile App..."

# Check if we're in the correct directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the mobile app directory."
    exit 1
fi

# Install dependencies
echo "📦 Installing React Native dependencies..."
npm install

# Install iOS dependencies (if on macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Installing iOS dependencies..."
    cd ios
    pod install
    cd ..
else
    echo "ℹ️  Skipping iOS setup (not on macOS)"
fi

# Clean and reset Metro cache
echo "🧹 Cleaning Metro cache..."
npx react-native start --reset-cache &
METRO_PID=$!
sleep 5
kill $METRO_PID

# Android setup
echo "🤖 Setting up Android environment..."
if command -v adb &> /dev/null; then
    echo "✅ ADB found"
else
    echo "⚠️  Warning: ADB not found. Please install Android SDK Platform-Tools"
fi

# Check React Native environment
echo "🔍 Checking React Native environment..."
npx react-native doctor

echo "✅ Setup complete!"
echo ""
echo "📱 To run the app:"
echo "  iOS:     npx react-native run-ios"
echo "  Android: npx react-native run-android"
echo ""
echo "🔧 Development commands:"
echo "  Start Metro: npx react-native start"
echo "  Clean build: npx react-native clean"
echo "  iOS clean:   cd ios && xcodebuild clean && cd .."
echo "  Android clean: cd android && ./gradlew clean && cd .."
echo ""
echo "🔒 Security notes:"
echo "  - Update certificate pins in network_security_config.xml"
echo "  - Configure proper signing certificates for production"
echo "  - Test biometric authentication on physical devices"
echo "  - Validate security checks work correctly"
