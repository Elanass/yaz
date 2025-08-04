import React from 'react';
import { UserInfo } from '../types/global';

interface StatusBarProps {
    connectionStatus: 'connected' | 'connecting' | 'disconnected' | 'error';
    isAuthenticated: boolean;
    userInfo: UserInfo | null;
    securityStatus: 'secure' | 'warning' | 'error';
    currentUrl: string;
}

export const StatusBar: React.FC<StatusBarProps> = ({
    connectionStatus,
    isAuthenticated,
    userInfo,
    securityStatus,
    currentUrl
}) => {
    const getConnectionStatusText = () => {
        switch (connectionStatus) {
            case 'connected': return 'Connected';
            case 'connecting': return 'Connecting...';
            case 'disconnected': return 'Disconnected';
            case 'error': return 'Connection Error';
            default: return 'Unknown';
        }
    };

    const getConnectionStatusClass = () => {
        switch (connectionStatus) {
            case 'connected': return 'status-dot';
            case 'connecting': return 'status-dot warning';
            case 'disconnected': 
            case 'error': return 'status-dot error';
            default: return 'status-dot error';
        }
    };

    const getUserDisplayText = () => {
        if (isAuthenticated && userInfo) {
            return `${userInfo.name} (${userInfo.role})`;
        }
        return 'Not logged in';
    };

    const getSecurityStatusText = () => {
        switch (securityStatus) {
            case 'secure': return 'Secure';
            case 'warning': return 'Warning';
            case 'error': return 'Insecure';
            default: return 'Unknown';
        }
    };

    return (
        <div className="status-bar">
            <div className="status-left">
                <div className="status-indicator">
                    <div className={getConnectionStatusClass()} />
                    <span>{getConnectionStatusText()}</span>
                </div>
                <div className="status-indicator">
                    <span>{getUserDisplayText()}</span>
                </div>
            </div>
            <div className="status-right">
                <div className="status-indicator">
                    <span>v1.0.0</span>
                </div>
                <div className="status-indicator">
                    <span>{getSecurityStatusText()}</span>
                </div>
            </div>
        </div>
    );
};
