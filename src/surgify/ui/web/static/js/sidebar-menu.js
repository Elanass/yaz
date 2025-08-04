// Sidebar Menu functionality
class SidebarManager {
    constructor() {
        this.isOpen = false;
        this.sidebar = null;
        this.overlay = null;
        this.init();
    }

    init() {
        this.createSidebar();
        this.bindEvents();
    }

    createSidebar() {
        // Create sidebar HTML
        this.sidebar = document.createElement('div');
        this.sidebar.className = 'sidebar';
        this.sidebar.innerHTML = `
            <div class="p-4 border-b border-[var(--border-color)]">
                <h2 class="text-lg font-bold text-[var(--text-primary)]">Surgify Menu</h2>
            </div>
            <nav class="p-4">
                <ul class="space-y-2">
                    <li><a href="/" class="sidebar-link">🏠 Home</a></li>
                    <li><a href="/surgify" class="sidebar-link">⚕️ Surgify Interface</a></li>
                    <li><a href="/dashboard" class="sidebar-link">📊 Analytics Dashboard</a></li>
                    <li><a href="/api/docs" class="sidebar-link">📖 API Documentation</a></li>
                    <li><a href="/health" class="sidebar-link">❤️ System Health</a></li>
                </ul>
                
                <div class="mt-8 p-4 bg-[var(--bg-secondary)] rounded-lg">
                    <h3 class="font-semibold text-[var(--text-primary)] mb-2">Quick Actions</h3>
                    <div class="space-y-2">
                        <button class="w-full text-left sidebar-link" onclick="window.surgifyApp.createNewCase()">
                            ➕ New Case
                        </button>
                        <button class="w-full text-left sidebar-link" onclick="window.surgifyApp.searchPatients()">
                            🔍 Search Patients
                        </button>
                        <button class="w-full text-left sidebar-link" onclick="window.surgifyApp.viewSchedule()">
                            📅 View Schedule
                        </button>
                    </div>
                </div>
            </nav>
        `;

        // Create overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'sidebar-overlay';
        
        // Add to DOM
        document.body.appendChild(this.sidebar);
        document.body.appendChild(this.overlay);
        
        // Add sidebar styles
        const style = document.createElement('style');
        style.textContent = `
            .sidebar-link {
                display: block;
                padding: 0.5rem 0.75rem;
                color: var(--text-secondary);
                text-decoration: none;
                border-radius: 0.375rem;
                transition: all 0.2s ease;
            }
            .sidebar-link:hover {
                background-color: var(--bg-tertiary);
                color: var(--text-primary);
            }
        `;
        document.head.appendChild(style);
    }

    bindEvents() {
        // Menu toggle button
        const menuToggle = document.querySelector('[data-action="toggle-menu"]');
        if (menuToggle) {
            menuToggle.addEventListener('click', () => this.toggleSidebar());
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
