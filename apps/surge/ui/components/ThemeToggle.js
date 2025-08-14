/**
 * ThemeToggle Component
 * A reusable theme toggle component with dark/light mode support and htmx integration
 */

class ThemeToggle {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            theme: options.theme || this.getStoredTheme() || 'light',
            showLabel: options.showLabel !== false,
            size: options.size || 'medium', // small, medium, large
            style: options.style || 'switch', // switch, button, icon
            position: options.position || 'inline', // inline, fixed-top-right, fixed-bottom-right
            animated: options.animated !== false,
            autoDetect: options.autoDetect === true,
            onChange: options.onChange || null,
            htmxEndpoint: options.htmxEndpoint || null,
            className: options.className || '',
            labels: {
                light: options.labels?.light || 'Light',
                dark: options.labels?.dark || 'Dark',
                auto: options.labels?.auto || 'Auto'
            },
            ...options
        };
        
        this.systemTheme = 'light';
        this.init();
    }

    init() {
        // Detect system theme preference
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            this.systemTheme = mediaQuery.matches ? 'dark' : 'light';
            
            // Listen for system theme changes
            mediaQuery.addEventListener('change', (e) => {
                this.systemTheme = e.matches ? 'dark' : 'light';
                if (this.options.theme === 'auto') {
                    this.applyTheme();
                }
            });
        }

        // Apply initial theme
        this.applyTheme();
    }

    render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container with id "${this.containerId}" not found`);
            return;
        }

        const html = `
            <div class="theme-toggle ${this.options.className} ${this.getPositionClasses()}" data-component="theme-toggle">
                ${this.renderToggle()}
            </div>
        `;

        container.innerHTML = html;
        this.attachEventListeners();
    }

    renderToggle() {
        switch (this.options.style) {
            case 'switch':
                return this.renderSwitchStyle();
            case 'button':
                return this.renderButtonStyle();
            case 'icon':
                return this.renderIconStyle();
            default:
                return this.renderSwitchStyle();
        }
    }

    renderSwitchStyle() {
        const sizeClasses = {
            small: 'w-10 h-5',
            medium: 'w-12 h-6',
            large: 'w-14 h-7'
        };

        const toggleSizeClasses = {
            small: 'w-4 h-4',
            medium: 'w-5 h-5',
            large: 'w-6 h-6'
        };

        const isDark = this.getCurrentTheme() === 'dark';

        return `
            <div class="flex items-center space-x-3">
                ${this.options.showLabel ? `
                    <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
                        ${this.options.labels.light} / ${this.options.labels.dark}
                    </span>
                ` : ''}
                <button 
                    class="theme-toggle-switch relative ${sizeClasses[this.options.size]} ${isDark ? 'bg-blue-600' : 'bg-gray-300'} rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors duration-200"
                    role="switch"
                    aria-checked="${isDark}"
                    ${this.options.htmxEndpoint ? `hx-post="${this.options.htmxEndpoint}" hx-vals='{"theme": "${isDark ? 'light' : 'dark'}"}'` : ''}
                >
                    <span class="sr-only">Toggle theme</span>
                    <span 
                        class="toggle-indicator absolute ${toggleSizeClasses[this.options.size]} bg-white rounded-full shadow transform transition-transform duration-200 ${isDark ? this.getTogglePositionRight() : 'translate-x-0.5'}"
                    >
                        ${this.renderToggleIcon()}
                    </span>
                </button>
            </div>
        `;
    }

    renderButtonStyle() {
        const sizeClasses = {
            small: 'px-3 py-1 text-sm',
            medium: 'px-4 py-2 text-sm',
            large: 'px-6 py-3 text-base'
        };

        const currentTheme = this.getCurrentTheme();
        const themes = this.options.autoDetect ? ['light', 'dark', 'auto'] : ['light', 'dark'];

        return `
            <div class="theme-toggle-buttons flex items-center space-x-2">
                ${this.options.showLabel ? `
                    <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Theme:</span>
                ` : ''}
                <div class="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
                    ${themes.map(theme => `
                        <button 
                            class="theme-option ${sizeClasses[this.options.size]} font-medium rounded-md transition-colors duration-200 ${
                                theme === this.options.theme 
                                    ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow' 
                                    : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
                            }"
                            data-theme="${theme}"
                            ${this.options.htmxEndpoint ? `hx-post="${this.options.htmxEndpoint}" hx-vals='{"theme": "${theme}"}'` : ''}
                        >
                            <div class="flex items-center space-x-2">
                                ${this.getThemeIcon(theme)}
                                <span>${this.options.labels[theme]}</span>
                            </div>
                        </button>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderIconStyle() {
        const sizeClasses = {
            small: 'w-8 h-8',
            medium: 'w-10 h-10',
            large: 'w-12 h-12'
        };

        const currentTheme = this.getCurrentTheme();

        return `
            <button 
                class="theme-toggle-icon ${sizeClasses[this.options.size]} flex items-center justify-center text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors duration-200"
                title="Toggle theme"
                ${this.options.htmxEndpoint ? `hx-post="${this.options.htmxEndpoint}" hx-vals='{"theme": "${currentTheme === 'dark' ? 'light' : 'dark'}"}'` : ''}
            >
                ${this.getThemeIcon(currentTheme === 'dark' ? 'light' : 'dark')}
            </button>
        `;
    }

    getPositionClasses() {
        switch (this.options.position) {
            case 'fixed-top-right':
                return 'fixed top-4 right-4 z-50';
            case 'fixed-bottom-right':
                return 'fixed bottom-4 right-4 z-50';
            default:
                return '';
        }
    }

    getTogglePositionRight() {
        const positions = {
            small: 'translate-x-5',
            medium: 'translate-x-6',
            large: 'translate-x-7'
        };
        return positions[this.options.size];
    }

    renderToggleIcon() {
        const currentTheme = this.getCurrentTheme();
        const iconSize = this.options.size === 'small' ? 'w-3 h-3' : this.options.size === 'large' ? 'w-4 h-4' : 'w-3.5 h-3.5';

        return `
            <div class="flex items-center justify-center w-full h-full">
                ${currentTheme === 'dark' ? `
                    <svg class="${iconSize} text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd" />
                    </svg>
                ` : `
                    <svg class="${iconSize} text-gray-700" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                    </svg>
                `}
            </div>
        `;
    }

    getThemeIcon(theme) {
        const iconClass = this.options.size === 'small' ? 'w-4 h-4' : this.options.size === 'large' ? 'w-6 h-6' : 'w-5 h-5';

        switch (theme) {
            case 'light':
                return `<svg class="${iconClass}" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd" />
                </svg>`;
            case 'dark':
                return `<svg class="${iconClass}" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                </svg>`;
            case 'auto':
                return `<svg class="${iconClass}" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
                </svg>`;
            default:
                return '';
        }
    }

    attachEventListeners() {
        const container = document.getElementById(this.containerId);

        // Switch style listeners
        const switchBtn = container.querySelector('.theme-toggle-switch');
        if (switchBtn) {
            switchBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleTheme();
            });
        }

        // Button style listeners
        const themeOptions = container.querySelectorAll('.theme-option');
        themeOptions.forEach(option => {
            option.addEventListener('click', (e) => {
                e.preventDefault();
                const theme = e.currentTarget.dataset.theme;
                this.setTheme(theme);
            });
        });

        // Icon style listeners
        const iconBtn = container.querySelector('.theme-toggle-icon');
        if (iconBtn) {
            iconBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleTheme();
            });
        }
    }

    // Theme management methods
    setTheme(theme) {
        if (['light', 'dark', 'auto'].includes(theme)) {
            this.options.theme = theme;
            this.storeTheme(theme);
            this.applyTheme();
            this.render();

            // Call custom callback
            if (this.options.onChange) {
                this.options.onChange(theme, this.getCurrentTheme());
            }

            // Dispatch custom event
            const container = document.getElementById(this.containerId);
            if (container) {
                container.dispatchEvent(new CustomEvent('themeChanged', {
                    detail: { 
                        selectedTheme: theme, 
                        actualTheme: this.getCurrentTheme() 
                    },
                    bubbles: true
                }));
            }
        }
    }

    toggleTheme() {
        const currentTheme = this.options.theme;
        let newTheme;

        if (this.options.autoDetect) {
            // Cycle through light -> dark -> auto
            switch (currentTheme) {
                case 'light':
                    newTheme = 'dark';
                    break;
                case 'dark':
                    newTheme = 'auto';
                    break;
                case 'auto':
                    newTheme = 'light';
                    break;
                default:
                    newTheme = 'dark';
            }
        } else {
            // Simple toggle between light and dark
            newTheme = currentTheme === 'light' ? 'dark' : 'light';
        }

        this.setTheme(newTheme);
    }

    getCurrentTheme() {
        if (this.options.theme === 'auto') {
            return this.systemTheme;
        }
        return this.options.theme;
    }

    applyTheme() {
        const actualTheme = this.getCurrentTheme();
        const html = document.documentElement;

        if (actualTheme === 'dark') {
            html.classList.add('dark');
        } else {
            html.classList.remove('dark');
        }

        // Update meta theme-color for mobile browsers
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', actualTheme === 'dark' ? '#1f2937' : '#ffffff');
        }
    }

    storeTheme(theme) {
        try {
            localStorage.setItem('theme-preference', theme);
        } catch (e) {
            // localStorage not available
        }
    }

    getStoredTheme() {
        try {
            return localStorage.getItem('theme-preference');
        } catch (e) {
            return null;
        }
    }

    // Public methods
    getTheme() {
        return this.options.theme;
    }

    getActiveTheme() {
        return this.getCurrentTheme();
    }

    // Cleanup
    destroy() {
        const container = document.getElementById(this.containerId);
        if (container) {
            container.innerHTML = '';
        }
    }
}

// Auto-initialization for theme toggles with data attributes
document.addEventListener('DOMContentLoaded', function() {
    const autoInitElements = document.querySelectorAll('[data-theme-toggle="auto"]');
    autoInitElements.forEach(element => {
        const options = {
            theme: element.dataset.theme || 'light',
            style: element.dataset.style || 'switch',
            size: element.dataset.size || 'medium',
            showLabel: element.dataset.showLabel !== 'false',
            autoDetect: element.dataset.autoDetect === 'true'
        };
        
        const toggle = new ThemeToggle(element.id, options);
        toggle.render();
    });
});

// HTMX integration
document.addEventListener('htmx:afterRequest', function(event) {
    const themeToggles = document.querySelectorAll('[data-component="theme-toggle"]');
    themeToggles.forEach(toggle => {
        // Handle theme updates from server
        const response = event.detail.xhr.response;
        if (response) {
            try {
                const data = JSON.parse(response);
                if (data.theme) {
                    // Update theme based on server response
                    const toggleInstance = toggle._themeToggleInstance;
                    if (toggleInstance) {
                        toggleInstance.setTheme(data.theme);
                    }
                }
            } catch (e) {
                // Response is not JSON, ignore
            }
        }
    });
});

// CSS for animations and styling
const themeToggleStyles = `
.theme-toggle {
    user-select: none;
}

.theme-toggle-switch {
    transition: background-color 0.2s ease-in-out;
}

.theme-toggle-switch:focus {
    outline: none;
}

.toggle-indicator {
    transition: transform 0.2s ease-in-out;
}

.theme-option {
    transition: all 0.2s ease-in-out;
}

.theme-toggle-icon {
    transition: all 0.2s ease-in-out;
}

.dark .theme-toggle-icon {
    background-color: #374151;
    border-color: #4b5563;
}

.dark .theme-toggle-icon:hover {
    background-color: #4b5563;
}

@media (prefers-reduced-motion: reduce) {
    .theme-toggle * {
        transition: none !important;
    }
}
`;

// Inject styles if not already present
if (!document.getElementById('theme-toggle-styles')) {
    const style = document.createElement('style');
    style.id = 'theme-toggle-styles';
    style.textContent = themeToggleStyles;
    document.head.appendChild(style);
}

// Export for module usage
window.ThemeToggle = ThemeToggle;
