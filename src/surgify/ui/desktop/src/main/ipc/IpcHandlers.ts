import { ipcMain, app, shell, dialog, BrowserWindow } from 'electron';
import log from 'electron-log';
import Store from 'electron-store';
import * as fs from 'fs';
import * as path from 'path';

export class IpcHandlers {
  private store: Store;

  constructor() {
    this.store = new Store();
  }

  public register(): void {
    // App information
    ipcMain.handle('app:getVersion', () => {
      return app.getVersion();
    });

    ipcMain.handle('app:getName', () => {
      return app.getName();
    });

    ipcMain.handle('app:getPath', (event, name: string) => {
      return app.getPath(name as any);
    });

    // Window management
    ipcMain.handle('window:minimize', (event) => {
      const window = BrowserWindow.fromWebContents(event.sender);
      window?.minimize();
    });

    ipcMain.handle('window:maximize', (event) => {
      const window = BrowserWindow.fromWebContents(event.sender);
      if (window?.isMaximized()) {
        window.unmaximize();
      } else {
        window?.maximize();
      }
    });

    ipcMain.handle('window:close', (event) => {
      const window = BrowserWindow.fromWebContents(event.sender);
      window?.close();
    });

    ipcMain.handle('window:isMaximized', (event) => {
      const window = BrowserWindow.fromWebContents(event.sender);
      return window?.isMaximized() || false;
    });

    ipcMain.handle('window:setAlwaysOnTop', (event, flag: boolean) => {
      const window = BrowserWindow.fromWebContents(event.sender);
      window?.setAlwaysOnTop(flag);
    });

    // Dialog operations
    ipcMain.handle('dialog:showMessageBox', async (event, options) => {
      const window = BrowserWindow.fromWebContents(event.sender);
      if (!window) return null;
      
      const result = await dialog.showMessageBox(window, options);
      return result;
    });

    ipcMain.handle('dialog:showErrorBox', async (event, title: string, content: string) => {
      dialog.showErrorBox(title, content);
    });

    ipcMain.handle('dialog:showOpenDialog', async (event, options) => {
      const window = BrowserWindow.fromWebContents(event.sender);
      if (!window) return null;
      
      const result = await dialog.showOpenDialog(window, options);
      return result;
    });

    ipcMain.handle('dialog:showSaveDialog', async (event, options) => {
      const window = BrowserWindow.fromWebContents(event.sender);
      if (!window) return null;
      
      const result = await dialog.showSaveDialog(window, options);
      return result;
    });

    // File system operations
    ipcMain.handle('fs:readFile', async (event, filePath: string) => {
      try {
        const content = await fs.promises.readFile(filePath, 'utf8');
        return { success: true, content };
      } catch (error) {
        log.error('Failed to read file:', error);
        return { success: false, error: (error as Error).message };
      }
    });

    ipcMain.handle('fs:writeFile', async (event, filePath: string, content: string) => {
      try {
        await fs.promises.writeFile(filePath, content, 'utf8');
        return { success: true };
      } catch (error) {
        log.error('Failed to write file:', error);
        return { success: false, error: (error as Error).message };
      }
    });

    ipcMain.handle('fs:exists', async (event, filePath: string) => {
      try {
        await fs.promises.access(filePath);
        return true;
      } catch {
        return false;
      }
    });

    ipcMain.handle('fs:mkdir', async (event, dirPath: string) => {
      try {
        await fs.promises.mkdir(dirPath, { recursive: true });
        return { success: true };
      } catch (error) {
        log.error('Failed to create directory:', error);
        return { success: false, error: (error as Error).message };
      }
    });

    // Store operations
    ipcMain.handle('store:get', (event, key: string, defaultValue?: any) => {
      return this.store.get(key, defaultValue);
    });

    ipcMain.handle('store:set', (event, key: string, value: any) => {
      this.store.set(key, value);
      return true;
    });

    ipcMain.handle('store:delete', (event, key: string) => {
      this.store.delete(key);
      return true;
    });

    ipcMain.handle('store:clear', (event) => {
      this.store.clear();
      return true;
    });

    ipcMain.handle('store:has', (event, key: string) => {
      return this.store.has(key);
    });

    ipcMain.handle('store:size', (event) => {
      return this.store.size;
    });

    // Shell operations
    ipcMain.handle('shell:openExternal', async (event, url: string) => {
      try {
        await shell.openExternal(url);
        return { success: true };
      } catch (error) {
        log.error('Failed to open external URL:', error);
        return { success: false, error: (error as Error).message };
      }
    });

    ipcMain.handle('shell:openPath', async (event, path: string) => {
      try {
        const result = await shell.openPath(path);
        return { success: !result, error: result || undefined };
      } catch (error) {
        log.error('Failed to open path:', error);
        return { success: false, error: (error as Error).message };
      }
    });

    ipcMain.handle('shell:showItemInFolder', (event, fullPath: string) => {
      shell.showItemInFolder(fullPath);
      return { success: true };
    });

    // Camera operations (placeholder for future implementation)
    ipcMain.handle('camera:getDevices', async (event) => {
      // This would integrate with actual camera APIs
      return { success: true, devices: [] };
    });

    ipcMain.handle('camera:capture', async (event, options: any) => {
      // This would integrate with actual camera APIs
      return { success: false, error: 'Camera not implemented yet' };
    });

    // Print operations
    ipcMain.handle('print:page', async (event, options?: any) => {
      const window = BrowserWindow.fromWebContents(event.sender);
      if (!window) return { success: false, error: 'No window found' };

      try {
        await window.webContents.print(options);
        return { success: true };
      } catch (error) {
        log.error('Print failed:', error);
        return { success: false, error: (error as Error).message };
      }
    });

    ipcMain.handle('print:toPDF', async (event, options?: any) => {
      const window = BrowserWindow.fromWebContents(event.sender);
      if (!window) return { success: false, error: 'No window found' };

      try {
        const data = await window.webContents.printToPDF(options || {});
        return { success: true, data };
      } catch (error) {
        log.error('Print to PDF failed:', error);
        return { success: false, error: (error as Error).message };
      }
    });

    // Security operations
    ipcMain.handle('security:getFingerprint', async (event) => {
      // Generate a unique device fingerprint
      const machineId = require('node-machine-id').machineIdSync();
      return { success: true, fingerprint: machineId };
    });

    ipcMain.handle('security:isSecureContext', (event) => {
      // Check if the app is running in a secure context
      return {
        success: true,
        isSecure: process.env.NODE_ENV === 'production',
        isDev: process.env.NODE_ENV === 'development'
      };
    });

    // Update operations
    ipcMain.handle('update:check', async (event) => {
      // This would integrate with the UpdateManager
      return { success: true, updateAvailable: false };
    });

    ipcMain.handle('update:install', async (event) => {
      // This would integrate with the UpdateManager
      return { success: false, error: 'No update available' };
    });

    // Backup operations
    ipcMain.handle('backup:create', async (event, backupPath: string) => {
      try {
        // This would create a backup of user data
        const userDataPath = app.getPath('userData');
        const backupData = {
          timestamp: new Date().toISOString(),
          version: app.getVersion(),
          userData: userDataPath
        };

        await fs.promises.writeFile(
          backupPath,
          JSON.stringify(backupData, null, 2),
          'utf8'
        );

        return { success: true };
      } catch (error) {
        log.error('Backup creation failed:', error);
        return { success: false, error: (error as Error).message };
      }
    });

    ipcMain.handle('backup:restore', async (event, backupPath: string) => {
      try {
        // This would restore from a backup file
        const backupContent = await fs.promises.readFile(backupPath, 'utf8');
        const backupData = JSON.parse(backupContent);

        // Validate backup data
        if (!backupData.timestamp || !backupData.version) {
          throw new Error('Invalid backup file format');
        }

        return { success: true, backupData };
      } catch (error) {
        log.error('Backup restoration failed:', error);
        return { success: false, error: (error as Error).message };
      }
    });

    // System information
    ipcMain.handle('system:getInfo', (event) => {
      const os = require('os');
      return {
        success: true,
        info: {
          platform: process.platform,
          arch: process.arch,
          nodeVersion: process.version,
          electronVersion: process.versions.electron,
          chromeVersion: process.versions.chrome,
          totalMemory: os.totalmem(),
          freeMemory: os.freemem(),
          cpus: os.cpus().length,
          uptime: os.uptime()
        }
      };
    });

    log.info('IPC handlers registered');
  }
}
