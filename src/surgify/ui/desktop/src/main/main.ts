import { app, BrowserWindow, Menu, shell, ipcMain, dialog, session } from 'electron';
import { autoUpdater } from 'electron-updater';
import windowStateKeeper from 'electron-window-state';
import contextMenu from 'electron-context-menu';
import log from 'electron-log';
import Store from 'electron-store';
import * as path from 'path';
import * as os from 'os';

// Import custom modules
import { SecurityManager } from './security/SecurityManager';
import { UpdateManager } from './managers/UpdateManager';
import { WindowManager } from './managers/WindowManager';
import { MenuManager } from './managers/MenuManager';
import { ProtocolManager } from './managers/ProtocolManager';
import { IpcHandlers } from './ipc/IpcHandlers';

// Configure logging
log.transports.file.resolvePathFn = () => path.join(os.homedir(), '.surgify', 'logs', 'main.log');
log.info('Application starting...');

// Store for app settings
const store = new Store({
  name: 'surgify-settings',
  defaults: {
    windowBounds: { width: 1200, height: 800 },
    webServerUrl: 'https://surgify.com',
    autoUpdate: true,
    hardwareAcceleration: true,
    securityLevel: 'high'
  }
});

class SurgifyDesktopApp {
  private mainWindow: BrowserWindow | null = null;
  private securityManager: SecurityManager;
  private updateManager: UpdateManager;
  private windowManager: WindowManager;
  private menuManager: MenuManager;
  private protocolManager: ProtocolManager;
  private ipcHandlers: IpcHandlers;

  constructor() {
    this.securityManager = new SecurityManager();
    this.updateManager = new UpdateManager();
    this.windowManager = new WindowManager();
    this.menuManager = new MenuManager();
    this.protocolManager = new ProtocolManager();
    this.ipcHandlers = new IpcHandlers();

    this.initializeApp();
  }

  private initializeApp(): void {
    // Configure app
    this.configureApp();
    
    // Set up event listeners
    this.setupEventListeners();
    
    // Configure security
    this.setupSecurity();
    
    // Set up IPC handlers
    this.setupIpcHandlers();
    
    // Set up context menu
    this.setupContextMenu();
  }

  private configureApp(): void {
    // App configuration
    app.setName('Surgify');
    app.setVersion('1.0.0');
    
    // Security settings
    app.setAsDefaultProtocolClient('surgify');
    
    // Prevent multiple instances
    const gotTheLock = app.requestSingleInstanceLock();
    if (!gotTheLock) {
      log.info('Another instance is already running, quitting...');
      app.quit();
      return;
    }

    // Handle second instance
    app.on('second-instance', () => {
      if (this.mainWindow) {
        if (this.mainWindow.isMinimized()) this.mainWindow.restore();
        this.mainWindow.focus();
      }
    });

    // Hardware acceleration
    if (!store.get('hardwareAcceleration', true)) {
      app.disableHardwareAcceleration();
    }
  }

  private setupEventListeners(): void {
    app.whenReady().then(() => {
      this.createMainWindow();
      this.setupApplicationMenu();
      this.updateManager.checkForUpdates();
    });

    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        app.quit();
      }
    });

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        this.createMainWindow();
      }
    });

    app.on('before-quit', (event) => {
      if (this.mainWindow) {
        this.windowManager.saveWindowState(this.mainWindow);
      }
    });

    // Handle certificate errors
    app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
      if (this.securityManager.isTrustedCertificate(certificate)) {
        event.preventDefault();
        callback(true);
      } else {
        callback(false);
      }
    });
  }

  private setupSecurity(): void {
    // Configure session security
    session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
      const allowedPermissions = ['camera', 'microphone', 'notifications'];
      callback(allowedPermissions.includes(permission));
    });

    // Block external navigation
    app.on('web-contents-created', (event, contents) => {
      contents.on('new-window', (navigationEvent, navigationUrl) => {
        const parsedUrl = new URL(navigationUrl);
        const allowedDomains = ['surgify.com', 'api.surgify.com'];
        
        if (!allowedDomains.includes(parsedUrl.hostname)) {
          navigationEvent.preventDefault();
          shell.openExternal(navigationUrl);
        }
      });

      contents.on('will-navigate', (navigationEvent, navigationUrl) => {
        const parsedUrl = new URL(navigationUrl);
        const allowedDomains = ['surgify.com', 'api.surgify.com', 'localhost'];
        
        if (!allowedDomains.includes(parsedUrl.hostname)) {
          navigationEvent.preventDefault();
        }
      });
    });

    // Content Security Policy
    session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
      callback({
        responseHeaders: {
          ...details.responseHeaders,
          'Content-Security-Policy': [
            "default-src 'self' https://surgify.com https://api.surgify.com; " +
            "script-src 'self' 'unsafe-inline' https://surgify.com; " +
            "style-src 'self' 'unsafe-inline' https://surgify.com; " +
            "img-src 'self' data: https://surgify.com; " +
            "connect-src 'self' https://surgify.com https://api.surgify.com; " +
            "frame-src 'none'; " +
            "object-src 'none';"
          ]
        }
      });
    });
  }

  private setupIpcHandlers(): void {
    this.ipcHandlers.register();
  }

  private setupContextMenu(): void {
    contextMenu({
      showLookUpSelection: false,
      showSearchWithGoogle: false,
      showCopyImage: false,
      prepend: (defaultActions, parameters, browserWindow) => [
        {
          label: 'Surgify Options',
          submenu: [
            {
              label: 'Reload Application',
              click: () => {
                if (this.mainWindow) {
                  this.mainWindow.reload();
                }
              }
            },
            {
              label: 'Toggle Developer Tools',
              click: () => {
                if (this.mainWindow) {
                  this.mainWindow.webContents.toggleDevTools();
                }
              }
            }
          ]
        }
      ]
    });
  }

  private createMainWindow(): void {
    // Restore window state
    const mainWindowState = windowStateKeeper({
      defaultWidth: 1200,
      defaultHeight: 800
    });

    // Create window
    this.mainWindow = new BrowserWindow({
      x: mainWindowState.x,
      y: mainWindowState.y,
      width: mainWindowState.width,
      height: mainWindowState.height,
      minWidth: 800,
      minHeight: 600,
      show: false,
      icon: this.getIconPath(),
      titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        enableRemoteModule: false,
        webSecurity: true,
        allowRunningInsecureContent: false,
        experimentalFeatures: false,
        plugins: false,
        preload: path.join(__dirname, 'preload.js')
      }
    });

    // Let windowStateKeeper manage the window
    mainWindowState.manage(this.mainWindow);

    // Load the app
    this.loadApplication();

    // Window event handlers
    this.mainWindow.once('ready-to-show', () => {
      if (this.mainWindow) {
        this.mainWindow.show();
        
        // Focus window on creation
        if (process.env.NODE_ENV === 'development') {
          this.mainWindow.webContents.openDevTools();
        }
      }
    });

    this.mainWindow.on('closed', () => {
      this.mainWindow = null;
    });

    // Handle external links
    this.mainWindow.webContents.setWindowOpenHandler(({ url }) => {
      shell.openExternal(url);
      return { action: 'deny' };
    });
  }

  private loadApplication(): void {
    if (!this.mainWindow) return;

    const serverUrl = store.get('webServerUrl', 'https://surgify.com') as string;
    
    if (process.env.NODE_ENV === 'development') {
      // In development, load from local server
      this.mainWindow.loadURL('http://localhost:8000');
    } else {
      // In production, load from configured server
      this.mainWindow.loadURL(serverUrl);
    }

    // Handle navigation
    this.mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
      log.error(`Failed to load ${validatedURL}: ${errorDescription}`);
      
      // Show error page
      this.mainWindow?.loadFile(path.join(__dirname, '../renderer/error.html'));
    });
  }

  private setupApplicationMenu(): void {
    const menu = this.menuManager.createMenu(this.mainWindow);
    Menu.setApplicationMenu(menu);
  }

  private getIconPath(): string {
    const iconName = process.platform === 'win32' ? 'icon.ico' : 
                     process.platform === 'darwin' ? 'icon.icns' : 'icon.png';
    return path.join(__dirname, '../../assets', iconName);
  }

  public getMainWindow(): BrowserWindow | null {
    return this.mainWindow;
  }
}

// Create app instance
const surgifyApp = new SurgifyDesktopApp();

// Handle app events
process.on('uncaughtException', (error) => {
  log.error('Uncaught Exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
  log.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

export { surgifyApp };
