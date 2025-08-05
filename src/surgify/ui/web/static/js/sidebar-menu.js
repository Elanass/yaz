// Enhanced Sidebar Menu functionality
class SidebarManager {
    constructor() {
        this.isOpen = false;
        this.sidebar = null;
        this.overlay = null;
        this.hamburgerButton = null;
        this.init();
    }

    init() {
        this.createSidebar();
        this.createHamburgerButton();
        this.bindEvents();
    }

    createHamburgerButton() {
        // Create enhanced hamburger menu button
        this.hamburgerButton = document.createElement('button');
        this.hamburgerButton.className = 'hamburger-menu';
        this.hamburgerButton.setAttribute('aria-label', 'Toggle navigation menu');
        this.hamburgerButton.innerHTML = `
            <span class="hamburger-line"></span>
            <span class="hamburger-line"></span>
            <span class="hamburger-line"></span>
        `;
        
        // Insert into header if it exists
        const header = document.querySelector('.header-enhanced, .nav-container, header');
        if (header) {
            header.insertBefore(this.hamburgerButton, header.firstChild);
        } else {
            document.body.appendChild(this.hamburgerButton);
        }
    }

    createSidebar() {
        // Create enhanced sidebar HTML
        this.sidebar = document.createElement('div');
        this.sidebar.className = 'sidebar-enhanced';
        this.sidebar.innerHTML = `
            <div class="sidebar-header">
                <h2 class="sidebar-title">
                    <span class="brand-icon">🏥</span>
                    Yaz & Surgify
                </h2>
                <button class="sidebar-close" aria-label="Close menu">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
            
            <nav class="sidebar-nav">
                <div class="nav-section">
                    <h3 class="nav-section-title">Main Navigation</h3>
                    <a href="/" class="nav-item">
                        <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
                        </svg>
                        Dashboard
                    </a>
                    <a href="/surgify" class="nav-item">
                        <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path>
                        </svg>
                        Surgify Interface
                    </a>
                    <a href="/analytics" class="nav-item">
                        <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                        </svg>
                        Analytics Dashboard
                    </a>
                </div>
                
                <div class="nav-section">
                    <h3 class="nav-section-title">Workflow Islands</h3>
                    <a href="/ingestion" class="nav-item">
                        <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                        </svg>
                        Data Ingestion
                    </a>
                    <a href="/results" class="nav-item">
                        <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                        </svg>
                        Results & Analytics
                    </a>
                    <a href="/comparison" class="nav-item">
                        <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"></path>
                        </svg>
                        Cohort Comparison
                    </a>
                    <a href="/discussion" class="nav-item">
                        <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z"></path>
                        </svg>
                        Case Discussions
                    </a>
                    <a href="/recommendations" class="nav-item">
                        <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        Recommendations
                    </a>
                </div>
                
                <div class="nav-section">
                    <h3 class="nav-section-title">System & Support</h3>
                    <a href="/api/docs" class="nav-item">
                        <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                        API Documentation
                    </a>
                    <a href="/health" class="nav-item">
                        <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
                        </svg>
                        System Health
                    </a>
                </div>
            </nav>
        `;

        // Create overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'sidebar-overlay';
        
        // Add to DOM
        document.body.appendChild(this.sidebar);
        document.body.appendChild(this.overlay);
    }

    bindEvents() {
        // Hamburger button click
        if (this.hamburgerButton) {
            this.hamburgerButton.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleSidebar();
            });
        }

        // Menu toggle button (fallback)
        const menuToggle = document.querySelector('[data-action="toggle-menu"]');
        if (menuToggle) {
            menuToggle.addEventListener('click', () => this.toggleSidebar());
        }

        // Sidebar close button
        const closeButton = this.sidebar.querySelector('.sidebar-close');
        if (closeButton) {
            closeButton.addEventListener('click', () => this.closeSidebar());
        }

        // Overlay click to close
        this.overlay.addEventListener('click', () => this.closeSidebar());

        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeSidebar();
            }
        });

        // Close on navigation
        this.sidebar.addEventListener('click', (e) => {
            if (e.target.tagName === 'A') {
                this.closeSidebar();
            }
        });

        // Hover effects for navigation items
        const navItems = this.sidebar.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('mouseenter', (e) => {
                e.target.style.transform = 'translateX(4px)';
            });
            
            item.addEventListener('mouseleave', (e) => {
                if (!e.target.classList.contains('active')) {
                    e.target.style.transform = 'translateX(0)';
                }
            });
        });
    }

    toggleSidebar() {
        if (this.isOpen) {
            this.closeSidebar();
        } else {
            this.openSidebar();
        }
    }

    openSidebar() {
        this.isOpen = true;
        this.sidebar.classList.add('open');
        this.overlay.style.opacity = '1';
        this.overlay.style.visibility = 'visible';
        
        if (this.hamburgerButton) {
            this.hamburgerButton.classList.add('active');
        }
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        
        // Focus trap
        this.sidebar.setAttribute('tabindex', '-1');
        this.sidebar.focus();
    }

    closeSidebar() {
        this.isOpen = false;
        this.sidebar.classList.remove('open');
        this.overlay.style.opacity = '0';
        this.overlay.style.visibility = 'hidden';
        
        if (this.hamburgerButton) {
            this.hamburgerButton.classList.remove('active');
        }
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        // Remove focus
        this.sidebar.removeAttribute('tabindex');
    }

    // Method to highlight active nav item
    setActiveNavItem(path) {
        const navItems = this.sidebar.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('href') === path) {
                item.classList.add('active');
            }
        });
    }
}

    toggleSidebar() {
        if (this.isOpen) {
            this.closeSidebar();
        } else {
            this.openSidebar();
        }
    }

    openSidebar() {
        this.isOpen = true;
        this.sidebar.classList.add('open');
        this.overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Focus management
        this.sidebar.focus();
    }

    closeSidebar() {
        this.isOpen = false;
        this.sidebar.classList.remove('open');
        this.overlay.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// Initialize sidebar when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.sidebarManager = new SidebarManager();
});
