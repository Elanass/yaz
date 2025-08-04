import React from 'react';

interface LoadingScreenProps {
    message: string;
    subMessage?: string;
}

export const LoadingScreen: React.FC<LoadingScreenProps> = ({ message, subMessage }) => {
    return (
        <div className="loading-screen">
            <div className="loading-spinner"></div>
            <div className="loading-text">{message}</div>
            {subMessage && <div className="loading-subtext">{subMessage}</div>}
        </div>
    );
};
