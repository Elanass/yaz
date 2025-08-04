import React from 'react';

interface TitleBarProps {
    onMinimize: () => void;
    onMaximize: () => void;
    onClose: () => void;
}

export const TitleBar: React.FC<TitleBarProps> = ({ onMinimize, onMaximize, onClose }) => {
    return (
        <div className="title-bar">
            <div className="title-bar-title">Surgify</div>
            <div className="title-bar-controls">
                <button 
                    className="title-bar-button close" 
                    onClick={onClose}
                    aria-label="Close window"
                />
                <button 
                    className="title-bar-button minimize" 
                    onClick={onMinimize}
                    aria-label="Minimize window"
                />
                <button 
                    className="title-bar-button maximize" 
                    onClick={onMaximize}
                    aria-label="Maximize window"
                />
            </div>
        </div>
    );
};
