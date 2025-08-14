import React from 'react';

interface OfflineScreenProps {
    onRetry: () => void;
}

export const OfflineScreen: React.FC<OfflineScreenProps> = ({ onRetry }) => {
    return (
        <div className="offline-message">
            <h2>Connection Lost</h2>
            <p>Unable to connect to Surgify servers. Please check your internet connection.</p>
            <button className="retry-button" onClick={onRetry}>
                Retry Connection
            </button>
        </div>
    );
};
