// Global type definitions for the Electron renderer process

declare global {
    interface Window {
        electronAPI: {
            // Window controls
            windowControl: (action: 'minimize' | 'maximize' | 'close') => void;
            
            // App lifecycle
            onAppReady: (callback: () => void) => void;
            onAppWillQuit: (callback: () => void) => void;
            
            // Security
            validateCertificate: (url: string) => Promise<boolean>;
            checkSecurityStatus: () => Promise<'secure' | 'warning' | 'error'>;
            
            // Authentication
            getAuthToken: () => Promise<string | null>;
            setAuthToken: (token: string) => Promise<void>;
            clearAuthToken: () => Promise<void>;
            
            // Storage
            store: {
                get: (key: string) => Promise<any>;
                set: (key: string, value: any) => Promise<void>;
                delete: (key: string) => Promise<void>;
                clear: () => Promise<void>;
            };
            
            // Updates
            checkForUpdates: () => Promise<void>;
            onUpdateAvailable: (callback: (info: any) => void) => void;
            onUpdateDownloaded: (callback: () => void) => void;
            installUpdate: () => void;
            
            // Network
            isOnline: () => Promise<boolean>;
            onNetworkChange: (callback: (isOnline: boolean) => void) => void;
            
            // Camera and Media (placeholders for future implementation)
            getCameraPermission: () => Promise<boolean>;
            startCamera: () => Promise<void>;
            stopCamera: () => Promise<void>;
            
            // Voice (placeholders for future implementation)
            getMicrophonePermission: () => Promise<boolean>;
            startVoiceRecording: () => Promise<void>;
            stopVoiceRecording: () => Promise<Blob>;
            
            // External links
            openExternal: (url: string) => void;
        };
    }
}

export interface UserInfo {
    id: string;
    name: string;
    email: string;
    role: string;
    avatar?: string;
}

export interface AuthStatus {
    isAuthenticated: boolean;
    userInfo: UserInfo | null;
    token?: string;
}

export interface ConnectionStatus {
    status: 'connected' | 'connecting' | 'disconnected' | 'error';
    lastConnected?: Date;
    latency?: number;
}

export interface SecurityStatus {
    status: 'secure' | 'warning' | 'error';
    certificateValid: boolean;
    connectionSecure: boolean;
    lastCheck: Date;
}

export {};
