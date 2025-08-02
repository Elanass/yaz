/**
 * Surgify Core - Minimal & Efficient JavaScript
 * Decision Precision Engine Frontend Logic
 */

class SurgifyApp {
    constructor() {
        this.sidebar = null;
        this.overlay = null;
        this.searchInput = null;
        this.filterButtons = null;
        this.theme = localStorage.getItem('theme') || 'light';
        
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        this.initElements();
        this.initTheme();
        this.initEventListeners();
        this.initSearch();
        this.initCarousels();
        
        console.log('🚀 Surgify Decision Engine initialized');
    }

    initElements() {
        this.sidebar = document.getElementById('sidebar');
        this.overlay = document.getElementById('sidebar-overlay');
        this.searchInput = document.getElementById('global-search');
        this.filterButtons = document.querySelectorAll('.filter-btn');
    }

    initTheme() {
        // Apply saved theme
        document.documentElement.setAttribute('data-theme', this.theme);
        
        // Update theme icon
        const themeIcon = document.getElementById('theme-icon');
        if (themeIcon) {
            this.updateThemeIcon(themeIcon);
        }
    }

    initEventListeners() {
        // Menu toggle
        document.addEventListener('click', (e) => {
            if (e.target.closest('[data-action="toggle-menu"]')) {
                this.toggleSidebar();
            }
            
            if (e.target.closest('[data-action="close-menu"]')) {
                this.closeSidebar();
            }
        });

        // Theme toggle
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }

        // Filter buttons
        this.filterButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.setFilter(btn.dataset.filter);
            });
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Escape to close sidebar
            if (e.key === 'Escape') {
                this.closeSidebar();
            }
            
            // Ctrl/Cmd + K for search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.focusSearch();
            }
        });

        // Resize handler for responsive behavior
        window.addEventListener('resize', () => {
            if (window.innerWidth >= 1024) {
                this.closeSidebar();
            }
        });
    }

    initSearch() {
        if (!this.searchInput) return;

        let searchTimeout;
        this.searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.performSearch(e.target.value);
            }, 300);
        });

        // Search placeholder enhancement
        this.searchInput.placeholder = "Search patients, procedures, cases...";
    }

    initCarousels() {
        // Add smooth scrolling to carousels
        const carousels = document.querySelectorAll('.carousel');
        carousels.forEach(carousel => {
            carousel.style.scrollBehavior = 'smooth';
        });
    }

    toggleSidebar() {
        if (!this.sidebar || !this.overlay) return;

        const isOpen = this.sidebar.classList.contains('open');
        
        if (isOpen) {
            this.closeSidebar();
        } else {
            this.openSidebar();
        }
    }

    openSidebar() {
        if (!this.sidebar || !this.overlay) return;
        
        this.sidebar.classList.add('open');
        this.overlay.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    closeSidebar() {
        if (!this.sidebar || !this.overlay) return;
        
        this.sidebar.classList.remove('open');
        this.overlay.classList.remove('show');
        document.body.style.overflow = '';
    }

    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        
        // Apply theme
        document.documentElement.setAttribute('data-theme', this.theme);
        
        // Save theme
        localStorage.setItem('theme', this.theme);
        
        // Update icon
        const themeIcon = document.getElementById('theme-icon');
        if (themeIcon) {
            this.updateThemeIcon(themeIcon);
        }
        
        console.log(`🎨 Theme switched to ${this.theme}`);
    }

    updateThemeIcon(icon) {
        if (this.theme === 'dark') {
            icon.innerHTML = '<path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd"></path>';
        } else {
            icon.innerHTML = '<path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"></path>';
        }
    }

    setFilter(filter) {
        // Update active filter button
        this.filterButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === filter);
        });

        // Filter carousel items
        const carouselItems = document.querySelectorAll('.carousel-item');
        carouselItems.forEach(item => {
            const itemSystem = item.dataset.system;
            const shouldShow = filter === 'all' || itemSystem === filter;
            item.style.display = shouldShow ? 'block' : 'none';
        });

        console.log(`🔍 Filter applied: ${filter}`);
    }

    performSearch(query) {
        if (query.length < 2) {
            this.clearSearchResults();
            return;
        }

        // Simple search implementation
        console.log(`🔍 Searching for: ${query}`);
        
        // In a real implementation, this would make an API call
        // For now, we'll just filter visible content
        this.filterContent(query.toLowerCase());
    }

    filterContent(query) {
        const items = document.querySelectorAll('.carousel-item, .nav-link');
        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            const matches = text.includes(query);
            item.style.opacity = matches ? '1' : '0.3';
        });
    }

    clearSearchResults() {
        const items = document.querySelectorAll('.carousel-item, .nav-link');
        items.forEach(item => {
            item.style.opacity = '1';
        });
    }

    focusSearch() {
        if (this.searchInput) {
            this.searchInput.focus();
            this.searchInput.select();
        }
    }

    // Utility method for API calls
    async apiCall(endpoint, options = {}) {
        try {
            const response = await fetch(`/api/v1${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }

    // Module navigation
    navigateToModule(moduleName) {
        window.location.href = `/modules/${moduleName}`;
    }
}

// Initialize app when script loads
const surgifyApp = new SurgifyApp();

// Export for global access if needed
window.SurgifyApp = surgifyApp;
