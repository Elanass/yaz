import { Menu, MenuItem, BrowserWindow, app, shell, dialog } from 'electron';
import log from 'electron-log';

export class MenuManager {
  public createMenu(mainWindow: BrowserWindow | null): Menu {
    const template: Electron.MenuItemConstructorOptions[] = [
      {
        label: 'Surgify',
        submenu: [
          {
            label: 'About Surgify',
            click: () => this.showAboutDialog(mainWindow)
          },
          { type: 'separator' },
          {
            label: 'Preferences...',
            accelerator: process.platform === 'darwin' ? 'Cmd+,' : 'Ctrl+,',
            click: () => this.openPreferences(mainWindow)
          },
          { type: 'separator' },
          {
            label: 'Check for Updates...',
            click: () => this.checkForUpdates()
          },
          { type: 'separator' },
          {
            label: 'Quit',
            accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
            click: () => app.quit()
          }
        ]
      },
      {
        label: 'File',
        submenu: [
          {
            label: 'New Case',
            accelerator: 'CmdOrCtrl+N',
            click: () => this.sendToRenderer(mainWindow, 'menu-new-case')
          },
          {
            label: 'Open Case',
            accelerator: 'CmdOrCtrl+O',
            click: () => this.sendToRenderer(mainWindow, 'menu-open-case')
          },
          { type: 'separator' },
          {
            label: 'Save',
            accelerator: 'CmdOrCtrl+S',
            click: () => this.sendToRenderer(mainWindow, 'menu-save')
          },
          {
            label: 'Save As...',
            accelerator: 'CmdOrCtrl+Shift+S',
            click: () => this.sendToRenderer(mainWindow, 'menu-save-as')
          },
          { type: 'separator' },
          {
            label: 'Export Case Data...',
            click: () => this.exportCaseData(mainWindow)
          },
          {
            label: 'Import Case Data...',
            click: () => this.importCaseData(mainWindow)
          },
          { type: 'separator' },
          {
            label: 'Print',
            accelerator: 'CmdOrCtrl+P',
            click: () => this.printPage(mainWindow)
          }
        ]
      },
      {
        label: 'Edit',
        submenu: [
          {
            label: 'Undo',
            accelerator: 'CmdOrCtrl+Z',
            role: 'undo'
          },
          {
            label: 'Redo',
            accelerator: 'CmdOrCtrl+Y',
            role: 'redo'
          },
          { type: 'separator' },
          {
            label: 'Cut',
            accelerator: 'CmdOrCtrl+X',
            role: 'cut'
          },
          {
            label: 'Copy',
            accelerator: 'CmdOrCtrl+C',
            role: 'copy'
          },
          {
            label: 'Paste',
            accelerator: 'CmdOrCtrl+V',
            role: 'paste'
          },
          {
            label: 'Select All',
            accelerator: 'CmdOrCtrl+A',
            role: 'selectAll'
          },
          { type: 'separator' },
          {
            label: 'Find',
            accelerator: 'CmdOrCtrl+F',
            click: () => this.sendToRenderer(mainWindow, 'menu-find')
          }
        ]
      },
      {
        label: 'View',
        submenu: [
          {
            label: 'Reload',
            accelerator: 'CmdOrCtrl+R',
            click: () => mainWindow?.reload()
          },
          {
            label: 'Force Reload',
            accelerator: 'CmdOrCtrl+Shift+R',
            click: () => mainWindow?.webContents.reloadIgnoringCache()
          },
          {
            label: 'Toggle Developer Tools',
            accelerator: process.platform === 'darwin' ? 'Alt+Cmd+I' : 'Ctrl+Shift+I',
            click: () => mainWindow?.webContents.toggleDevTools()
          },
          { type: 'separator' },
          {
            label: 'Actual Size',
            accelerator: 'CmdOrCtrl+0',
            click: () => mainWindow?.webContents.setZoomLevel(0)
          },
          {
            label: 'Zoom In',
            accelerator: 'CmdOrCtrl+Plus',
            click: () => this.zoomIn(mainWindow)
          },
          {
            label: 'Zoom Out',
            accelerator: 'CmdOrCtrl+-',
            click: () => this.zoomOut(mainWindow)
          },
          { type: 'separator' },
          {
            label: 'Toggle Fullscreen',
            accelerator: process.platform === 'darwin' ? 'Ctrl+Cmd+F' : 'F11',
            click: () => this.toggleFullscreen(mainWindow)
          }
        ]
      },
      {
        label: 'Navigation',
        submenu: [
          {
            label: 'Dashboard',
            accelerator: 'CmdOrCtrl+1',
            click: () => this.sendToRenderer(mainWindow, 'navigate-dashboard')
          },
          {
            label: 'Cases',
            accelerator: 'CmdOrCtrl+2',
            click: () => this.sendToRenderer(mainWindow, 'navigate-cases')
          },
          {
            label: 'Analytics',
            accelerator: 'CmdOrCtrl+3',
            click: () => this.sendToRenderer(mainWindow, 'navigate-analytics')
          },
          {
            label: 'Settings',
            accelerator: 'CmdOrCtrl+4',
            click: () => this.sendToRenderer(mainWindow, 'navigate-settings')
          },
          { type: 'separator' },
          {
            label: 'Back',
            accelerator: 'CmdOrCtrl+Left',
            click: () => this.sendToRenderer(mainWindow, 'navigate-back')
          },
          {
            label: 'Forward',
            accelerator: 'CmdOrCtrl+Right',
            click: () => this.sendToRenderer(mainWindow, 'navigate-forward')
          }
        ]
      },
      {
        label: 'Tools',
        submenu: [
          {
            label: 'Camera Capture',
            accelerator: 'CmdOrCtrl+Shift+C',
            click: () => this.sendToRenderer(mainWindow, 'tool-camera')
          },
          {
            label: 'Voice Recording',
            accelerator: 'CmdOrCtrl+Shift+V',
            click: () => this.sendToRenderer(mainWindow, 'tool-voice')
          },
          { type: 'separator' },
          {
            label: 'Data Sync',
            click: () => this.sendToRenderer(mainWindow, 'tool-sync')
          },
          {
            label: 'Backup Data',
            click: () => this.backupData(mainWindow)
          },
          { type: 'separator' },
          {
            label: 'Security Check',
            click: () => this.runSecurityCheck(mainWindow)
          }
        ]
      },
      {
        label: 'Window',
        submenu: [
          {
            label: 'Minimize',
            accelerator: 'CmdOrCtrl+M',
            role: 'minimize'
          },
          {
            label: 'Close',
            accelerator: 'CmdOrCtrl+W',
            role: 'close'
          },
          { type: 'separator' },
          {
            label: 'Bring All to Front',
            role: 'front'
          }
        ]
      },
      {
        label: 'Help',
        submenu: [
          {
            label: 'User Guide',
            click: () => shell.openExternal('https://surgify.com/help/user-guide')
          },
          {
            label: 'Video Tutorials',
            click: () => shell.openExternal('https://surgify.com/help/tutorials')
          },
          {
            label: 'Keyboard Shortcuts',
            click: () => this.showKeyboardShortcuts(mainWindow)
          },
          { type: 'separator' },
          {
            label: 'Report Issue',
            click: () => shell.openExternal('https://surgify.com/support/report-issue')
          },
          {
            label: 'Contact Support',
            click: () => shell.openExternal('https://surgify.com/support/contact')
          },
          { type: 'separator' },
          {
            label: 'About Surgify',
            click: () => this.showAboutDialog(mainWindow)
          }
        ]
      }
    ];

    // Platform-specific menu adjustments
    if (process.platform === 'darwin') {
      // macOS specific menu adjustments
      template[0].submenu = [
        { label: 'About Surgify', role: 'about' },
        { type: 'separator' },
        { label: 'Services', role: 'services', submenu: [] },
        { type: 'separator' },
        { label: 'Hide Surgify', accelerator: 'Command+H', role: 'hide' },
        { label: 'Hide Others', accelerator: 'Command+Shift+H', role: 'hideothers' },
        { label: 'Show All', role: 'unhide' },
        { type: 'separator' },
        { label: 'Quit', accelerator: 'Command+Q', click: () => app.quit() }
      ];
    }

    return Menu.buildFromTemplate(template);
  }

  private sendToRenderer(window: BrowserWindow | null, channel: string, ...args: any[]): void {
    if (window && !window.isDestroyed()) {
      window.webContents.send(channel, ...args);
    }
  }

  private async showAboutDialog(window: BrowserWindow | null): Promise<void> {
    if (!window) return;

    await dialog.showMessageBox(window, {
      type: 'info',
      title: 'About Surgify',
      message: 'Surgify Desktop',
      detail: `Version: ${app.getVersion()}\nElectron: ${process.versions.electron}\nNode.js: ${process.versions.node}\nChromium: ${process.versions.chrome}`,
      buttons: ['OK']
    });
  }

  private openPreferences(window: BrowserWindow | null): void {
    this.sendToRenderer(window, 'open-preferences');
  }

  private checkForUpdates(): void {
    // This would trigger the UpdateManager
    log.info('Manual update check requested');
  }

  private async exportCaseData(window: BrowserWindow | null): Promise<void> {
    if (!window) return;

    const result = await dialog.showSaveDialog(window, {
      title: 'Export Case Data',
      defaultPath: 'surgify-cases.json',
      filters: [
        { name: 'JSON Files', extensions: ['json'] },
        { name: 'CSV Files', extensions: ['csv'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });

    if (!result.canceled && result.filePath) {
      this.sendToRenderer(window, 'export-case-data', result.filePath);
    }
  }

  private async importCaseData(window: BrowserWindow | null): Promise<void> {
    if (!window) return;

    const result = await dialog.showOpenDialog(window, {
      title: 'Import Case Data',
      filters: [
        { name: 'JSON Files', extensions: ['json'] },
        { name: 'CSV Files', extensions: ['csv'] },
        { name: 'All Files', extensions: ['*'] }
      ],
      properties: ['openFile']
    });

    if (!result.canceled && result.filePaths.length > 0) {
      this.sendToRenderer(window, 'import-case-data', result.filePaths[0]);
    }
  }

  private printPage(window: BrowserWindow | null): void {
    if (window) {
      window.webContents.print();
    }
  }

  private zoomIn(window: BrowserWindow | null): void {
    if (window) {
      const currentZoom = window.webContents.getZoomLevel();
      window.webContents.setZoomLevel(Math.min(currentZoom + 0.5, 3));
    }
  }

  private zoomOut(window: BrowserWindow | null): void {
    if (window) {
      const currentZoom = window.webContents.getZoomLevel();
      window.webContents.setZoomLevel(Math.max(currentZoom - 0.5, -3));
    }
  }

  private toggleFullscreen(window: BrowserWindow | null): void {
    if (window) {
      window.setFullScreen(!window.isFullScreen());
    }
  }

  private async backupData(window: BrowserWindow | null): Promise<void> {
    if (!window) return;

    const result = await dialog.showSaveDialog(window, {
      title: 'Backup Data',
      defaultPath: `surgify-backup-${new Date().toISOString().split('T')[0]}.zip`,
      filters: [
        { name: 'Backup Files', extensions: ['zip'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });

    if (!result.canceled && result.filePath) {
      this.sendToRenderer(window, 'backup-data', result.filePath);
    }
  }

  private runSecurityCheck(window: BrowserWindow | null): void {
    this.sendToRenderer(window, 'run-security-check');
  }

  private async showKeyboardShortcuts(window: BrowserWindow | null): Promise<void> {
    if (!window) return;

    const shortcuts = [
      'File Operations:',
      '  Ctrl+N - New Case',
      '  Ctrl+O - Open Case',
      '  Ctrl+S - Save',
      '  Ctrl+P - Print',
      '',
      'Navigation:',
      '  Ctrl+1 - Dashboard',
      '  Ctrl+2 - Cases',
      '  Ctrl+3 - Analytics',
      '  Ctrl+4 - Settings',
      '',
      'Tools:',
      '  Ctrl+Shift+C - Camera Capture',
      '  Ctrl+Shift+V - Voice Recording',
      '',
      'View:',
      '  Ctrl+R - Reload',
      '  F11 - Toggle Fullscreen',
      '  Ctrl+Plus - Zoom In',
      '  Ctrl+Minus - Zoom Out'
    ].join('\n');

    await dialog.showMessageBox(window, {
      type: 'info',
      title: 'Keyboard Shortcuts',
      message: 'Surgify Keyboard Shortcuts',
      detail: shortcuts,
      buttons: ['OK']
    });
  }
}
