# Surgify Mobile - Android

This directory contains the Android-specific code for the Surgify mobile application.

## Setup

1. **Prerequisites:**
   - Android Studio (latest version)
   - Android SDK 31 or higher
   - Java Development Kit (JDK) 11 or higher
   - Node.js 16 or higher

2. **Installation:**
   ```bash
   cd /workspaces/yaz/src/surgify/ui/mobile
   npm install
   cd android
   ./gradlew clean
   ```

3. **Running:**
   ```bash
   # From the mobile directory
   npm run android
   ```

## Architecture

### Native Modules
- **SurgifyBridge**: Main bridge for communication between React Native and native code
- **BiometricModule**: Handles fingerprint and face recognition
- **CameraModule**: Advanced camera functionality for medical imaging
- **FileSystemModule**: Secure file storage and management
- **SecurityModule**: Device security and encryption

### Key Features
- Medical-grade image capture and processing
- Biometric authentication with hardware-backed keystore
- Encrypted local storage for sensitive data
- Background sync capabilities
- Push notifications for case updates
- Offline mode with selective sync
- React Native for cross-platform development (alternative)

Features:
- Native Android interface
- Offline case management
- Push notifications
- Secure data synchronization
- Biometric authentication

Structure:
- app/ - Main application module
- gradle/ - Build configuration
- res/ - Resources (layouts, strings, drawables)
- tests/ - Unit and instrumentation tests

To get started:
1. Install Android Studio
2. Set up Android SDK
3. Configure gradle build system
4. Run initial setup script (when available)

Current Status: Development in progress
"""

# Android app entry point placeholder
print("Surgify Android App - Coming Soon!")
