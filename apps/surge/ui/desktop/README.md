# Surgify Desktop Application

A secure, cross-platform desktop wrapper for Surgify using Electron, providing native desktop integration while maintaining web-based functionality.

## Features

- **Secure WebView Integration**: Sandboxed web content with strict security policies
- **Native Window Controls**: Custom title bar with minimize, maximize, and close controls
- **Connection Management**: Automatic reconnection and health monitoring
- **Offline Detection**: Graceful handling of network connectivity issues
- **Authentication Management**: Secure token storage and validation
- **Auto-Updates**: Built-in update mechanism for seamless maintenance
- **Cross-Platform**: Support for Windows, macOS, and Linux

## Architecture

### Main Process (`src/main/`)
- **main.ts**: Entry point and application lifecycle management
- **SecurityManager.ts**: Certificate validation and security policies
- **WindowManager.ts**: Window creation and management
- **UpdateManager.ts**: Auto-update functionality
- **MenuManager.ts**: Native menu creation
- **ProtocolManager.ts**: Custom protocol handling
- **IpcHandlers.ts**: Inter-process communication

### Renderer Process (`src/renderer/`)
- **React Components**: Modern UI components for the desktop interface
- **Vanilla JS Alternative**: Standalone renderer without React dependencies
- **Service Managers**: Authentication, connection, and WebView management
- **Global Styles**: Consistent styling across the application

## Security Features

- Content Security Policy (CSP) enforcement
- Certificate validation for HTTPS connections
- Sandboxed WebView with limited permissions
- Secure token storage using Electron's secure storage
- Prevention of code injection and XSS attacks

## Prerequisites

Before running the desktop application, ensure you have:

- Node.js 18+ installed
- Git for version control
- Platform-specific build tools:
  - **Windows**: Visual Studio Build Tools or Visual Studio Community
  - **macOS**: Xcode Command Line Tools
  - **Linux**: build-essential package

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd surgify/src/surgify/ui/desktop
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Build the application**:
   ```bash
   npm run build
   ```

## Development

### Running in Development Mode

```bash
# Start the application in development mode
npm run dev

# Or start individual processes
npm run dev:main    # Main process with hot reload
npm run dev:renderer # Renderer process with hot reload
```

### Building for Production

```bash
# Build both main and renderer processes
npm run build

# Build for distribution
npm run build:prod

# Package the application
npm run package

# Create platform-specific installers
npm run make
```

### Available Scripts

- `npm start` - Start the packaged application
- `npm run dev` - Development mode with hot reload
- `npm run build` - Build for production
- `npm run test` - Run unit tests
- `npm run lint` - Check code quality
- `npm run clean` - Clean build artifacts

## Configuration

### Environment Variables

Create a `.env` file in the desktop directory:

```env
SURGIFY_API_URL=https://api.surgify.com
SURGIFY_WEB_URL=https://surgify.com
ELECTRON_ENV=development
AUTO_UPDATE_URL=https://updates.surgify.com
```

### Build Configuration

The application uses several configuration files:

- `package.json` - Dependencies and build scripts
- `tsconfig.json` - TypeScript configuration for renderer
- `tsconfig.main.json` - TypeScript configuration for main process
- `webpack.renderer.config.js` - Webpack configuration for renderer
- `electron-builder.json` - Distribution packaging configuration

## Platform-Specific Builds

### Windows
```bash
npm run build:win
```
Creates: `.exe` installer, portable `.exe`, and Microsoft Store package

### macOS
```bash
npm run build:mac
```
Creates: `.dmg` installer, `.app` bundle, and Mac App Store package

### Linux
```bash
npm run build:linux
```
Creates: `.deb`, `.rpm`, `.AppImage`, and `.tar.gz` packages

## Security Considerations

### Certificate Validation
The application validates HTTPS certificates for all connections to Surgify servers. Invalid certificates will trigger security warnings.

### Content Security Policy
Strict CSP rules prevent:
- Execution of inline scripts
- Loading of external resources
- Code injection attempts
- XSS attacks

### Sandboxing
The WebView is sandboxed with:
- No Node.js integration in renderer
- Limited API access
- Secure communication via IPC
- Prevention of arbitrary code execution

## Troubleshooting

### Common Issues

1. **Application won't start**
   - Check Node.js version (18+ required)
   - Verify all dependencies are installed
   - Clear node_modules and reinstall

2. **Build failures**
   - Ensure platform-specific build tools are installed
   - Check TypeScript compilation errors
   - Verify Webpack configuration

3. **Connection issues**
   - Check network connectivity
   - Verify Surgify API endpoints are accessible
   - Review certificate validation errors

4. **Performance issues**
   - Enable hardware acceleration in settings
   - Check available system memory
   - Monitor CPU usage in Task Manager

### Debug Mode

Enable debug logging:
```bash
DEBUG=surgify:* npm start
```

### Logs Location

Application logs are stored in:
- **Windows**: `%USERPROFILE%\AppData\Roaming\Surgify\logs`
- **macOS**: `~/Library/Logs/Surgify`
- **Linux**: `~/.config/Surgify/logs`

## Updates

The application includes automatic update functionality:

1. **Automatic Check**: Checks for updates on startup
2. **Background Download**: Downloads updates in the background
3. **User Notification**: Prompts user to restart and install
4. **Rollback Support**: Ability to rollback failed updates

## Contributing

1. Follow the existing code style and patterns
2. Add tests for new functionality
3. Update documentation for changes
4. Test on all target platforms before submitting

## Support

For technical support or questions:
- Email: support@surgify.com
- Documentation: https://docs.surgify.com
- Issue Tracker: [Internal tracking system]

## License

Proprietary - All rights reserved by Surgify Inc.
