// Surgify Interactive UI Components
class SurgifyUI {
    constructor() {
        this.initSidebar();
        this.initAuth();
        this.initAnimations();
    }

    // Sidebar Management
    initSidebar() {
        const sidebar = document.getElementById('sidebar');
        const sidebarToggle = document.getElementById('sidebarToggle');
        const sidebarClose = document.getElementById('sidebarClose');
        const sidebarOverlay = document.getElementById('sidebarOverlay');

        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }
        
        if (sidebarClose) {
            sidebarClose.addEventListener('click', () => this.closeSidebar());
        }
        
        if (sidebarOverlay) {
            sidebarOverlay.addEventListener('click', () => this.closeSidebar());
        }

        // Close sidebar on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeSidebar();
                this.closeAuth();
            }
        });
    }

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebarOverlay');
        
        if (sidebar && overlay) {
            const isOpen = !sidebar.classList.contains('-translate-x-full');
            
            if (isOpen) {
                this.closeSidebar();
            } else {
                this.openSidebar();
            }
        }
    }

    openSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebarOverlay');
        
        if (sidebar && overlay) {
            sidebar.classList.remove('-translate-x-full');
            overlay.classList.remove('opacity-0', 'invisible');
            document.body.style.overflow = 'hidden';
        }
    }

    closeSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebarOverlay');
        
        if (sidebar && overlay) {
            sidebar.classList.add('-translate-x-full');
            overlay.classList.add('opacity-0', 'invisible');
            document.body.style.overflow = '';
        }
    }

    // Auth Modal Management
    initAuth() {
        const authToggle = document.getElementById('authToggle');
        const authModal = document.getElementById('authModal');
        const authModalClose = document.getElementById('authModalClose');
        const loginTab = document.getElementById('loginTab');
        const registerTab = document.getElementById('registerTab');
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');

        if (authToggle) {
            authToggle.addEventListener('click', () => this.openAuth());
        }

        if (authModalClose) {
            authModalClose.addEventListener('click', () => this.closeAuth());
        }

        if (authModal) {
            authModal.addEventListener('click', (e) => {
                if (e.target === authModal) {
                    this.closeAuth();
                }
            });
        }

        // Tab switching
        if (loginTab && registerTab) {
            loginTab.addEventListener('click', () => this.switchAuthTab('login'));
            registerTab.addEventListener('click', () => this.switchAuthTab('register'));
        }

        // Form submissions
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegister(e));
        }
    }

    openAuth() {
        const authModal = document.getElementById('authModal');
        
        if (authModal) {
            authModal.classList.remove('opacity-0', 'invisible');
            authModal.querySelector('.bg-white').classList.remove('scale-95');
            authModal.querySelector('.bg-white').classList.add('scale-100');
            document.body.style.overflow = 'hidden';
        }
    }

    closeAuth() {
        const authModal = document.getElementById('authModal');
        
        if (authModal) {
            authModal.classList.add('opacity-0', 'invisible');
            authModal.querySelector('.bg-white').classList.add('scale-95');
            authModal.querySelector('.bg-white').classList.remove('scale-100');
            document.body.style.overflow = '';
        }
    }

    switchAuthTab(tab) {
        const loginTab = document.getElementById('loginTab');
        const registerTab = document.getElementById('registerTab');
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');

        if (tab === 'login') {
            loginTab.classList.add('bg-white', 'text-blue-600', 'shadow-sm');
            loginTab.classList.remove('text-gray-600');
            registerTab.classList.remove('bg-white', 'text-blue-600', 'shadow-sm');
            registerTab.classList.add('text-gray-600');
            
            loginForm.classList.remove('hidden');
            registerForm.classList.add('hidden');
        } else {
            registerTab.classList.add('bg-white', 'text-blue-600', 'shadow-sm');
            registerTab.classList.remove('text-gray-600');
            loginTab.classList.remove('bg-white', 'text-blue-600', 'shadow-sm');
            loginTab.classList.add('text-gray-600');
            
            registerForm.classList.remove('hidden');
            loginForm.classList.add('hidden');
        }
    }

    handleLogin(e) {
        e.preventDefault();
        // Add login logic here
        this.showNotification('Login successful!', 'success');
        this.closeAuth();
    }

    handleRegister(e) {
        e.preventDefault();
        // Add registration logic here
        this.showNotification('Account created successfully!', 'success');
        this.closeAuth();
    }

    // Animations and UI Enhancements
    initAnimations() {
        // Add smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            });
        });

        // Add loading states to buttons
        document.querySelectorAll('button[type="submit"]').forEach(button => {
            button.addEventListener('click', function() {
                if (!this.disabled) {
                    this.classList.add('opacity-75');
                    setTimeout(() => {
                        this.classList.remove('opacity-75');
                    }, 1000);
                }
            });
        });

        // Add hover effects to cards
        document.querySelectorAll('.group').forEach(element => {
            element.addEventListener('mouseenter', function() {
                this.classList.add('transform', 'scale-105');
            });
            
            element.addEventListener('mouseleave', function() {
                this.classList.remove('transform', 'scale-105');
            });
        });
    }

    // Notification System
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 transform translate-x-full transition-transform duration-300 ${
            type === 'success' ? 'bg-green-500 text-white' : 
            type === 'error' ? 'bg-red-500 text-white' : 
            'bg-blue-500 text-white'
        }`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);
        
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    // Surgery State Management
    updateSurgeryState(state) {
        const stateElement = document.querySelector('[data-surgery-state]');
        if (stateElement) {
            stateElement.textContent = state;
            stateElement.className = `text-xs ${
                state === 'Ready' ? 'text-green-600' :
                state === 'In Progress' ? 'text-yellow-600' :
                state === 'Complete' ? 'text-blue-600' :
                'text-gray-600'
            }`;
        }
    }
}

// Initialize Surgify UI when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.surgifyUI = new SurgifyUI();
    
    // Add some demo functionality
    setTimeout(() => {
        if (window.surgifyUI) {
            window.surgifyUI.showNotification('Surgify platform loaded successfully!', 'success');
        }
    }, 1000);
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SurgifyUI;
}
