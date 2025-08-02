// Utility functions for YAZ Surgery Analytics Platform

const YAZUtils = {
    // API utilities
    api: {
        async get(url, options = {}) {
            return this.request('GET', url, null, options);
        },

        async post(url, data, options = {}) {
            return this.request('POST', url, data, options);
        },

        async put(url, data, options = {}) {
            return this.request('PUT', url, data, options);
        },

        async delete(url, options = {}) {
            return this.request('DELETE', url, null, options);
        },

        async request(method, url, data, options = {}) {
            const config = {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            };

            if (data && method !== 'GET') {
                config.body = JSON.stringify(data);
            }

            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return response.json();
        }
    },

    // Local storage utilities
    storage: {
        set(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
                return true;
            } catch (error) {
                console.error('Storage set error:', error);
                return false;
            }
        },

        get(key, defaultValue = null) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (error) {
                console.error('Storage get error:', error);
                return defaultValue;
            }
        },

        remove(key) {
            try {
                localStorage.removeItem(key);
                return true;
            } catch (error) {
                console.error('Storage remove error:', error);
                return false;
            }
        },

        clear() {
            try {
                localStorage.clear();
                return true;
            } catch (error) {
                console.error('Storage clear error:', error);
                return false;
            }
        }
    },

    // Date/time utilities
    date: {
        format(date, format = 'YYYY-MM-DD') {
            const d = new Date(date);
            const year = d.getFullYear();
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2, '0');
            const hours = String(d.getHours()).padStart(2, '0');
            const minutes = String(d.getMinutes()).padStart(2, '0');

            return format
                .replace('YYYY', year)
                .replace('MM', month)
                .replace('DD', day)
                .replace('HH', hours)
                .replace('mm', minutes);
        },

        timeAgo(date) {
            const now = new Date();
            const diff = now - new Date(date);
            const seconds = Math.floor(diff / 1000);
            const minutes = Math.floor(seconds / 60);
            const hours = Math.floor(minutes / 60);
            const days = Math.floor(hours / 24);

            if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
            if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
            if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
            return 'Just now';
        }
    },

    // Validation utilities
    validate: {
        email(email) {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(email);
        },

        required(value) {
            return value !== null && value !== undefined && value.toString().trim() !== '';
        },

        minLength(value, min) {
            return value && value.toString().length >= min;
        },

        maxLength(value, max) {
            return value && value.toString().length <= max;
        },

        numeric(value) {
            return !isNaN(value) && !isNaN(parseFloat(value));
        }
    },

    // DOM utilities
    dom: {
        create(tag, attributes = {}, children = []) {
            const element = document.createElement(tag);
            
            Object.entries(attributes).forEach(([key, value]) => {
                if (key === 'className') {
                    element.className = value;
                } else if (key === 'textContent') {
                    element.textContent = value;
                } else if (key === 'innerHTML') {
                    element.innerHTML = value;
                } else {
                    element.setAttribute(key, value);
                }
            });

            children.forEach(child => {
                if (typeof child === 'string') {
                    element.appendChild(document.createTextNode(child));
                } else {
                    element.appendChild(child);
                }
            });

            return element;
        },

        query(selector) {
            return document.querySelector(selector);
        },

        queryAll(selector) {
            return Array.from(document.querySelectorAll(selector));
        },

        addClass(element, className) {
            element.classList.add(className);
        },

        removeClass(element, className) {
            element.classList.remove(className);
        },

        toggleClass(element, className) {
            element.classList.toggle(className);
        }
    },

    // Environment detection
    env: {
        isLocal() {
            return location.hostname === 'localhost' || location.hostname === '127.0.0.1';
        },

        isP2P() {
            // Check for P2P indicators
            return this.storage.get('p2p_mode', false);
        },

        isCloud() {
            return !this.isLocal() && !this.isP2P();
        },

        getMode() {
            if (this.isP2P()) return 'p2p';
            if (this.isLocal()) return 'local';
            return 'cloud';
        }
    },

    // Error handling
    error: {
        handle(error, context = '') {
            console.error(`Error in ${context}:`, error);
            
            if (window.yazApp) {
                window.yazApp.showNotification(
                    `An error occurred${context ? ` in ${context}` : ''}. Please try again.`,
                    'error'
                );
            }
        },

        async retry(fn, maxAttempts = 3, delay = 1000) {
            for (let attempt = 1; attempt <= maxAttempts; attempt++) {
                try {
                    return await fn();
                } catch (error) {
                    if (attempt === maxAttempts) throw error;
                    await new Promise(resolve => setTimeout(resolve, delay * attempt));
                }
            }
        }
    }
};

// Make utilities globally available
window.YAZUtils = YAZUtils;

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = YAZUtils;
}
