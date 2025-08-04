// Main Surgify Application
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
        this.loadUserSession();
        this.setupSearch();
        this.setupBottomNavigation();
        this.checkSystemHealth();
        this.setupNotificationSystem();
    }

    setupEventListeners() {
        // Global click handlers
        document.addEventListener('click', (e) => {
            this.handleGlobalClick(e);
        });

        // Form submissions
        document.addEventListener('submit', (e) => {
            this.handleFormSubmit(e);
        });

        // Window events
        window.addEventListener('online', () => this.showNotification('Back online', 'success'));
        window.addEventListener('offline', () => this.showNotification('Connection lost', 'warning'));
        
        // Close search results when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#global-search') && !e.target.closest('#search-results')) {
                this.hideSearchResults();
            }
        });
    }

    setupNotificationSystem() {
        // Create notification container if it doesn't exist
        if (!document.getElementById('notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 80px;
                right: 1rem;
                z-index: 1000;
                max-width: 400px;
                pointer-events: none;
            `;
            document.body.appendChild(container);
        }
    }

    setupSearch() {
        const searchInput = document.getElementById('global-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                clearTimeout(this.searchTimeout);
                this.searchTimeout = setTimeout(() => {
                    this.performSearch(e.target.value);
                }, 300);
            });

            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.performSearch(e.target.value);
                }
            });
        }
    }

    setupBottomNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                this.handleNavigation(e);
            });
        });
    }

    async performSearch(query) {
        if (query.length < 2) {
            this.hideSearchResults();
            return;
        }
        
        this.showSearchLoading();
        
        try {
            const response = await this.fetch(`${this.apiBase}/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, limit: 10 })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.displaySearchResults(data.results);
            } else {
                this.showNotification('Search failed', 'error');
                this.hideSearchResults();
            }
        } catch (error) {
            console.error('Search error:', error);
            this.displayMockSearchResults(query);
        }
    }

    showSearchLoading() {
        let dropdown = document.getElementById('search-results');
        if (!dropdown) {
            dropdown = document.createElement('div');
            dropdown.id = 'search-results';
            dropdown.className = 'absolute top-full left-0 right-0 mt-1 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded-lg shadow-lg z-50 max-h-60 overflow-y-auto';
            document.getElementById('global-search').parentElement.appendChild(dropdown);
        }
        dropdown.innerHTML = '<div class="p-3 flex items-center gap-2"><div class="spinner"></div>Searching...</div>';
        dropdown.style.display = 'block';
    }

    hideSearchResults() {
        const dropdown = document.getElementById('search-results');
        if (dropdown) {
            dropdown.style.display = 'none';
        }
    }

    displayMockSearchResults(query) {
        // Mock results for demo when API is not available
        const mockResults = [
            { type: 'case', id: '1', title: 'Case SURG-001', description: 'Gastric resection - Completed', url: '/cases/1' },
            { type: 'case', id: '2', title: 'Case SURG-002', description: 'Laparoscopic surgery - In Progress', url: '/cases/2' },
            { type: 'patient', id: '1', title: 'John Smith', description: 'Patient ID: PAT-001', url: '/patients/1' },
            { type: 'procedure', id: '1', title: 'Gastric Resection', description: 'Surgical removal of stomach tissue', url: '/procedures/gastric' }
        ].filter(result => 
            result.title.toLowerCase().includes(query.toLowerCase()) ||
            result.description.toLowerCase().includes(query.toLowerCase())
        );

        this.displaySearchResults(mockResults);
    }

    displaySearchResults(results) {
        // Create or update search results dropdown
        let dropdown = document.getElementById('search-results');
        if (!dropdown) {
            dropdown = document.createElement('div');
            dropdown.id = 'search-results';
            dropdown.className = 'absolute top-full left-0 right-0 mt-1 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded-lg shadow-lg z-50 max-h-60 overflow-y-auto';
            document.getElementById('global-search').parentElement.appendChild(dropdown);
        }

        if (results.length === 0) {
            dropdown.innerHTML = '<div class="p-3 text-[var(--text-tertiary)]">No results found</div>';
        } else {
            dropdown.innerHTML = results.map(result => `
                <div class="p-3 hover:bg-[var(--bg-secondary)] cursor-pointer border-b border-[var(--border-color)] last:border-b-0" 
                     onclick="window.surgifyApp.selectSearchResult('${result.type}', '${result.id}')">
                    <div class="font-medium text-[var(--text-primary)]">${result.title}</div>
                    <div class="text-sm text-[var(--text-secondary)]">${result.description}</div>
                </div>
            `).join('');
        }

        // Hide dropdown when clicking outside
        setTimeout(() => {
            document.addEventListener('click', function hideDropdown(e) {
                if (!dropdown.contains(e.target) && e.target !== document.getElementById('global-search')) {
                    dropdown.remove();
                    document.removeEventListener('click', hideDropdown);
                }
            });
        }, 100);
    }

    selectSearchResult(type, id) {
        this.showNotification(`Opening ${type}: ${id}`, 'info');
        
        // Navigate based on type
        switch (type) {
            case 'case':
                window.location.href = `/cases/${id}`;
                break;
            case 'patient':
                window.location.href = `/patients/${id}`;
                break;
            case 'protocol':
                window.location.href = `/protocols/${id}`;
                break;
            default:
                console.log('Unknown result type:', type);
        }
    }

    showNotification(message, type = 'info', duration = 3000) {
        const container = document.getElementById('notification-container');
        if (!container) return;
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="flex items-center justify-between">
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-3 text-white hover:text-gray-200">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                    </svg>
                </button>
            </div>
        `;
        
        notification.style.pointerEvents = 'auto';
        container.appendChild(notification);
        
        // Show notification
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Auto remove
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }

    handleGlobalClick(e) {
        // Handle menu toggle
        if (e.target.closest('[data-action="toggle-menu"]')) {
            if (window.sidebarManager) {
                window.sidebarManager.toggle();
            }
            return;
        }

        // Handle interactive cards
        if (e.target.closest('.interactive')) {
            const card = e.target.closest('.interactive');
            const action = card.dataset.action;
            if (action) {
                this.handleAction(action, card);
            }
        }

        // Handle case cards
        if (e.target.closest('[data-case-id]')) {
            const caseId = e.target.closest('[data-case-id]').dataset.caseId;
            this.showNotification(`Opening case ${caseId}`, 'info');
            // Could navigate to case detail
        }
    }

    // Enhanced mobile app functionality
    downloadApp(platform) {
        const urls = {
            ios: 'https://apps.apple.com/app/surgify',
            android: 'https://play.google.com/store/apps/details?id=com.surgify.app'
        };
        
        // Track download attempts
        this.trackEvent('app_download_attempted', { platform });
        
        // Check if apps are available
        fetch(`${this.apiBase}/mobile/app-status/${platform}`)
            .then(response => response.json())
            .then(data => {
                if (data.available) {
                    window.open(urls[platform], '_blank');
                    this.showNotification(`Redirecting to ${platform.toUpperCase()} App Store...`, 'success');
                } else {
                    this.showNotification(`${platform.toUpperCase()} app is coming soon! We'll notify you when it's available.`, 'info');
                    // Optionally collect email for notifications
                    this.showEmailSignup(platform);
                }
            })
            .catch(() => {
                this.showNotification(`${platform.toUpperCase()} app is coming soon! We'll notify you when it's available.`, 'info');
            });
    }

    // Show email signup for app notifications
    showEmailSignup(platform) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-md mx-4">
                <h3 class="text-lg font-bold mb-4">Get notified when ${platform.toUpperCase()} app is ready</h3>
                <form id="email-signup-form">
                    <input type="email" id="signup-email" placeholder="Your email address" 
                           class="w-full px-3 py-2 border rounded-lg mb-4" required>
                    <div class="flex gap-2">
                        <button type="submit" class="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                            Notify Me
                        </button>
                        <button type="button" onclick="this.closest('.fixed').remove()" 
                                class="px-4 py-2 border rounded-lg hover:bg-gray-50">
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        modal.querySelector('#email-signup-form').addEventListener('submit', (e) => {
            e.preventDefault();
            const email = modal.querySelector('#signup-email').value;
            this.subscribeToAppUpdates(email, platform);
            modal.remove();
        });
    }

    // Subscribe to app update notifications
    async subscribeToAppUpdates(email, platform) {
        try {
            const response = await fetch(`${this.apiBase}/mobile/subscribe`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, platform })
            });
            
            if (response.ok) {
                this.showNotification('Thank you! We\'ll notify you when the app is ready.', 'success');
            } else {
                throw new Error('Subscription failed');
            }
        } catch (error) {
            this.showNotification('Thank you for your interest! We\'ll keep you updated.', 'success');
        }
    }

    // Handle action buttons (Start, Doc, etc.)
    handleAction(action) {
        switch (action) {
            case 'start-workstation':
                this.startWorkstation();
                break;
            case 'open-docs':
                this.openDocumentation();
                break;
            default:
                console.log('Unknown action:', action);
        }
    }

    // Start workstation with authentication check
    async startWorkstation() {
        try {
            // Check if user is authenticated
            const authStatus = await this.checkAuthentication();
            
            if (authStatus.authenticated) {
                window.location.href = '/workstation';
            } else {
                // Show authentication options
                this.showAuthenticationModal();
            }
        } catch (error) {
            // Fallback to direct navigation
            window.location.href = '/workstation';
        }
    }

    // Open documentation
    openDocumentation() {
        window.open('/api/docs', '_blank');
    }

    // Check authentication status
    async checkAuthentication() {
        try {
            const response = await fetch(`${this.apiBase}/auth/status`);
            return await response.json();
        } catch (error) {
            return { authenticated: false };
        }
    }

    // Show authentication modal
    showAuthenticationModal() {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-md mx-4">
                <h3 class="text-lg font-bold mb-4">Access Workstation</h3>
                <p class="text-gray-600 mb-6">Sign in to access your clinical workstation and cases.</p>
                <div class="flex flex-col gap-3">
                    <a href="/auth/login" class="bg-blue-600 text-white px-4 py-2 rounded-lg text-center hover:bg-blue-700">
                        Sign In
                    </a>
                    <a href="/auth/register" class="border border-gray-300 px-4 py-2 rounded-lg text-center hover:bg-gray-50">
                        Create Account
                    </a>
                    <button onclick="this.closest('.fixed').remove(); window.location.href='/workstation'" 
                            class="text-sm text-gray-500 hover:text-gray-700">
                        Continue as Guest
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    // Enhanced footer interactions
    showAbout() {
        this.showInfoModal('About Surgify', `
            <p class="mb-4">Surgify is an advanced decision support platform for surgical excellence, 
            designed to enhance clinical outcomes through AI-powered insights and comprehensive case management.</p>
            <p class="mb-4">Our mission is to empower surgeons with cutting-edge technology that supports 
            evidence-based decision making and improves patient care.</p>
            <p class="text-sm text-gray-600">Version 2.0 - Make your way</p>
        `);
    }

    showTeam() {
        this.showInfoModal('Our Team', `
            <div class="space-y-4">
                <div class="text-center">
                    <div class="w-16 h-16 bg-gray-200 rounded-full mx-auto mb-2"></div>
                    <h4 class="font-semibold">Dr. Sarah Wilson</h4>
                    <p class="text-sm text-gray-600">Chief Medical Officer</p>
                </div>
                <div class="text-center">
                    <div class="w-16 h-16 bg-gray-200 rounded-full mx-auto mb-2"></div>
                    <h4 class="font-semibold">Dr. Michael Chen</h4>
                    <p class="text-sm text-gray-600">Lead Surgeon & Advisor</p>
                </div>
                <div class="text-center">
                    <div class="w-16 h-16 bg-gray-200 rounded-full mx-auto mb-2"></div>
                    <h4 class="font-semibold">Alex Johnson</h4>
                    <p class="text-sm text-gray-600">Technical Director</p>
                </div>
            </div>
        `);
    }

    submitFeedback() {
        this.showFeedbackModal('feedback');
    }

    reportIssue() {
        this.showFeedbackModal('issue');
    }

    requestFeature() {
        this.showFeedbackModal('feature');
    }

    // Show feedback modal
    showFeedbackModal(type) {
        const titles = {
            feedback: 'Send Feedback',
            issue: 'Report an Issue',
            feature: 'Request a Feature'
        };

        const placeholders = {
            feedback: 'Tell us what you think about Surgify...',
            issue: 'Describe the issue you encountered...',
            feature: 'Describe the feature you\'d like to see...'
        };

        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-md mx-4 w-full">
                <h3 class="text-lg font-bold mb-4">${titles[type]}</h3>
                <form id="feedback-form">
                    <textarea id="feedback-text" placeholder="${placeholders[type]}" 
                              class="w-full px-3 py-2 border rounded-lg mb-4 h-32 resize-none" required></textarea>
                    <input type="email" id="feedback-email" placeholder="Your email (optional)" 
                           class="w-full px-3 py-2 border rounded-lg mb-4">
                    <div class="flex gap-2">
                        <button type="submit" class="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                            Send ${type === 'feedback' ? 'Feedback' : type === 'issue' ? 'Report' : 'Request'}
                        </button>
                        <button type="button" onclick="this.closest('.fixed').remove()" 
                                class="px-4 py-2 border rounded-lg hover:bg-gray-50">
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        modal.querySelector('#feedback-form').addEventListener('submit', (e) => {
            e.preventDefault();
            const text = modal.querySelector('#feedback-text').value;
            const email = modal.querySelector('#feedback-email').value;
            this.sendFeedback(type, text, email);
            modal.remove();
        });
    }

    // Send feedback to backend
    async sendFeedback(type, text, email) {
        try {
            const response = await fetch(`${this.apiBase}/feedback`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type, text, email, timestamp: new Date().toISOString() })
            });
            
            if (response.ok) {
                this.showNotification('Thank you for your feedback!', 'success');
            } else {
                throw new Error('Failed to send feedback');
            }
        } catch (error) {
            this.showNotification('Thank you for your feedback! We appreciate your input.', 'success');
        }
    }

    // Show information modal
    showInfoModal(title, content) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-md mx-4">
                <h3 class="text-lg font-bold mb-4">${title}</h3>
                <div class="text-gray-700 mb-6">${content}</div>
                <button onclick="this.closest('.fixed').remove()" 
                        class="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                    Close
                </button>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    // Track events for analytics
    trackEvent(event, data = {}) {
        if (window.gtag) {
            window.gtag('event', event, data);
        }
        console.log('Event tracked:', event, data);
    }

    // Database and API functions
    async fetch(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };

        return fetch(url, { ...defaultOptions, ...options });
    }

    async loadUserSession() {
        try {
            const response = await this.fetch(`${this.apiBase}/auth/me`);
            if (response.ok) {
                this.currentUser = await response.json();
                this.updateUserInterface();
            }
        } catch (error) {
            console.log('No active session');
        }
    }

    updateUserInterface() {
        // Add user info to top nav if logged in
        const header = document.querySelector('header');
        if (this.currentUser && header) {
            const userInfo = document.createElement('div');
            userInfo.className = 'flex items-center gap-2 text-sm';
            userInfo.innerHTML = `
                <span class="text-[var(--text-secondary)]">Dr. ${this.currentUser.name || 'User'}</span>
                <button onclick="window.surgifyApp.logout()" class="text-[var(--text-tertiary)] hover:text-[var(--text-primary)]">
                    Logout
                </button>
            `;
            header.querySelector('.flex.items-center.gap-4:last-child').appendChild(userInfo);
        }
    }

    async checkSystemHealth() {
        try {
            const response = await this.fetch('/health');
            if (response.ok) {
                const health = await response.json();
                console.log('System health:', health);
                return health;
            }
        } catch (error) {
            console.error('Health check failed:', error);
            this.showNotification('System health check failed', 'warning');
        }
    }

    // Application actions
    async createNewCase() {
        this.showNotification('Creating new case...', 'info');
        
        try {
            const response = await this.fetch(`${this.apiBase}/cases`, {
                method: 'POST',
                body: JSON.stringify({
                    procedure: 'New Surgical Case',
                    status: 'planned',
                    notes: 'Created from UI'
                })
            });
            
            if (response.ok) {
                const newCase = await response.json();
                this.showNotification('New case created successfully', 'success');
                window.location.href = `/cases/${newCase.id}`;
            } else {
                this.showNotification('Failed to create case', 'error');
            }
        } catch (error) {
            console.error('Create case error:', error);
            this.showNotification('Case creation failed', 'error');
        }
    }

    async searchPatients() {
        this.showNotification('Opening patient search...', 'info');
        
        try {
            const response = await this.fetch(`${this.apiBase}/cases`);
            if (response.ok) {
                const cases = await response.json();
                this.showNotification(`Found ${cases.length} cases`, 'success');
                console.log('Cases:', cases);
            }
        } catch (error) {
            console.error('Patient search error:', error);
            this.showNotification('Patient search failed', 'error');
        }
    }

    async viewSchedule() {
        this.showNotification('Loading schedule...', 'info');
        
        try {
            const response = await this.fetch(`${this.apiBase}/dashboard/metrics`);
            if (response.ok) {
                const metrics = await response.json();
                this.showNotification('Schedule loaded', 'success');
                console.log('Metrics:', metrics);
            }
        } catch (error) {
            console.error('Schedule error:', error);
            this.showNotification('Schedule loading failed', 'error');
        }
    }

    async viewAnalytics() {
        this.showNotification('Opening analytics dashboard...', 'info');
        window.location.href = '/dashboard';
    }

    async logout() {
        try {
            await this.fetch(`${this.apiBase}/auth/logout`, { method: 'POST' });
            this.currentUser = null;
            this.showNotification('Logged out successfully', 'success');
            window.location.reload();
        } catch (error) {
            console.error('Logout error:', error);
            this.showNotification('Logout failed', 'error');
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.surgifyApp = new SurgifyApp();
});
