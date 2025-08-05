/**
 * Cross-Browser Compatibility Utilities
 * Ensures Surgify UI works across all browsers including Zen browser
 */

class BrowserCompatibility {
    constructor() {
        this.browserInfo = this.detectBrowser();
        this.capabilities = this.checkCapabilities();
        this.polyfills = new Map();
        
        this.init();
    }
    
    init() {
        this.loadPolyfills();
        this.setupEventListeners();
        this.fixKnownIssues();
        
        // Log browser info for debugging
        console.log('Browser detected:', this.browserInfo);
        if (this.browserInfo.name === 'zen') {
            console.log('Zen browser detected - applying compatibility fixes');
        }
    }
    
    detectBrowser() {
        const userAgent = navigator.userAgent.toLowerCase();
        const vendor = navigator.vendor?.toLowerCase() || '';
        
        // Zen browser detection
        if (userAgent.includes('zen/') || userAgent.includes('zen browser')) {
            return {
                name: 'zen',
                version: this.extractVersion(userAgent, /zen[\/\s]([0-9.]+)/),
                engine: 'gecko', // Zen is based on Firefox
                isMobile: /mobile|android|iphone|ipad/.test(userAgent)
            };
        }
        
        // Firefox detection
        if (userAgent.includes('firefox') && !userAgent.includes('seamonkey')) {
            return {
                name: 'firefox',
                version: this.extractVersion(userAgent, /firefox[\/\s]([0-9.]+)/),
                engine: 'gecko',
                isMobile: /mobile/.test(userAgent)
            };
        }
        
        // Chrome detection
        if (userAgent.includes('chrome') && !userAgent.includes('edg') && !userAgent.includes('opr')) {
            return {
                name: 'chrome',
                version: this.extractVersion(userAgent, /chrome[\/\s]([0-9.]+)/),
                engine: 'blink',
                isMobile: /mobile/.test(userAgent)
            };
        }
        
        // Safari detection
        if (userAgent.includes('safari') && !userAgent.includes('chrome')) {
            return {
                name: 'safari',
                version: this.extractVersion(userAgent, /version[\/\s]([0-9.]+)/),
                engine: 'webkit',
                isMobile: /mobile|iphone|ipad/.test(userAgent)
            };
        }
        
        // Edge detection
        if (userAgent.includes('edg')) {
            return {
                name: 'edge',
                version: this.extractVersion(userAgent, /edg[\/\s]([0-9.]+)/),
                engine: 'blink',
                isMobile: /mobile/.test(userAgent)
            };
        }
        
        // Fallback
        return {
            name: 'unknown',
            version: '0.0.0',
            engine: 'unknown',
            isMobile: /mobile/.test(userAgent)
        };
    }
    
    extractVersion(userAgent, regex) {
        const match = userAgent.match(regex);
        return match ? match[1] : '0.0.0';
    }
    
    checkCapabilities() {
        return {
            flexbox: this.supportsCSS('display', 'flex'),
            grid: this.supportsCSS('display', 'grid'),
            customProperties: this.supportsCSS('--test', '1'),
            webComponents: 'customElements' in window,
            intersectionObserver: 'IntersectionObserver' in window,
            resizeObserver: 'ResizeObserver' in window,
            fetch: 'fetch' in window,
            es6: this.supportsES6(),
            webGL: this.supportsWebGL(),
            localforage: 'indexedDB' in window
        };
    }
    
    supportsCSS(property, value) {
        const element = document.createElement('div');
        element.style[property] = value;
        return element.style[property] === value;
    }
    
    supportsES6() {
        try {
            eval('const test = () => {}; class Test {}');
            return true;
        } catch (e) {
            return false;
        }
    }
    
    supportsWebGL() {
        try {
            const canvas = document.createElement('canvas');
            return !!(window.WebGLRenderingContext && 
                     (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
        } catch (e) {
            return false;
        }
    }
    
    loadPolyfills() {
        // Fetch polyfill
        if (!this.capabilities.fetch) {
            this.loadPolyfill('fetch', 'https://cdn.jsdelivr.net/npm/whatwg-fetch@3.6.2/dist/fetch.umd.js');
        }
        
        // IntersectionObserver polyfill
        if (!this.capabilities.intersectionObserver) {
            this.loadPolyfill('intersectionObserver', 
                'https://cdn.jsdelivr.net/npm/intersection-observer@0.12.2/intersection-observer.js');
        }
        
        // ResizeObserver polyfill
        if (!this.capabilities.resizeObserver) {
            this.loadPolyfill('resizeObserver',
                'https://cdn.jsdelivr.net/npm/resize-observer-polyfill@1.5.1/dist/ResizeObserver.global.js');
        }
        
        // Custom Properties polyfill for older browsers
        if (!this.capabilities.customProperties) {
            this.loadPolyfill('customProperties',
                'https://cdn.jsdelivr.net/npm/css-vars-ponyfill@2.4.8/dist/css-vars-ponyfill.min.js');
        }
    }
    
    async loadPolyfill(name, url) {
        return new Promise((resolve, reject) => {
            if (this.polyfills.has(name)) {
                resolve();
                return;
            }
            
            const script = document.createElement('script');
            script.src = url;
            script.async = true;
            script.onload = () => {
                this.polyfills.set(name, true);
                console.log(`Loaded polyfill: ${name}`);
                resolve();
            };
            script.onerror = () => {
                console.error(`Failed to load polyfill: ${name}`);
                reject(new Error(`Failed to load ${name} polyfill`));
            };
            
            document.head.appendChild(script);
        });
    }
    
    setupEventListeners() {
        // Handle viewport changes for mobile
        if (this.browserInfo.isMobile) {
            this.setupMobileViewportFix();
        }
        
        // Handle focus/blur for better accessibility
        this.setupFocusManagement();
        
        // Handle touch events for touch devices
        this.setupTouchSupport();
    }
    
    setupMobileViewportFix() {
        const setViewportHeight = () => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        };
        
        setViewportHeight();
        window.addEventListener('resize', setViewportHeight, { passive: true });
        window.addEventListener('orientationchange', setViewportHeight, { passive: true });
    }
    
    setupFocusManagement() {
        // Better keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-nav');
            }
        });
        
        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-nav');
        });
    }
    
    setupTouchSupport() {
        // Add touch classes for styling
        if ('ontouchstart' in window) {
            document.documentElement.classList.add('touch');
        } else {
            document.documentElement.classList.add('no-touch');
        }
        
        // Prevent double-tap zoom on iOS
        let lastTouchEnd = 0;
        document.addEventListener('touchend', (e) => {
            const now = Date.now();
            if (now - lastTouchEnd <= 300) {
                e.preventDefault();
            }
            lastTouchEnd = now;
        }, { passive: false });
    }
    
    fixKnownIssues() {
        // Zen browser specific fixes
        if (this.browserInfo.name === 'zen') {
            this.applyZenBrowserFixes();
        }
        
        // Firefox specific fixes
        if (this.browserInfo.name === 'firefox' || this.browserInfo.name === 'zen') {
            this.applyFirefoxFixes();
        }
        
        // Safari specific fixes
        if (this.browserInfo.name === 'safari') {
            this.applySafariFixes();
        }
        
        // General CSS fixes
        this.applyGeneralFixes();
    }
    
    applyZenBrowserFixes() {
        // Add Zen-specific CSS class
        document.documentElement.classList.add('zen-browser');
        
        // Fix scrollbar styling for Zen
        const style = document.createElement('style');
        style.textContent = `
            /* Zen browser scrollbar fixes */
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: var(--bg-secondary, #f5f5f5);
            }
            
            ::-webkit-scrollbar-thumb {
                background: var(--border-color, #d1d5db);
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: var(--text-tertiary, #6b7280);
            }
            
            /* Fix for modal z-index issues in Zen */
            .modal, .dropdown, .tooltip {
                z-index: 9999 !important;
            }
            
            /* Fix for form validation in Zen */
            input:invalid {
                box-shadow: none;
            }
        `;
        document.head.appendChild(style);
        
        // Fix DOM manipulation issues
        this.zenDOMFixes();
    }
    
    zenDOMFixes() {
        // Override problematic DOM methods for Zen compatibility
        const originalAddEventListener = EventTarget.prototype.addEventListener;
        EventTarget.prototype.addEventListener = function(type, listener, options) {
            // Fix for Zen's event handling quirks
            if (typeof options === 'boolean') {
                options = { capture: options, passive: false };
            } else if (!options) {
                options = { passive: false };
            }
            
            return originalAddEventListener.call(this, type, listener, options);
        };
    }
    
    applyFirefoxFixes() {
        document.documentElement.classList.add('firefox-browser');
        
        const style = document.createElement('style');
        style.textContent = `
            /* Firefox-specific fixes */
            @-moz-document url-prefix() {
                .flex-container {
                    display: -moz-flex;
                    display: flex;
                }
                
                /* Fix for button styling */
                button::-moz-focus-inner {
                    border: 0;
                    padding: 0;
                }
                
                /* Fix for input styling */
                input[type="search"]::-moz-search-cancel-button {
                    -webkit-appearance: none;
                    appearance: none;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    applySafariFixes() {
        document.documentElement.classList.add('safari-browser');
        
        const style = document.createElement('style');
        style.textContent = `
            /* Safari-specific fixes */
            @supports (-webkit-appearance: none) {
                /* Fix for 100vh on mobile Safari */
                .full-height {
                    height: calc(var(--vh, 1vh) * 100);
                }
                
                /* Fix for date inputs */
                input[type="date"]::-webkit-calendar-picker-indicator {
                    opacity: 1;
                }
                
                /* Fix for transform3d performance */
                .animated {
                    -webkit-transform: translateZ(0);
                    transform: translateZ(0);
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    applyGeneralFixes() {
        const style = document.createElement('style');
        style.textContent = `
            /* General cross-browser fixes */
            *, *::before, *::after {
                box-sizing: border-box;
            }
            
            /* Consistent focus styles */
            :focus {
                outline: 2px solid var(--primary-color, #3b82f6);
                outline-offset: 2px;
            }
            
            .keyboard-nav :focus {
                outline: 2px solid var(--primary-color, #3b82f6);
            }
            
            .keyboard-nav button:focus,
            .keyboard-nav input:focus,
            .keyboard-nav select:focus,
            .keyboard-nav textarea:focus {
                outline: 2px solid var(--primary-color, #3b82f6);
                outline-offset: 2px;
            }
            
            /* Loading states */
            .loading {
                pointer-events: none;
                opacity: 0.6;
            }
            
            /* Smooth scrolling */
            html {
                scroll-behavior: smooth;
            }
            
            @media (prefers-reduced-motion) {
                html {
                    scroll-behavior: auto;
                }
                
                * {
                    animation-duration: 0s !important;
                    transition-duration: 0s !important;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Public methods for components to use
    isBrowser(name) {
        return this.browserInfo.name === name;
    }
    
    hasCapability(capability) {
        return this.capabilities[capability];
    }
    
    addCompatibilityFix(selector, styles) {
        const style = document.createElement('style');
        style.textContent = `${selector} { ${styles} }`;
        document.head.appendChild(style);
    }
    
    // State management fix for Zen browser
    createStateManager() {
        return new StateManager(this.browserInfo);
    }
}

class StateManager {
    constructor(browserInfo) {
        this.browserInfo = browserInfo;
        this.state = new Map();
        this.listeners = new Map();
        this.isZen = browserInfo.name === 'zen';
    }
    
    setState(key, value) {
        const oldValue = this.state.get(key);
        this.state.set(key, value);
        
        // Notify listeners
        const listeners = this.listeners.get(key) || [];
        listeners.forEach(listener => {
            try {
                listener(value, oldValue);
            } catch (error) {
                console.error('State listener error:', error);
            }
        });
        
        // Special handling for Zen browser
        if (this.isZen) {
            this.zenStateSync(key, value);
        }
    }
    
    getState(key) {
        return this.state.get(key);
    }
    
    subscribe(key, listener) {
        if (!this.listeners.has(key)) {
            this.listeners.set(key, []);
        }
        this.listeners.get(key).push(listener);
        
        // Return unsubscribe function
        return () => {
            const listeners = this.listeners.get(key) || [];
            const index = listeners.indexOf(listener);
            if (index > -1) {
                listeners.splice(index, 1);
            }
        };
    }
    
    zenStateSync(key, value) {
        // Force DOM update for Zen browser
        requestAnimationFrame(() => {
            const event = new CustomEvent('statechange', {
                detail: { key, value }
            });
            document.dispatchEvent(event);
        });
    }
}

// Initialize compatibility layer
const browserCompat = new BrowserCompatibility();

// Export for global use
window.BrowserCompatibility = BrowserCompatibility;
window.browserCompat = browserCompat;

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('Browser compatibility layer initialized');
    });
} else {
    console.log('Browser compatibility layer initialized');
}
