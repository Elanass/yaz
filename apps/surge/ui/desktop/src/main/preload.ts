import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // App information
  getVersion: () => ipcRenderer.invoke('app:getVersion'),
  getName: () => ipcRenderer.invoke('app:getName'),
  getPath: (name: string) => ipcRenderer.invoke('app:getPath', name),

  // Window management
  minimizeWindow: () => ipcRenderer.invoke('window:minimize'),
  maximizeWindow: () => ipcRenderer.invoke('window:maximize'),
  closeWindow: () => ipcRenderer.invoke('window:close'),
  isMaximized: () => ipcRenderer.invoke('window:isMaximized'),
  setAlwaysOnTop: (flag: boolean) => ipcRenderer.invoke('window:setAlwaysOnTop', flag),

  // Dialog operations
  showMessageBox: (options: any) => ipcRenderer.invoke('dialog:showMessageBox', options),
  showErrorBox: (title: string, content: string) => ipcRenderer.invoke('dialog:showErrorBox', title, content),
  showOpenDialog: (options: any) => ipcRenderer.invoke('dialog:showOpenDialog', options),
  showSaveDialog: (options: any) => ipcRenderer.invoke('dialog:showSaveDialog', options),

  // File system operations
  readFile: (filePath: string) => ipcRenderer.invoke('fs:readFile', filePath),
  writeFile: (filePath: string, content: string) => ipcRenderer.invoke('fs:writeFile', filePath, content),
  fileExists: (filePath: string) => ipcRenderer.invoke('fs:exists', filePath),
  createDirectory: (dirPath: string) => ipcRenderer.invoke('fs:mkdir', dirPath),

  // Store operations
  storeGet: (key: string, defaultValue?: any) => ipcRenderer.invoke('store:get', key, defaultValue),
  storeSet: (key: string, value: any) => ipcRenderer.invoke('store:set', key, value),
  storeDelete: (key: string) => ipcRenderer.invoke('store:delete', key),
  storeClear: () => ipcRenderer.invoke('store:clear'),
  storeHas: (key: string) => ipcRenderer.invoke('store:has', key),
  storeSize: () => ipcRenderer.invoke('store:size'),

  // Shell operations
  openExternal: (url: string) => ipcRenderer.invoke('shell:openExternal', url),
  openPath: (path: string) => ipcRenderer.invoke('shell:openPath', path),
  showItemInFolder: (fullPath: string) => ipcRenderer.invoke('shell:showItemInFolder', fullPath),

  // Camera operations
  getCameraDevices: () => ipcRenderer.invoke('camera:getDevices'),
  captureImage: (options: any) => ipcRenderer.invoke('camera:capture', options),

  // Print operations
  printPage: (options?: any) => ipcRenderer.invoke('print:page', options),
  printToPDF: (options?: any) => ipcRenderer.invoke('print:toPDF', options),

  // Security operations
  getFingerprint: () => ipcRenderer.invoke('security:getFingerprint'),
  isSecureContext: () => ipcRenderer.invoke('security:isSecureContext'),

  // Update operations
  checkForUpdates: () => ipcRenderer.invoke('update:check'),
  installUpdate: () => ipcRenderer.invoke('update:install'),

  // Backup operations
  createBackup: (backupPath: string) => ipcRenderer.invoke('backup:create', backupPath),
  restoreBackup: (backupPath: string) => ipcRenderer.invoke('backup:restore', backupPath),

  // System information
  getSystemInfo: () => ipcRenderer.invoke('system:getInfo'),

  // Event listeners for renderer process
  onMenuAction: (callback: (action: string, ...args: any[]) => void) => {
    const wrappedCallback = (event: any, action: string, ...args: any[]) => callback(action, ...args);
    ipcRenderer.on('menu-action', wrappedCallback);
    
    // Return a cleanup function
    return () => ipcRenderer.removeListener('menu-action', wrappedCallback);
  },

  onUpdateDownloadProgress: (callback: (progress: any) => void) => {
    const wrappedCallback = (event: any, progress: any) => callback(progress);
    ipcRenderer.on('update-download-progress', wrappedCallback);
    
    return () => ipcRenderer.removeListener('update-download-progress', wrappedCallback);
  },

  onUpdateReadyToInstall: (callback: () => void) => {
    const wrappedCallback = () => callback();
    ipcRenderer.on('update-ready-to-install', wrappedCallback);
    
    return () => ipcRenderer.removeListener('update-ready-to-install', wrappedCallback);
  },

  // Menu-triggered actions
  onNewCase: (callback: () => void) => {
    const wrappedCallback = () => callback();
    ipcRenderer.on('menu-new-case', wrappedCallback);
    return () => ipcRenderer.removeListener('menu-new-case', wrappedCallback);
  },

  onOpenCase: (callback: () => void) => {
    const wrappedCallback = () => callback();
    ipcRenderer.on('menu-open-case', wrappedCallback);
    return () => ipcRenderer.removeListener('menu-open-case', wrappedCallback);
  },

  onSave: (callback: () => void) => {
    const wrappedCallback = () => callback();
    ipcRenderer.on('menu-save', wrappedCallback);
    return () => ipcRenderer.removeListener('menu-save', wrappedCallback);
  },

  onSaveAs: (callback: () => void) => {
    const wrappedCallback = () => callback();
    ipcRenderer.on('menu-save-as', wrappedCallback);
    return () => ipcRenderer.removeListener('menu-save-as', wrappedCallback);
  },

  onFind: (callback: () => void) => {
    const wrappedCallback = () => callback();
    ipcRenderer.on('menu-find', wrappedCallback);
    return () => ipcRenderer.removeListener('menu-find', wrappedCallback);
  },

  onNavigate: (callback: (destination: string) => void) => {
    const dashboardCallback = () => callback('dashboard');
    const casesCallback = () => callback('cases');
    const analyticsCallback = () => callback('analytics');
    const settingsCallback = () => callback('settings');
    const backCallback = () => callback('back');
    const forwardCallback = () => callback('forward');

    ipcRenderer.on('navigate-dashboard', dashboardCallback);
    ipcRenderer.on('navigate-cases', casesCallback);
    ipcRenderer.on('navigate-analytics', analyticsCallback);
    ipcRenderer.on('navigate-settings', settingsCallback);
    ipcRenderer.on('navigate-back', backCallback);
    ipcRenderer.on('navigate-forward', forwardCallback);

    return () => {
      ipcRenderer.removeListener('navigate-dashboard', dashboardCallback);
      ipcRenderer.removeListener('navigate-cases', casesCallback);
      ipcRenderer.removeListener('navigate-analytics', analyticsCallback);
      ipcRenderer.removeListener('navigate-settings', settingsCallback);
      ipcRenderer.removeListener('navigate-back', backCallback);
      ipcRenderer.removeListener('navigate-forward', forwardCallback);
    };
  },

  onToolAction: (callback: (tool: string) => void) => {
    const cameraCallback = () => callback('camera');
    const voiceCallback = () => callback('voice');
    const syncCallback = () => callback('sync');

    ipcRenderer.on('tool-camera', cameraCallback);
    ipcRenderer.on('tool-voice', voiceCallback);
    ipcRenderer.on('tool-sync', syncCallback);

    return () => {
      ipcRenderer.removeListener('tool-camera', cameraCallback);
      ipcRenderer.removeListener('tool-voice', voiceCallback);
      ipcRenderer.removeListener('tool-sync', syncCallback);
    };
  },

  onExportData: (callback: (filePath: string) => void) => {
    const wrappedCallback = (event: any, filePath: string) => callback(filePath);
    ipcRenderer.on('export-case-data', wrappedCallback);
    return () => ipcRenderer.removeListener('export-case-data', wrappedCallback);
  },

  onImportData: (callback: (filePath: string) => void) => {
    const wrappedCallback = (event: any, filePath: string) => callback(filePath);
    ipcRenderer.on('import-case-data', wrappedCallback);
    return () => ipcRenderer.removeListener('import-case-data', wrappedCallback);
  },

  onBackupData: (callback: (filePath: string) => void) => {
    const wrappedCallback = (event: any, filePath: string) => callback(filePath);
    ipcRenderer.on('backup-data', wrappedCallback);
    return () => ipcRenderer.removeListener('backup-data', wrappedCallback);
  },

  onRunSecurityCheck: (callback: () => void) => {
    const wrappedCallback = () => callback();
    ipcRenderer.on('run-security-check', wrappedCallback);
    return () => ipcRenderer.removeListener('run-security-check', wrappedCallback);
  },

  onOpenPreferences: (callback: () => void) => {
    const wrappedCallback = () => callback();
    ipcRenderer.on('open-preferences', wrappedCallback);
    return () => ipcRenderer.removeListener('open-preferences', wrappedCallback);
  },

  // Remove all listeners (cleanup)
  removeAllListeners: () => {
    ipcRenderer.removeAllListeners('menu-action');
    ipcRenderer.removeAllListeners('update-download-progress');
    ipcRenderer.removeAllListeners('update-ready-to-install');
    ipcRenderer.removeAllListeners('menu-new-case');
    ipcRenderer.removeAllListeners('menu-open-case');
    ipcRenderer.removeAllListeners('menu-save');
    ipcRenderer.removeAllListeners('menu-save-as');
    ipcRenderer.removeAllListeners('menu-find');
    ipcRenderer.removeAllListeners('navigate-dashboard');
    ipcRenderer.removeAllListeners('navigate-cases');
    ipcRenderer.removeAllListeners('navigate-analytics');
    ipcRenderer.removeAllListeners('navigate-settings');
    ipcRenderer.removeAllListeners('navigate-back');
    ipcRenderer.removeAllListeners('navigate-forward');
    ipcRenderer.removeAllListeners('tool-camera');
    ipcRenderer.removeAllListeners('tool-voice');
    ipcRenderer.removeAllListeners('tool-sync');
    ipcRenderer.removeAllListeners('export-case-data');
    ipcRenderer.removeAllListeners('import-case-data');
    ipcRenderer.removeAllListeners('backup-data');
    ipcRenderer.removeAllListeners('run-security-check');
    ipcRenderer.removeAllListeners('open-preferences');
  }
});

// Expose environment information
contextBridge.exposeInMainWorld('environment', {
  platform: process.platform,
  arch: process.arch,
  nodeVersion: process.versions.node,
  electronVersion: process.versions.electron,
  chromeVersion: process.versions.chrome
});
