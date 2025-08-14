import React, { useState } from 'react';
import { TOKENS } from '../styles/tokens';
import { Card } from './Primitives';
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
    const [showThemeToggle] = useState(true); // Dev-only toggle

    const getConnectionStatusText = () => {
        switch (connectionStatus) {
            case 'connected': return 'Connected';
            case 'connecting': return 'Connecting...';
            case 'disconnected': return 'Disconnected';
            case 'error': return 'Connection Error';
            default: return 'Unknown';
        }
    };

    const getConnectionStatusColor = () => {
        switch (connectionStatus) {
            case 'connected': return TOKENS.ok;
            case 'connecting': return TOKENS.warn;
            case 'disconnected': 
            case 'error': return TOKENS.err;
            default: return TOKENS.muted;
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

    const getSecurityStatusColor = () => {
        switch (securityStatus) {
            case 'secure': return TOKENS.ok;
            case 'warning': return TOKENS.warn;
            case 'error': return TOKENS.err;
            default: return TOKENS.muted;
        }
    };

    return (
        <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: `${TOKENS.spacing[2]}px ${TOKENS.spacing[4]}px`,
            background: TOKENS.bg,
            borderTop: `1px solid #1c2230`,
            fontSize: '12px',
            fontFamily: TOKENS.fontUI
        }}>
            {/* Left Section */}
            <div style={{ display: 'flex', alignItems: 'center', gap: TOKENS.spacing[4] }}>
                {/* Connection Status */}
                <div style={{ display: 'flex', alignItems: 'center', gap: TOKENS.spacing[2] }}>
                    <div style={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        background: getConnectionStatusColor(),
                        animation: connectionStatus === 'connecting' ? 'pulse 2s infinite' : 'none'
                    }} />
                    <span style={{ color: TOKENS.text }}>
                        {getConnectionStatusText()}
                    </span>
                </div>

                {/* User Info */}
                <div style={{ color: TOKENS.muted }}>
                    {getUserDisplayText()}
                </div>

                {/* Current URL/Route */}
                <div style={{ 
                    color: TOKENS.muted,
                    maxWidth: '200px',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                }}>
                    {currentUrl || 'yaz://surge'}
                </div>
            </div>

            {/* Right Section */}
            <div style={{ display: 'flex', alignItems: 'center', gap: TOKENS.spacing[4] }}>
                {/* Dev Theme Toggle */}
                {showThemeToggle && (
                    <Card pad={6} style={{ 
                        border: `1px solid #1c2230`,
                        background: TOKENS.elev
                    }}>
                        <button
                            style={{
                                background: 'transparent',
                                border: 'none',
                                color: TOKENS.brand,
                                fontSize: '11px',
                                cursor: 'pointer',
                                fontFamily: TOKENS.fontUI,
                                fontWeight: 500
                            }}
                            onClick={() => {
                                // Toggle UI theme in development
                                const isDev = process.env.NODE_ENV === 'development';
                                if (isDev) {
                                    // Implementation would go here
                                    console.log('Theme toggle clicked');
                                }
                            }}
                            title="Toggle UI Theme (Dev Only)"
                        >
                            <svg width="12" height="12" fill="currentColor" viewBox="0 0 24 24" style={{ marginRight: '4px' }}>
                                <path d="M12 2.25a.75.75 0 01.75.75v2.25a.75.75 0 01-1.5 0V3a.75.75 0 01.75-.75zM7.5 12a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM18.894 6.166a.75.75 0 00-1.06-1.06l-1.591 1.59a.75.75 0 101.06 1.061l1.591-1.59zM21.75 12a.75.75 0 01-.75.75h-2.25a.75.75 0 010-1.5H21a.75.75 0 01.75.75zM17.834 18.894a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 10-1.061 1.06l1.59 1.591zM12 18a.75.75 0 01.75.75V21a.75.75 0 01-1.5 0v-2.25A.75.75 0 0112 18zM7.758 17.303a.75.75 0 00-1.061-1.06l-1.591 1.59a.75.75 0 001.06 1.061l1.591-1.59zM6 12a.75.75 0 01-.75.75H3a.75.75 0 010-1.5h2.25A.75.75 0 016 12zM6.697 7.757a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 00-1.061 1.06l1.59 1.591z"/>
                            </svg>
                            UI
                        </button>
                    </Card>
                )}

                {/* Security Status */}
                <div style={{ display: 'flex', alignItems: 'center', gap: TOKENS.spacing[2] }}>
                    <svg width="12" height="12" fill={getSecurityStatusColor()} viewBox="0 0 24 24">
                        <path fillRule="evenodd" d="M12.516 2.17a.75.75 0 00-1.032 0 11.209 11.209 0 01-7.877 3.08.75.75 0 00-.722.515A12.74 12.74 0 002.25 9.75c0 5.814 3.720 10.764 9 12.185a.75.75 0 00.495 0c5.280-1.421 9-6.171 9-12.185 0-1.39-.223-2.73-.635-3.985a.75.75 0 00-.722-.515 11.209 11.209 0 01-7.877-3.08z" clipRule="evenodd"/>
                    </svg>
                    <span style={{ color: getSecurityStatusColor() }}>
                        {getSecurityStatusText()}
                    </span>
                </div>

                {/* App Version */}
                <div style={{ color: TOKENS.muted }}>
                    v2.1.0
                </div>

                {/* Performance Indicator */}
                <div style={{ display: 'flex', alignItems: 'center', gap: TOKENS.spacing[1] }}>
                    <div style={{
                        width: 6,
                        height: 6,
                        borderRadius: '50%',
                        background: TOKENS.ok
                    }} />
                    <span style={{ color: TOKENS.muted }}>
                        Fast
                    </span>
                </div>
            </div>
        </div>
    );
};
