import React from 'react';
import { TOKENS } from '../styles/tokens';
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
    const getStatusColor = () => {
        switch (connectionStatus) {
            case 'connected': return TOKENS.ok;
            case 'connecting': return TOKENS.warn;
            case 'disconnected': 
            case 'error': return TOKENS.err;
            default: return TOKENS.err;
        }
    };

    const getStatusText = () => {
        switch (connectionStatus) {
            case 'connected': return 'Connected';
            case 'connecting': return 'Connecting...';
            case 'disconnected': return 'Disconnected';
            case 'error': return 'Connection Error';
            default: return 'Unknown';
        }
    };

    return (
        <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: `${TOKENS.spacing[2]}px ${TOKENS.spacing[4]}px`,
            background: TOKENS.bg,
            borderTop: '1px solid #1c2230',
            fontSize: '12px',
            color: TOKENS.muted
        }}>
            <div style={{ display: 'flex', gap: TOKENS.spacing[4], alignItems: 'center' }}>
                <div style={{ display: 'flex', gap: TOKENS.spacing[1], alignItems: 'center' }}>
                    <div style={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        background: getStatusColor()
                    }} />
                    <span>{getStatusText()}</span>
                </div>
                <div>
                    {isAuthenticated && userInfo 
                        ? `${userInfo.name} (${userInfo.role})`
                        : 'Not logged in'
                    }
                </div>
            </div>
            <div style={{ display: 'flex', gap: TOKENS.spacing[4], alignItems: 'center' }}>
                <span>v1.0.0</span>
                <span style={{ color: securityStatus === 'secure' ? TOKENS.ok : TOKENS.warn }}>
                    {securityStatus === 'secure' ? 'Secure' : 'Warning'}
                </span>
            </div>
        </div>
    );
};
