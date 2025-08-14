import { autoUpdater } from 'electron-updater';
import { dialog, BrowserWindow } from 'electron';
import log from 'electron-log';
import Store from 'electron-store';

export interface UpdateConfig {
  autoUpdate: boolean;
  checkInterval: number; // in milliseconds
  allowPrerelease: boolean;
  downloadInBackground: boolean;
}

export class UpdateManager {
  private store: Store<UpdateConfig>;
  private updateCheckInterval?: NodeJS.Timeout;

  constructor() {
    this.store = new Store<UpdateConfig>({
      name: 'surgify-updates',
      defaults: {
        autoUpdate: true,
        checkInterval: 24 * 60 * 60 * 1000, // 24 hours
        allowPrerelease: false,
        downloadInBackground: true
      }
    });

    this.configureAutoUpdater();
    this.setupEventHandlers();
  }

  private configureAutoUpdater(): void {
    // Configure auto-updater
    autoUpdater.logger = log;
    autoUpdater.autoDownload = this.store.get('downloadInBackground', true);
    autoUpdater.allowPrerelease = this.store.get('allowPrerelease', false);
    
    // Set update server URL
    if (process.env.NODE_ENV === 'development') {
      autoUpdater.updateConfigPath = './dev-app-update.yml';
    }
  }

  private setupEventHandlers(): void {
    autoUpdater.on('checking-for-update', () => {
      log.info('Checking for update...');
    });

    autoUpdater.on('update-available', (info) => {
      log.info('Update available:', info);
      this.handleUpdateAvailable(info);
    });

    autoUpdater.on('update-not-available', (info) => {
      log.info('Update not available:', info);
    });

    autoUpdater.on('error', (err) => {
      log.error('Update error:', err);
      this.handleUpdateError(err);
    });

    autoUpdater.on('download-progress', (progressObj) => {
      const message = `Download speed: ${progressObj.bytesPerSecond} - Downloaded ${progressObj.percent}% (${progressObj.transferred}/${progressObj.total})`;
      log.info(message);
      this.handleDownloadProgress(progressObj);
    });

    autoUpdater.on('update-downloaded', (info) => {
      log.info('Update downloaded:', info);
      this.handleUpdateDownloaded(info);
    });
  }

  public checkForUpdates(): void {
    if (!this.store.get('autoUpdate', true)) {
      log.info('Auto-update disabled, skipping check');
      return;
    }

    autoUpdater.checkForUpdatesAndNotify().catch(err => {
      log.error('Failed to check for updates:', err);
    });
  }

  public startPeriodicChecks(): void {
    const interval = this.store.get('checkInterval', 24 * 60 * 60 * 1000);
    
    if (this.updateCheckInterval) {
      clearInterval(this.updateCheckInterval);
    }

    this.updateCheckInterval = setInterval(() => {
      this.checkForUpdates();
    }, interval);

    log.info(`Started periodic update checks every ${interval / 1000 / 60 / 60} hours`);
  }

  public stopPeriodicChecks(): void {
    if (this.updateCheckInterval) {
      clearInterval(this.updateCheckInterval);
      this.updateCheckInterval = undefined;
      log.info('Stopped periodic update checks');
    }
  }

  private async handleUpdateAvailable(info: any): Promise<void> {
    const mainWindow = BrowserWindow.getAllWindows()[0];
    
    if (!mainWindow) return;

    const response = await dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update Available',
      message: `A new version of Surgify is available (v${info.version})`,
      detail: 'Would you like to download and install it now?',
      buttons: ['Download Now', 'Later', 'View Release Notes'],
      defaultId: 0,
      cancelId: 1
    });

    switch (response.response) {
      case 0: // Download Now
        if (!this.store.get('downloadInBackground', true)) {
          autoUpdater.downloadUpdate();
        }
        break;
      case 2: // View Release Notes
        // Open release notes URL
        const { shell } = require('electron');
        shell.openExternal(`https://github.com/surgify/desktop/releases/tag/v${info.version}`);
        break;
    }
  }

  private handleDownloadProgress(progressObj: any): void {
    const mainWindow = BrowserWindow.getAllWindows()[0];
    if (mainWindow) {
      // Send progress to renderer process
      mainWindow.webContents.send('update-download-progress', {
        percent: Math.round(progressObj.percent),
        transferred: progressObj.transferred,
        total: progressObj.total,
        bytesPerSecond: progressObj.bytesPerSecond
      });
    }
  }

  private async handleUpdateDownloaded(info: any): Promise<void> {
    const mainWindow = BrowserWindow.getAllWindows()[0];
    
    if (!mainWindow) {
      // Auto-install if no window is open
      autoUpdater.quitAndInstall();
      return;
    }

    const response = await dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update Downloaded',
      message: 'Update has been downloaded successfully',
      detail: 'The application will restart to apply the update. Any unsaved work will be lost.',
      buttons: ['Restart Now', 'Restart Later'],
      defaultId: 0,
      cancelId: 1
    });

    if (response.response === 0) {
      autoUpdater.quitAndInstall();
    } else {
      // Notify user they can restart later
      mainWindow.webContents.send('update-ready-to-install');
    }
  }

  private async handleUpdateError(error: Error): Promise<void> {
    const mainWindow = BrowserWindow.getAllWindows()[0];
    
    if (!mainWindow) return;

    await dialog.showErrorBox(
      'Update Error',
      `An error occurred while checking for updates: ${error.message}`
    );
  }

  public installUpdateNow(): void {
    autoUpdater.quitAndInstall();
  }

  public setAutoUpdate(enabled: boolean): void {
    this.store.set('autoUpdate', enabled);
    
    if (enabled) {
      this.startPeriodicChecks();
    } else {
      this.stopPeriodicChecks();
    }
    
    log.info(`Auto-update ${enabled ? 'enabled' : 'disabled'}`);
  }

  public setCheckInterval(interval: number): void {
    this.store.set('checkInterval', interval);
    
    if (this.store.get('autoUpdate', true)) {
      this.startPeriodicChecks();
    }
    
    log.info(`Update check interval set to ${interval / 1000 / 60 / 60} hours`);
  }

  public setAllowPrerelease(allow: boolean): void {
    this.store.set('allowPrerelease', allow);
    autoUpdater.allowPrerelease = allow;
    log.info(`Prerelease updates ${allow ? 'enabled' : 'disabled'}`);
  }

  public getUpdateConfig(): UpdateConfig {
    return {
      autoUpdate: this.store.get('autoUpdate', true),
      checkInterval: this.store.get('checkInterval', 24 * 60 * 60 * 1000),
      allowPrerelease: this.store.get('allowPrerelease', false),
      downloadInBackground: this.store.get('downloadInBackground', true)
    };
  }

  public async checkForUpdatesManually(): Promise<void> {
    try {
      const result = await autoUpdater.checkForUpdates();
      
      if (!result?.updateInfo) {
        const mainWindow = BrowserWindow.getAllWindows()[0];
        if (mainWindow) {
          dialog.showMessageBox(mainWindow, {
            type: 'info',
            title: 'No Updates',
            message: 'You are running the latest version of Surgify',
            buttons: ['OK']
          });
        }
      }
    } catch (error) {
      log.error('Manual update check failed:', error);
      throw error;
    }
  }
}
