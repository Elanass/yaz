/**
 * Base Component Class and Utilities
 * Common patterns extracted from UI components for DRY principles
 */

class BaseComponent {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            // Default options
            autoRefresh: false,
            refreshInterval: 30000,
            showLoading: true,
            apiBase: '/api/v1',
            ...options
        };
        
        this.data = {};
        this.initialized = false;
        this.refreshTimer = null;
        this.eventListeners = [];
    }

    // Common initialization pattern
    async init() {
        try {
            await this.loadData();
            this.render();
            this.attachEventListeners();
            this.initialized = true;
            
            if (this.options.autoRefresh) {
                this.startAutoRefresh();
            }
        } catch (error) {
            this.handleError('Initialization failed', error);
        }
    }

    // Abstract methods to be implemented by subclasses
    async loadData() {
        throw new Error('loadData method must be implemented by subclass');
    }

    render() {
        throw new Error('render method must be implemented by subclass');
    }

    // Common utility methods
    getContainer() {
        return document.getElementById(this.containerId);
    }

    setLoading(loading = true) {
        const container = this.getContainer();
        if (container) {
            if (loading) {
                container.classList.add('component-loading');
            } else {
                container.classList.remove('component-loading');
            }
        }
    }

    async makeApiCall(endpoint, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.getAuthToken()}`
            }
        };

        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: { ...defaultOptions.headers, ...options.headers }
        };

        const response = await fetch(`${this.options.apiBase}${endpoint}`, mergedOptions);
        
        if (!response.ok) {
            throw new Error(`API call failed: ${response.status} ${response.statusText}`);
        }
        
        return response.json();
    }

    getAuthToken() {
        return localStorage.getItem('authToken') || '';
    }

    formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }

    formatCurrency(amount, currency = '$') {
        if (amount == null) return `${currency}0.00`;
        return `${currency}${Number(amount).toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        })}`;
    }

    formatPercentage(value, decimals = 1) {
        if (value == null) return '0.0%';
        return `${Number(value).toFixed(decimals)}%`;
    }

    createElement(tag, className = '', content = '') {
        const element = document.createElement(tag);
        if (className) element.className = className;
        if (content) element.innerHTML = content;
        return element;
    }

    // Event handling
    addEventListener(element, event, handler) {
        element.addEventListener(event, handler);
        this.eventListeners.push({ element, event, handler });
    }

    attachEventListeners() {
        // To be implemented by subclasses
    }

    // Auto refresh functionality
    startAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }
        
        this.refreshTimer = setInterval(async () => {
            try {
                await this.refreshData();
            } catch (error) {
                this.handleError('Auto refresh failed', error);
            }
        }, this.options.refreshInterval);
    }

    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    async refreshData() {
        this.setLoading(true);
        await this.loadData();
        this.render();
        this.setLoading(false);
    }

    // Error handling
    handleError(message, error) {
        console.error(`${this.constructor.name}: ${message}`, error);
        this.showError(message);
    }

    showError(message) {
        const container = this.getContainer();
        if (container) {
            const errorDiv = this.createElement('div', 'error-message', 
                `<p><strong>Error:</strong> ${message}</p>`);
            container.prepend(errorDiv);
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                if (errorDiv.parentNode) {
                    errorDiv.parentNode.removeChild(errorDiv);
                }
            }, 5000);
        }
    }

    // Cleanup
    destroy() {
        this.stopAutoRefresh();
        
        // Remove event listeners
        this.eventListeners.forEach(({ element, event, handler }) => {
            element.removeEventListener(event, handler);
        });
        this.eventListeners = [];
        
        // Clear container
        const container = this.getContainer();
        if (container) {
            container.innerHTML = '';
        }
        
        this.initialized = false;
    }

    // Public methods
    setData(newData) {
        this.data = newData;
        if (this.initialized) {
            this.render();
        }
    }

    getData() {
        return this.data;
    }

    getOptions() {
        return this.options;
    }

    updateOptions(newOptions) {
        this.options = { ...this.options, ...newOptions };
    }
}

// Common utility functions for components
const ComponentUtils = {
    // Generate unique IDs for components
    generateId(prefix = 'comp') {
        const timestamp = Date.now();
        const random = Math.floor(Math.random() * 1000);
        return `${prefix}-${timestamp}-${random}`;
    },

    // Debounce function calls
    debounce(func, delay) {
        let timeoutId;
        return function (...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    },

    // Throttle function calls
    throttle(func, limit) {
        let inThrottle;
        return function (...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    // Deep clone object
    deepClone(obj) {
        return JSON.parse(JSON.stringify(obj));
    },

    // Merge objects
    mergeObjects(obj1, obj2) {
        return { ...obj1, ...obj2 };
    },

    // Format file size
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Validate email
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    // Escape HTML
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    // Show notification
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span>${ComponentUtils.escapeHtml(message)}</span>
            <button class="notification-close">&times;</button>
        `;

        document.body.appendChild(notification);

        // Auto-hide
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, duration);

        // Manual close
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        });
    },

    // Local storage with expiration
    setLocalStorageWithExpiry(key, value, ttl = 3600000) { // default 1 hour
        const now = new Date();
        const item = {
            value: value,
            expiry: now.getTime() + ttl
        };
        localStorage.setItem(key, JSON.stringify(item));
    },

    getLocalStorageWithExpiry(key) {
        const itemStr = localStorage.getItem(key);
        if (!itemStr) return null;

        const item = JSON.parse(itemStr);
        const now = new Date();

        if (now.getTime() > item.expiry) {
            localStorage.removeItem(key);
            return null;
        }
        return item.value;
    }
};

// Export for use in other components
if (typeof window !== 'undefined') {
    window.BaseComponent = BaseComponent;
    window.ComponentUtils = ComponentUtils;
}
