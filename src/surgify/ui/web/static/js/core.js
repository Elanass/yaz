// Core JavaScript - Essential functionality for all pages

// Simple utility functions
const YAZ = {
    // API helper
    async fetch(url, options = {}) {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return response.json();
    },
    
    // Simple element selector
    $(selector) {
        return document.querySelector(selector);
    },
    
    // Show/hide loading state
    setLoading(element, loading = true) {
        if (loading) {
            element.style.opacity = '0.5';
            element.style.pointerEvents = 'none';
        } else {
            element.style.opacity = '1';
            element.style.pointerEvents = 'auto';
        }
    },
    
    // Simple notification
    notify(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
};

// Basic form handling
document.addEventListener('DOMContentLoaded', function() {
    // Auto-submit forms with data-auto-submit
    const autoForms = document.querySelectorAll('form[data-auto-submit]');
    autoForms.forEach(form => {
        form.addEventListener('change', () => {
            form.submit();
        });
    });
    
    // Simple loading states for buttons
    const buttons = document.querySelectorAll('button[type="submit"]');
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            button.textContent = 'Loading...';
            button.disabled = true;
        });
    });
});

// Export for module use
window.YAZ = YAZ;
