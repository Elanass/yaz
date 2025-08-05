/**
 * Sidepanel Menu Functionality
 * Handles opening, closing, and navigation for the sidepanel menu
 */

class SidepanelManager {
    constructor() {
        this.sidepanel = null;
        this.overlay = null;
        this.toggleButton = null;
        this.closeButton = null;
        this.isOpen = false;
        
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
        // Get elements
        this.sidepanel = document.getElementById('sidepanel');
        this.overlay = document.getElementById('sidepanel-overlay');
        this.toggleButton = document.getElementById('sidepanel-toggle');
        this.closeButton = document.getElementById('sidepanel-close');
        
        if (!this.sidepanel) {
            console.warn('Sidepanel element not found');
            return;
        }
        
        this.bindEvents();
        this.highlightActiveMenuItem();
        this.handleResponsiveDisplay();
    }
    
    bindEvents() {
        // Toggle button
        if (this.toggleButton) {
            this.toggleButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.open();
            });
        }
        
        // Close button
        if (this.closeButton) {
            this.closeButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.close();
            });
        }
        
        // Overlay click
        if (this.overlay) {
            this.overlay.addEventListener('click', () => {
                this.close();
            });
        }
        
        // Keyboard events
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
        
        // Menu item clicks (close on mobile)
        const menuItems = this.sidepanel.querySelectorAll('nav a');
        menuItems.forEach(item => {
            item.addEventListener('click', () => {
                if (window.innerWidth < 1024) {
                    setTimeout(() => this.close(), 100);
                }
            });
        });
        
        // Handle window resize
        window.addEventListener('resize', () => {
            this.handleResponsiveDisplay();
        });
    }
    
    open() {
        if (!this.sidepanel || this.isOpen) return;
        
        this.sidepanel.classList.remove('-translate-x-full');
        this.sidepanel.classList.add('translate-x-0');
        
        if (this.overlay) {
            this.overlay.classList.remove('hidden');
        }
        
        document.body.style.overflow = 'hidden';
        this.isOpen = true;
        
        // Focus management for accessibility
        const firstFocusable = this.sidepanel.querySelector('button, a');
        if (firstFocusable) {
            firstFocusable.focus();
        }
        
        this.sidepanel.setAttribute('aria-hidden', 'false');
    }
    
    close() {
        if (!this.sidepanel || !this.isOpen) return;
        
        this.sidepanel.classList.add('-translate-x-full');
        this.sidepanel.classList.remove('translate-x-0');
        
        if (this.overlay) {
            this.overlay.classList.add('hidden');
        }
        
        document.body.style.overflow = 'auto';
        this.isOpen = false;
        
        // Return focus to toggle button
        if (this.toggleButton) {
            this.toggleButton.focus();
        }
        
        this.sidepanel.setAttribute('aria-hidden', 'true');
    }
    
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
    
    highlightActiveMenuItem() {
        if (!this.sidepanel) return;
        
        const currentPath = window.location.pathname;
        const menuItems = this.sidepanel.querySelectorAll('nav a');
        
        menuItems.forEach(item => {
            const href = item.getAttribute('href');
            
            // Remove existing active classes
            item.classList.remove('bg-blue-50', 'text-blue-600', 'border-r-2', 'border-blue-600');
            
            // Add active class to current page
            if (href === currentPath || (currentPath === '/' && href === '/dashboard')) {
                item.classList.add('bg-blue-50', 'text-blue-600');
            }
        });
    }
    
    handleResponsiveDisplay() {
        // Auto-close on desktop if open
        if (window.innerWidth >= 1024 && this.isOpen) {
            this.close();
        }
    }
}

// Initialize sidepanel manager
const sidepanelManager = new SidepanelManager();

// Export for potential external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SidepanelManager;
} else if (typeof window !== 'undefined') {
    window.SidepanelManager = SidepanelManager;
    window.sidepanelManager = sidepanelManager;
}
