import React from 'react';
import { WebViewManager } from '../services/WebViewManager';

interface WebViewContainerProps {
    isVisible: boolean;
    webViewManager: WebViewManager;
}

export const WebViewContainer: React.FC<WebViewContainerProps> = ({ isVisible, webViewManager }) => {
    return (
        <div className={`webview-container ${isVisible ? '' : 'hidden'}`}>
            <webview 
                className="webview" 
                id="webview"
                src="about:blank"
                nodeintegration="false"
                websecurity="true"
                allowpopups="false"
                preload="./preload.js"
            />
        </div>
    );
};
