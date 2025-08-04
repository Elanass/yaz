// Theme Switcher - Dark/Light Mode Toggle
class ThemeSwitcher {
    constructor() {
        this.init();
    }

    init() {
        // Get saved theme or default to light
        this.currentTheme = localStorage.getItem('surgify-theme') || 'light';
        this.applyTheme(this.currentTheme);
        
        // Set up toggle button
        this.setupToggleButton();
        
        // Listen for system theme changes
        this.listenForSystemThemeChanges();
    }

    setupToggleButton() {
        const toggleButton = document.getElementById('theme-toggle');
        const lightIcon = document.getElementById('theme-icon-light');
        const darkIcon = document.getElementById('theme-icon-dark');

        if (!toggleButton) return;

        // Update icons based on current theme
        this.updateIcons();

        // Add click handler
        toggleButton.addEventListener('click', () => {
            this.toggleTheme();
        });
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(this.currentTheme);
        localStorage.setItem('surgify-theme', this.currentTheme);
        
        // Add visual feedback
        this.showThemeChangeNotification();
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.updateIcons();
        
        // Update meta theme-color for mobile browsers
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.content = theme === 'dark' ? '#1a202c' : '#ffffff';
        }
    }

    updateIcons() {
        const lightIcon = document.getElementById('theme-icon-light');
        const darkIcon = document.getElementById('theme-icon-dark');

        if (!lightIcon || !darkIcon) return;

        if (this.currentTheme === 'light') {
            lightIcon.classList.add('hidden');
            darkIcon.classList.remove('hidden');
        } else {
            lightIcon.classList.remove('hidden');
            darkIcon.classList.add('hidden');
        }
    }

    listenForSystemThemeChanges() {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addListener((e) => {
            // Only auto-switch if user hasn't manually set a preference
            if (!localStorage.getItem('surgify-theme')) {
                this.currentTheme = e.matches ? 'dark' : 'light';
                this.applyTheme(this.currentTheme);
            }
        });
    }

    showThemeChangeNotification() {
        const notification = document.createElement('div');
        notification.className = 'notification show';
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <svg style="width: 1rem; height: 1rem;" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                </svg>
                <span>Theme changed to ${this.currentTheme} mode</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Initialize theme switcher when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.themeSwitcher = new ThemeSwitcher();
});

// Export for use in other modules
window.ThemeSwitcher = ThemeSwitcher;
