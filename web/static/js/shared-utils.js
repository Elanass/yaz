/**
 * Shared Utilities for Gastric ADCI Platform
 * Centralized utility functions for DRY compliance
 */

// Global Utility Namespace
window.SharedUtils = window.SharedUtils || {};

/**
 * Notification System
 */
SharedUtils.notifications = {
    show: (message, type = 'info', duration = 5000) => {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        // Styles
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 16px',
            borderRadius: '8px',
            color: 'white',
            zIndex: '9999',
            maxWidth: '300px',
            fontSize: '14px',
            fontWeight: '500',
            backgroundColor: type === 'success' ? '#10b981' : 
                           type === 'error' ? '#ef4444' :
                           type === 'warning' ? '#f59e0b' : '#3b82f6',
            boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease'
        });
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);
        
        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => notification.remove(), 300);
            }, duration);
        }
    }
};

/**
 * API Helper Functions
 */
SharedUtils.api = {
    async call(endpoint, options = {}) {
        const response = await fetch(endpoint, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`API call failed: ${response.statusText}`);
        }
        
        return response.json();
    }
};

/**
 * DOM Utilities
 */
SharedUtils.dom = {
    ready(callback) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', callback);
        } else {
            callback();
        }
    },
    
    addClass(element, className) {
        if (element) element.classList.add(className);
    },
    
    removeClass(element, className) {
        if (element) element.classList.remove(className);
    },
    
    toggleClass(element, className) {
        if (element) element.classList.toggle(className);
    }
};
