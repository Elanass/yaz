import { BrowserWindow, screen } from 'electron';
import Store from 'electron-store';
import log from 'electron-log';

export interface WindowState {
  x?: number;
  y?: number;
  width: number;
  height: number;
  isMaximized: boolean;
  isFullScreen: boolean;
}

export interface WindowConfig {
  defaultWidth: number;
  defaultHeight: number;
  minWidth: number;
  minHeight: number;
  rememberPosition: boolean;
  rememberSize: boolean;
  centerOnScreen: boolean;
}

export class WindowManager {
  private store: Store<{ windowState: WindowState; windowConfig: WindowConfig }>;

  constructor() {
    this.store = new Store({
      name: 'surgify-window',
      defaults: {
        windowState: {
          width: 1200,
          height: 800,
          isMaximized: false,
          isFullScreen: false
        },
        windowConfig: {
          defaultWidth: 1200,
          defaultHeight: 800,
          minWidth: 800,
          minHeight: 600,
          rememberPosition: true,
          rememberSize: true,
          centerOnScreen: true
        }
      }
    });
  }

  public getWindowState(): WindowState {
    const state = this.store.get('windowState');
    const config = this.store.get('windowConfig');

    // Validate the stored state
    const validatedState = this.validateWindowState(state);

    // If position should be centered or is invalid, calculate center position
    if (config.centerOnScreen || (!validatedState.x && !validatedState.y)) {
      const centerPosition = this.getCenterPosition(validatedState.width, validatedState.height);
      validatedState.x = centerPosition.x;
      validatedState.y = centerPosition.y;
    }

    return validatedState;
  }

  public saveWindowState(window: BrowserWindow): void {
    const config = this.store.get('windowConfig');
    
    if (!config.rememberPosition && !config.rememberSize) {
      return;
    }

    const bounds = window.getBounds();
    const state: WindowState = {
      isMaximized: window.isMaximized(),
      isFullScreen: window.isFullScreen(),
      width: bounds.width,
      height: bounds.height
    };

    if (config.rememberPosition && !window.isMaximized() && !window.isFullScreen()) {
      state.x = bounds.x;
      state.y = bounds.y;
    }

    if (config.rememberSize && !window.isMaximized() && !window.isFullScreen()) {
      state.width = bounds.width;
      state.height = bounds.height;
    }

    this.store.set('windowState', state);
    log.info('Window state saved:', state);
  }

  public createWindow(options: Partial<Electron.BrowserWindowConstructorOptions> = {}): BrowserWindow {
    const state = this.getWindowState();
    const config = this.store.get('windowConfig');

    const windowOptions: Electron.BrowserWindowConstructorOptions = {
      x: state.x,
      y: state.y,
      width: state.width,
      height: state.height,
      minWidth: config.minWidth,
      minHeight: config.minHeight,
      show: false, // Don't show until ready
      ...options
    };

    const window = new BrowserWindow(windowOptions);

    // Restore window state
    if (state.isMaximized) {
      window.maximize();
    }

    if (state.isFullScreen) {
      window.setFullScreen(true);
    }

    // Set up event listeners for this window
    this.setupWindowEventListeners(window);

    return window;
  }

  private setupWindowEventListeners(window: BrowserWindow): void {
    // Save state when window is moved or resized
    let saveStateTimeout: NodeJS.Timeout;

    const debouncedSaveState = () => {
      clearTimeout(saveStateTimeout);
      saveStateTimeout = setTimeout(() => {
        this.saveWindowState(window);
      }, 500); // Debounce to avoid excessive saves
    };

    window.on('resize', debouncedSaveState);
    window.on('move', debouncedSaveState);
    window.on('maximize', debouncedSaveState);
    window.on('unmaximize', debouncedSaveState);
    window.on('enter-full-screen', debouncedSaveState);
    window.on('leave-full-screen', debouncedSaveState);

    // Final save when window is closed
    window.on('close', () => {
      clearTimeout(saveStateTimeout);
      this.saveWindowState(window);
    });
  }

  private validateWindowState(state: WindowState): WindowState {
    const config = this.store.get('windowConfig');
    const displays = screen.getAllDisplays();
    
    // Ensure minimum dimensions
    state.width = Math.max(state.width, config.minWidth);
    state.height = Math.max(state.height, config.minHeight);

    // Validate position is on screen
    if (state.x !== undefined && state.y !== undefined) {
      const windowBounds = {
        x: state.x,
        y: state.y,
        width: state.width,
        height: state.height
      };

      const isOnScreen = displays.some(display => {
        const { x, y, width, height } = display.bounds;
        return (
          windowBounds.x < x + width &&
          windowBounds.x + windowBounds.width > x &&
          windowBounds.y < y + height &&
          windowBounds.y + windowBounds.height > y
        );
      });

      if (!isOnScreen) {
        log.warn('Window position is off-screen, centering window');
        delete state.x;
        delete state.y;
      }
    }

    return state;
  }

  private getCenterPosition(width: number, height: number): { x: number; y: number } {
    const primaryDisplay = screen.getPrimaryDisplay();
    const { width: screenWidth, height: screenHeight } = primaryDisplay.workAreaSize;
    
    return {
      x: Math.round((screenWidth - width) / 2),
      y: Math.round((screenHeight - height) / 2)
    };
  }

  public resetWindowState(): void {
    const config = this.store.get('windowConfig');
    const centerPosition = this.getCenterPosition(config.defaultWidth, config.defaultHeight);
    
    const defaultState: WindowState = {
      x: centerPosition.x,
      y: centerPosition.y,
      width: config.defaultWidth,
      height: config.defaultHeight,
      isMaximized: false,
      isFullScreen: false
    };

    this.store.set('windowState', defaultState);
    log.info('Window state reset to defaults');
  }

  public getWindowConfig(): WindowConfig {
    return this.store.get('windowConfig');
  }

  public updateWindowConfig(updates: Partial<WindowConfig>): void {
    const currentConfig = this.store.get('windowConfig');
    const newConfig = { ...currentConfig, ...updates };
    this.store.set('windowConfig', newConfig);
    log.info('Window configuration updated:', updates);
  }

  public getAllDisplayInfo(): Electron.Display[] {
    return screen.getAllDisplays();
  }

  public getPrimaryDisplayInfo(): Electron.Display {
    return screen.getPrimaryDisplay();
  }

  public getDisplayAt(x: number, y: number): Electron.Display {
    return screen.getDisplayNearestPoint({ x, y });
  }

  public isPointOnScreen(x: number, y: number): boolean {
    const displays = screen.getAllDisplays();
    return displays.some(display => {
      const { x: dx, y: dy, width, height } = display.bounds;
      return x >= dx && x < dx + width && y >= dy && y < dy + height;
    });
  }

  public getScreenScaleFactor(): number {
    return screen.getPrimaryDisplay().scaleFactor;
  }

  public getWorkAreaSize(): Electron.Size {
    return screen.getPrimaryDisplay().workAreaSize;
  }
}
