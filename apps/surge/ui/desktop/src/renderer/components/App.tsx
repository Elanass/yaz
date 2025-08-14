import React, { useState, useEffect, useCallback } from 'react';
import { TOKENS } from '../styles/tokens';
import { Card } from './Primitives';
import { WebViewManager } from '../services/WebViewManager';
import { AuthManager } from '../services/AuthManager';
import { ConnectionManager } from '../services/ConnectionManager';
import { TitleBar } from './TitleBar';
import { StatusBar } from './StatusBar';
import { LoadingScreen } from './LoadingScreen';
import { OfflineScreen } from './OfflineScreen';
import { WebViewContainer } from './WebViewContainer';

export interface AppState {
    isLoading: boolean;
    isOnline: boolean;
    isAuthenticated: boolean;
    userInfo: {
        name?: string;
        email?: string;
        role?: string;
    } | null;
    connectionStatus: 'connected' | 'connecting' | 'disconnected' | 'error';
    currentUrl: string;
    securityStatus: 'secure' | 'warning' | 'error';
    uiTheme?: 'legacy' | 'new'; // Dev theme toggle
}

export const App: React.FC = () => {
    const [state, setState] = useState<AppState>({
        isLoading: true,
        isOnline: navigator.onLine,
        isAuthenticated: false,
        userInfo: null,
        connectionStatus: 'connecting',
        currentUrl: '',
        securityStatus: 'secure',
        uiTheme: 'new' // Default to new UI for development
    });

    const webViewManager = new WebViewManager();
    const authManager = new AuthManager();
    const connectionManager = new ConnectionManager();

    // Handle connection status changes
    const handleConnectionChange = useCallback((status: AppState['connectionStatus']) => {
        setState(prev => ({ ...prev, connectionStatus: status }));
    }, []);

    // Handle authentication changes
    const handleAuthChange = useCallback((isAuthenticated: boolean, userInfo: AppState['userInfo']) => {
        setState(prev => ({ 
            ...prev, 
            isAuthenticated, 
            userInfo,
            isLoading: false 
        }));
    }, []);

    // Handle online/offline status
    const handleOnlineStatusChange = useCallback(() => {
        const isOnline = navigator.onLine;
        setState(prev => ({ ...prev, isOnline }));
        
        if (isOnline) {
            connectionManager.reconnect();
        }
    }, [connectionManager]);

    // Handle URL changes
    const handleUrlChange = useCallback((url: string) => {
        setState(prev => ({ ...prev, currentUrl: url }));
    }, []);

    // Handle security status changes
    const handleSecurityStatusChange = useCallback((status: AppState['securityStatus']) => {
        setState(prev => ({ ...prev, securityStatus: status }));
    }, []);

    // Initialize the application
    useEffect(() => {
        const initializeApp = async () => {
            try {
                // Initialize services
                await webViewManager.initialize();
                await authManager.initialize();
                await connectionManager.initialize();

                // Set up event listeners
                connectionManager.onStatusChange(handleConnectionChange);
                authManager.onAuthChange(handleAuthChange);
                webViewManager.onUrlChange(handleUrlChange);
                webViewManager.onSecurityStatusChange(handleSecurityStatusChange);

                // Check initial authentication status
                const authStatus = await authManager.checkAuthStatus();
                handleAuthChange(authStatus.isAuthenticated, authStatus.userInfo);

                // Load the main application
                await webViewManager.loadUrl('https://surgify.com/workstation');

            } catch (error) {
                console.error('Failed to initialize app:', error);
                setState(prev => ({ 
                    ...prev, 
                    isLoading: false, 
                    connectionStatus: 'error',
                    securityStatus: 'error'
                }));
            }
        };

        initializeApp();

        // Set up online/offline listeners
        window.addEventListener('online', handleOnlineStatusChange);
        window.addEventListener('offline', handleOnlineStatusChange);

        return () => {
            window.removeEventListener('online', handleOnlineStatusChange);
            window.removeEventListener('offline', handleOnlineStatusChange);
        };
    }, []);

    // Handle retry connection
    const handleRetryConnection = useCallback(async () => {
        setState(prev => ({ ...prev, connectionStatus: 'connecting' }));
        try {
            await connectionManager.reconnect();
            await webViewManager.reload();
        } catch (error) {
            console.error('Reconnection failed:', error);
            setState(prev => ({ ...prev, connectionStatus: 'error' }));
        }
    }, [connectionManager, webViewManager]);

    // Handle window controls
    const handleMinimize = useCallback(() => {
        window.electronAPI?.windowControl('minimize');
    }, []);

    const handleMaximize = useCallback(() => {
        window.electronAPI?.windowControl('maximize');
    }, []);

    const handleClose = useCallback(() => {
        window.electronAPI?.windowControl('close');
    }, []);

    return (
        <div className="app-container">
            <TitleBar
                onMinimize={handleMinimize}
                onMaximize={handleMaximize}
                onClose={handleClose}
            />
            
            <div className="content-area">
                {state.isLoading && (
                    <LoadingScreen 
                        message="Loading Surgify..."
                        subMessage="Connecting to secure servers"
                    />
                )}

                {!state.isOnline && !state.isLoading && (
                    <OfflineScreen onRetry={handleRetryConnection} />
                )}

                <WebViewContainer
                    isVisible={!state.isLoading && state.isOnline}
                    webViewManager={webViewManager}
                />
            </div>

            <StatusBar
                connectionStatus={state.connectionStatus}
                isAuthenticated={state.isAuthenticated}
                userInfo={state.userInfo}
                securityStatus={state.securityStatus}
                currentUrl={state.currentUrl}
            />
        </div>
    );
};
