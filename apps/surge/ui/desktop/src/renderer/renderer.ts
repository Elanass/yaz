import React from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './components/App';
import './styles/global.css';

// Initialize the React application
const container = document.getElementById('react-root');
if (container) {
    const root = createRoot(container);
    root.render(React.createElement(App));
} else {
    console.error('React root container not found');
}

// Export for potential use by other scripts
export { App };
