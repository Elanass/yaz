# Surgify Mobile - iOS

This directory contains the iOS-specific code for the Surgify mobile application.

## Setup

1. **Prerequisites:**
   - Xcode 14 or higher
   - iOS 14.0 or higher
   - CocoaPods 1.11 or higher
   - Node.js 16 or higher

2. **Installation:**
   ```bash
   cd /workspaces/yaz/src/surgify/ui/mobile
   npm install
   cd ios
   pod install
   ```

3. **Running:**
   ```bash
   # From the mobile directory
   npm run ios
   ```

## Architecture

### Native Modules
- **SurgifyBridge**: Main bridge for communication between React Native and native code
- **BiometricModule**: Handles Touch ID and Face ID authentication
- **CameraModule**: Advanced camera functionality for medical imaging
- **FileSystemModule**: Secure file storage with iOS Data Protection
- **SecurityModule**: Device security and encryption with Keychain Services
- React Native for cross-platform development (alternative)

Features:
- Native iOS interface
- Offline case management
- Push notifications
- Secure data synchronization
- Touch ID/Face ID authentication

Structure:
- src/ - Source code
- assets/ - Images, icons, and resources
- config/ - Configuration files
- tests/ - Unit and integration tests

To get started:
1. Install Xcode and development tools
2. Set up iOS development environment
3. Run initial setup script (when available)

Current Status: Development in progress
"""

# iOS app entry point placeholder
print("Surgify iOS App - Coming Soon!")
