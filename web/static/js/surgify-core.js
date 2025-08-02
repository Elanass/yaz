/**
 * Surgify Core - Unified JavaScript Application
 * DRY and minimal approach with modular components
 */

class SurgifyCore {
    constructor() {
        this.modules = new Map();
        this.state = new Map();
        this.init();
    }

    init() {
        this.initTheme();
        this.initSidebar();
        this.initSearch();
        this.initCarousels();
        this.initAuth();
        console.log('🚀 Surgify Core initialized');
    }

    // Theme Management
    initTheme() {
        const themeToggle = document.getElementById('theme-toggle');
        const currentTheme = localStorage.getItem('theme') || 'light';
        
        document.documentElement.setAttribute('data-theme', currentTheme);
        
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                const newTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
            });
        }
    }

    // Sidebar Management
    initSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebar-overlay');
        const toggles = document.querySelectorAll('[data-action="toggle-menu"]');
        const closers = document.querySelectorAll('[data-action="close-menu"]');

        const openSidebar = () => {
            sidebar?.classList.remove('-translate-x-full');
            overlay?.classList.remove('hidden');
        };

        const closeSidebar = () => {
            sidebar?.classList.add('-translate-x-full');
            overlay?.classList.add('hidden');
        };

        toggles.forEach(toggle => toggle.addEventListener('click', openSidebar));
        closers.forEach(closer => closer.addEventListener('click', closeSidebar));
        overlay?.addEventListener('click', closeSidebar);
    }

    // Search with Filters
    initSearch() {
        const searchInput = document.getElementById('global-search');
        const filterButtons = document.querySelectorAll('.filter-btn');

        // Filter functionality
        filterButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                filterButtons.forEach(b => b.classList.remove('active', 'bg-blue-100', 'text-blue-600'));
                btn.classList.add('active', 'bg-blue-100', 'text-blue-600');
                
                const filter = btn.dataset.filter;
                this.applyFilter(filter);
            });
        });

        // Search functionality
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.performSearch(e.target.value);
                }, 300);
            });
        }
    }

    applyFilter(filter) {
        console.log(`Applying filter: ${filter}`);
        // Filter carousel content based on system type
        this.filterCarousels(filter);
    }

    filterCarousels(filter) {
        const carousels = document.querySelectorAll('[data-system]');
        carousels.forEach(carousel => {
            const system = carousel.dataset.system;
            if (filter === 'all' || system === filter) {
                carousel.style.display = 'block';
            } else {
                carousel.style.display = 'none';
            }
        });
    }

    performSearch(query) {
        if (query.length < 2) return;
        
        console.log(`Searching for: ${query}`);
        // Implement search logic here
        this.highlightSearchResults(query);
    }

    highlightSearchResults(query) {
        // Simple highlight implementation
        const cards = document.querySelectorAll('.carousel-card');
        cards.forEach(card => {
            const text = card.textContent.toLowerCase();
            if (text.includes(query.toLowerCase())) {
                card.style.border = '2px solid #3b82f6';
            } else {
                card.style.border = '';
            }
        });
    }

    // Carousel Management
    initCarousels() {
        const carousels = document.querySelectorAll('.overflow-x-auto');
        
        carousels.forEach(carousel => {
            let isDown = false;
            let startX;
            let scrollLeft;

            carousel.addEventListener('mousedown', (e) => {
                isDown = true;
                startX = e.pageX - carousel.offsetLeft;
                scrollLeft = carousel.scrollLeft;
            });

            carousel.addEventListener('mouseleave', () => {
                isDown = false;
            });

            carousel.addEventListener('mouseup', () => {
                isDown = false;
            });

            carousel.addEventListener('mousemove', (e) => {
                if (!isDown) return;
                e.preventDefault();
                const x = e.pageX - carousel.offsetLeft;
                const walk = (x - startX) * 2;
                carousel.scrollLeft = scrollLeft - walk;
            });
        });
    }

    // Authentication
    initAuth() {
        const loginBtn = document.getElementById('login-btn');
        const logoutBtn = document.getElementById('logout-btn');
        const userMenu = document.getElementById('user-menu-toggle');
        const userDropdown = document.getElementById('user-dropdown');

        // User menu toggle
        if (userMenu && userDropdown) {
            userMenu.addEventListener('click', () => {
                userDropdown.classList.toggle('hidden');
            });

            // Close dropdown when clicking outside
            document.addEventListener('click', (e) => {
                if (!userMenu.contains(e.target) && !userDropdown.contains(e.target)) {
                    userDropdown.classList.add('hidden');
                }
            });
        }

        // WebAuthn support (if available)
        if (window.PublicKeyCredential) {
            this.initWebAuthn();
        }
    }

    async initWebAuthn() {
        // WebAuthn implementation
        console.log('WebAuthn available');
    }

    // Utility Methods
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg z-50 ${type === 'error' ? 'bg-red-500' : type === 'success' ? 'bg-green-500' : 'bg-blue-500'} text-white`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // State Management
    setState(key, value) {
        this.state.set(key, value);
        this.notifyStateChange(key, value);
    }

    getState(key) {
        return this.state.get(key);
    }

    notifyStateChange(key, value) {
        const event = new CustomEvent('stateChange', {
            detail: { key, value }
        });
        document.dispatchEvent(event);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.surgify = new SurgifyCore();
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SurgifyCore;
}
