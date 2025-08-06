// Surgify Application - Consolidated JavaScript
class SurgifyApp {
    constructor() {
        this.apiBase = '/api/v1';
        this.currentUser = null;
        this.searchTimeout = null;
        this.notifications = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupSearch();
        this.setupNavigation();
        this.setupPWA();
        this.setupTheme();
    }

    // Event listeners
    setupEventListeners() {
        document.addEventListener('click', (e) => this.handleGlobalClick(e));
        document.addEventListener('submit', (e) => this.handleFormSubmit(e));
        
        // Mobile menu toggle
        const menuToggle = document.getElementById('menu-toggle');
        const sidebar = document.getElementById('sidebar');
        if (menuToggle && sidebar) {
            menuToggle.addEventListener('click', () => {
                sidebar.classList.toggle('-translate-x-full');
            });
        }
    }

    // Search functionality
    setupSearch() {
        const searchInput = document.getElementById('global-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                clearTimeout(this.searchTimeout);
                this.searchTimeout = setTimeout(() => {
                    this.performSearch(e.target.value);
                }, 300);
            });
        }
    }

    async performSearch(query) {
        if (query.length < 2) return;
        
        try {
            const response = await this.fetch(`${this.apiBase}/search`, {
                method: 'POST',
                body: JSON.stringify({ query, limit: 10 })
            });
            this.displaySearchResults(response.results);
        } catch (error) {
            console.error('Search failed:', error);
        }
    }

    // Navigation
    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => this.handleNavigation(e));
        });
    }

    handleNavigation(e) {
        const target = e.target.closest('.nav-item');
        if (!target) return;
        
        // Remove active state from all nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Add active state to clicked item
        target.classList.add('active');
    }

    // PWA functionality
    setupPWA() {
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            this.showInstallPrompt();
        });

        const installBtn = document.getElementById('install-btn');
        if (installBtn) {
            installBtn.addEventListener('click', () => {
                if (deferredPrompt) {
                    deferredPrompt.prompt();
                    deferredPrompt.userChoice.then((choiceResult) => {
                        deferredPrompt = null;
                        this.hideInstallPrompt();
                    });
                }
            });
        }
    }

    showInstallPrompt() {
        const prompt = document.querySelector('.pwa-install-prompt');
        if (prompt) {
            prompt.classList.add('show');
        }
    }

    hideInstallPrompt() {
        const prompt = document.querySelector('.pwa-install-prompt');
        if (prompt) {
            prompt.classList.remove('show');
        }
    }

    // Theme management
    setupTheme() {
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
        
        // Load saved theme
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Update theme toggle icon
        const themeIcon = document.querySelector('#theme-toggle svg');
        if (themeIcon) {
            themeIcon.innerHTML = theme === 'light' 
                ? '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>'
                : '<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>';
        }
    }

    // Global click handler
    handleGlobalClick(e) {
        // Close dropdowns when clicking outside
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.classList.add('hidden');
            });
        }
        
        // Handle dropdown toggles
        if (e.target.matches('[data-dropdown-toggle]')) {
            const targetId = e.target.getAttribute('data-dropdown-toggle');
            const menu = document.getElementById(targetId);
            if (menu) {
                menu.classList.toggle('hidden');
            }
        }
    }

    // Form submission handler
    handleFormSubmit(e) {
        if (e.target.matches('[data-ajax-form]')) {
            e.preventDefault();
            this.submitFormAjax(e.target);
        }
    }

    async submitFormAjax(form) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        try {
            const response = await this.fetch(form.action, {
                method: form.method || 'POST',
                body: JSON.stringify(data)
            });
            
            this.showNotification('Form submitted successfully', 'success');
            form.reset();
        } catch (error) {
            this.showNotification('Form submission failed', 'error');
            console.error('Form submission error:', error);
        }
    }

    // Notification system
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type} slide-down`;
        notification.innerHTML = `
            <div class="flex items-center justify-between p-4 rounded-lg shadow-lg">
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-lg">&times;</button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    // Utility methods
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
    }

    $(selector) {
        return document.querySelector(selector);
    }

    $$(selector) {
        return document.querySelectorAll(selector);
    }

    setLoading(element, loading = true) {
        if (loading) {
            element.classList.add('component-loading');
        } else {
            element.classList.remove('component-loading');
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.surgifyApp = new SurgifyApp();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SurgifyApp;
}
