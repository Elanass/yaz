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
        this.setupDashboard();
        
        // Load initial data
        this.loadInitialData();
        
        // Make showSection globally accessible
        window.showSection = this.showSection.bind(this);
    }

    loadInitialData() {
        // Load cases by default (initial tab)
        setTimeout(() => {
            this.loadCases();
        }, 100);
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
        // Register service worker
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/sw.js')
                .then(registration => {
                    console.log('SW registered:', registration);
                })
                .catch(error => {
                    console.log('SW registration failed:', error);
                });
        }
        
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

    // Modern Theme management with animations and system preference
    setupTheme() {
        const themeToggle = document.getElementById('theme-toggle');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
        
        // Get saved theme or use system preference
        const savedTheme = localStorage.getItem('theme');
        const currentTheme = savedTheme || (prefersDark.matches ? 'dark' : 'light');
        
        // Apply theme with smooth transition
        this.setTheme(currentTheme, false);
        
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.toggleTheme();
                
                // Add click animation
                themeToggle.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    themeToggle.style.transform = 'scale(1)';
                }, 150);
            });
        }
        
        // Listen for system theme changes
        prefersDark.addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                this.setTheme(e.matches ? 'dark' : 'light', true);
            }
        });
    }

    toggleTheme() {
        const currentTheme = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme, true);
    }

    setTheme(theme, animate = false) {
        // Add smooth transition for theme change
        if (animate) {
            document.documentElement.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
            setTimeout(() => {
                document.documentElement.style.transition = '';
            }, 300);
        }
        
        // Remove existing theme classes
        document.documentElement.classList.remove('light', 'dark');
        
        // Add new theme class
        document.documentElement.classList.add(theme);
        
        // Save theme preference
        localStorage.setItem('theme', theme);
        
        // Update icons if Lucide is available
        if (typeof lucide !== 'undefined') {
            setTimeout(() => {
                lucide.createIcons();
            }, 100);
        }
        
        // Emit theme change event for other components
        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
    }
        localStorage.setItem('theme', theme);
        
        // Update theme toggle icons
        const sunIcon = document.getElementById('sun-icon');
        const moonIcon = document.getElementById('moon-icon');
        
        if (sunIcon && moonIcon) {
            if (theme === 'dark') {
                sunIcon.classList.add('hidden');
                moonIcon.classList.remove('hidden');
            } else {
                sunIcon.classList.remove('hidden');
                moonIcon.classList.add('hidden');
            }
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

    // Dashboard functionality
    setupDashboard() {
        if (document.body.classList.contains('page-dashboard')) {
            this.loadDashboardStats();
            // Auto-refresh every 30 seconds
            setInterval(() => this.loadDashboardStats(), 30000);
        }
    }

    async loadDashboardStats() {
        try {
            const stats = await this.fetch('/api/v1/dashboard/stats');
            
            // Update stat numbers
            const activeCases = this.$('#active-cases');
            const completedToday = this.$('#completed-today');
            
            if (activeCases) activeCases.textContent = stats.activeCases || 0;
            if (completedToday) completedToday.textContent = stats.completedToday || 0;
            
        } catch (error) {
            console.error('Failed to load dashboard stats:', error);
            this.showNotification('Failed to load dashboard data', 'error');
        }
    }

    // Data loading functions for UI sections
    async loadCases() {
        const casesList = document.getElementById('cases-list');
        if (!casesList) return;

        this.setLoading(casesList, true);
        
        try {
            const cases = await this.fetch('/api/v1/cases/');
            
            if (cases.length === 0) {
                casesList.innerHTML = `
                    <div class="text-center py-8 text-gray-500 dark:text-gray-400">
                        <p>No active cases found</p>
                        <button class="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors" 
                                onclick="surgifyApp.showAddCaseModal()">
                            Add New Case
                        </button>
                    </div>
                `;
                return;
            }

            casesList.innerHTML = cases.map(case_ => `
                <div class="case-card bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow cursor-pointer" 
                     onclick="surgifyApp.openCase('${case_.id}')">
                    <div class="flex justify-between items-start mb-2">
                        <h3 class="font-semibold text-gray-900 dark:text-white">${case_.patient_id || 'Unknown Patient'}</h3>
                        <span class="px-2 py-1 text-xs rounded-full ${this.getStatusColor(case_.status)}">
                            ${case_.status || 'Unknown'}
                        </span>
                    </div>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">${case_.procedure_type || 'No procedure specified'}</p>
                    <p class="text-xs text-gray-500 dark:text-gray-500">
                        Created: ${new Date(case_.created_at).toLocaleDateString()}
                    </p>
                </div>
            `).join('');
            
        } catch (error) {
            console.error('Failed to load cases:', error);
            casesList.innerHTML = `
                <div class="text-center py-8 text-red-500">
                    <p>Failed to load cases</p>
                    <button class="mt-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors" 
                            onclick="surgifyApp.loadCases()">
                        Retry
                    </button>
                </div>
            `;
        } finally {
            this.setLoading(casesList, false);
        }
    }

    async loadProposals() {
        const proposalsList = document.getElementById('proposals-list');
        if (!proposalsList) return;

        this.setLoading(proposalsList, true);
        
        try {
            const proposals = await this.fetch('/api/v1/proposals/');
            
            if (proposals.length === 0) {
                proposalsList.innerHTML = `
                    <div class="text-center py-8 text-gray-500 dark:text-gray-400">
                        <p>No surgical proposals found</p>
                        <button class="mt-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                            Create Proposal
                        </button>
                    </div>
                `;
                return;
            }

            proposalsList.innerHTML = proposals.map(proposal => `
                <div class="proposal-card bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow cursor-pointer">
                    <div class="flex justify-between items-start mb-2">
                        <h3 class="font-semibold text-gray-900 dark:text-white">${proposal.title || 'Untitled Proposal'}</h3>
                        <span class="px-2 py-1 text-xs rounded-full ${this.getStatusColor(proposal.status)}">
                            ${proposal.status || 'Draft'}
                        </span>
                    </div>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">${proposal.description || 'No description'}</p>
                    <p class="text-xs text-gray-500 dark:text-gray-500">
                        Submitted: ${new Date(proposal.created_at).toLocaleDateString()}
                    </p>
                </div>
            `).join('');
            
        } catch (error) {
            console.error('Failed to load proposals:', error);
            proposalsList.innerHTML = `
                <div class="text-center py-8 text-red-500">
                    <p>Failed to load proposals</p>
                    <button class="mt-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors" 
                            onclick="surgifyApp.loadProposals()">
                        Retry
                    </button>
                </div>
            `;
        } finally {
            this.setLoading(proposalsList, false);
        }
    }

    async loadCollaborations() {
        const collaborationsList = document.getElementById('collaborations-list');
        if (!collaborationsList) return;

        this.setLoading(collaborationsList, true);
        
        try {
            const collaborations = await this.fetch('/api/v1/collaboration/');
            
            if (collaborations.length === 0) {
                collaborationsList.innerHTML = `
                    <div class="text-center py-8 text-gray-500 dark:text-gray-400">
                        <p>No active collaborations</p>
                        <button class="mt-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
                            Start Collaboration
                        </button>
                    </div>
                `;
                return;
            }

            collaborationsList.innerHTML = collaborations.map(collab => `
                <div class="collaboration-card bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow cursor-pointer">
                    <div class="flex justify-between items-start mb-2">
                        <h3 class="font-semibold text-gray-900 dark:text-white">${collab.title || 'Collaboration'}</h3>
                        <span class="px-2 py-1 text-xs rounded-full bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
                            ${collab.participants_count || 0} members
                        </span>
                    </div>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">${collab.description || 'No description'}</p>
                    <p class="text-xs text-gray-500 dark:text-gray-500">
                        Last activity: ${new Date(collab.updated_at).toLocaleDateString()}
                    </p>
                </div>
            `).join('');
            
        } catch (error) {
            console.error('Failed to load collaborations:', error);
            collaborationsList.innerHTML = `
                <div class="text-center py-8 text-red-500">
                    <p>Failed to load collaborations</p>
                    <button class="mt-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors" 
                            onclick="surgifyApp.loadCollaborations()">
                        Retry
                    </button>
                </div>
            `;
        } finally {
            this.setLoading(collaborationsList, false);
        }
    }

    async loadStudies() {
        const studiesList = document.getElementById('studies-list');
        if (!studiesList) return;

        this.setLoading(studiesList, true);
        
        try {
            const studies = await this.fetch('/api/v1/research/studies/');
            
            if (studies.length === 0) {
                studiesList.innerHTML = `
                    <div class="text-center py-8 text-gray-500 dark:text-gray-400">
                        <p>No research studies found</p>
                        <button class="mt-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
                            Create Study
                        </button>
                    </div>
                `;
                return;
            }

            studiesList.innerHTML = studies.map(study => `
                <div class="study-card bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow cursor-pointer">
                    <div class="flex justify-between items-start mb-2">
                        <h3 class="font-semibold text-gray-900 dark:text-white">${study.title || 'Research Study'}</h3>
                        <span class="px-2 py-1 text-xs rounded-full ${this.getStatusColor(study.status)}">
                            ${study.status || 'Active'}
                        </span>
                    </div>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">${study.description || 'No description'}</p>
                    <div class="flex justify-between text-xs text-gray-500 dark:text-gray-500">
                        <span>Participants: ${study.participants_count || 0}</span>
                        <span>Progress: ${study.progress || 0}%</span>
                    </div>
                </div>
            `).join('');
            
        } catch (error) {
            console.error('Failed to load studies:', error);
            studiesList.innerHTML = `
                <div class="text-center py-8 text-red-500">
                    <p>Failed to load research studies</p>
                    <button class="mt-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors" 
                            onclick="surgifyApp.loadStudies()">
                        Retry
                    </button>
                </div>
            `;
        } finally {
            this.setLoading(studiesList, false);
        }
    }

    // Helper function for status colors
    getStatusColor(status) {
        const statusColors = {
            'active': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
            'completed': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
            'pending': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
            'cancelled': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
            'in_progress': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
            'draft': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
        };
        return statusColors[status?.toLowerCase()] || statusColors['draft'];
    }

    // Modern UI Section Management
    async showSection(sectionName) {
        // Add loading animation
        this.showLoadingOverlay();
        
        try {
            // Hide all sections with fade out
            document.querySelectorAll('.content-section').forEach(section => {
                section.classList.add('hidden');
                section.classList.remove('animate-fade-in');
            });
            
            // Update tab states with modern styling
            document.querySelectorAll('.tab-button').forEach(tab => {
                tab.classList.remove('active');
                tab.classList.remove('bg-blue-600', 'text-white', 'shadow-lg');
                tab.classList.add('text-slate-600', 'dark:text-slate-400', 'hover:bg-white/50', 'dark:hover:bg-slate-700/50');
            });
            
            // Show target section with fade in
            const targetSection = document.getElementById(`${sectionName}-section`);
            if (targetSection) {
                setTimeout(() => {
                    targetSection.classList.remove('hidden');
                    targetSection.classList.add('animate-fade-in');
                }, 150);
            }
            
            // Activate selected tab with modern styling
            const activeTab = document.querySelector(`[onclick="showSection('${sectionName}')"]`);
            if (activeTab) {
                activeTab.classList.add('active', 'bg-blue-600', 'text-white', 'shadow-lg');
                activeTab.classList.remove('text-slate-600', 'dark:text-slate-400', 'hover:bg-white/50', 'dark:hover:bg-slate-700/50');
            }
            
            // Load section data
            await this.loadSectionData(sectionName);
            
        } catch (error) {
            console.error(`Error showing section ${sectionName}:`, error);
            this.showNotification(`Error loading ${sectionName}`, 'error');
        } finally {
            this.hideLoadingOverlay();
        }
    }
    
    async loadSectionData(sectionName) {
        switch (sectionName) {
            case 'cases':
                await this.loadCases();
                break;
            case 'proposals':
                await this.loadProposals();
                break;
            case 'collaborations':
                await this.loadCollaborations();
                break;
            case 'studies':
                await this.loadStudies();
                break;
        }
    }
    
    async loadCases() {
        try {
            const response = await this.apiCall('/api/v1/cases/');
            const cases = await response.json();
            
            const container = document.getElementById('cases-list');
            if (!container) return;
            
            if (cases.length === 0) {
                container.innerHTML = this.getEmptyState('cases', 'No active cases found', 'Create your first case to get started');
                return;
            }
            
            container.innerHTML = cases.map(caseItem => this.renderCaseCard(caseItem)).join('');
            document.getElementById('cases-count').textContent = cases.length;
            document.getElementById('stats-active-cases').textContent = cases.length;
            
        } catch (error) {
            console.error('Error loading cases:', error);
            document.getElementById('cases-list').innerHTML = this.getErrorState('Failed to load cases');
        }
    }
    
    async loadProposals() {
        try {
            const response = await this.apiCall('/api/v1/proposals/');
            const proposals = await response.json();
            
            const container = document.getElementById('proposals-list');
            if (!container) return;
            
            if (proposals.length === 0) {
                container.innerHTML = this.getEmptyState('proposals', 'No proposals found', 'Create your first surgical proposal');
                return;
            }
            
            container.innerHTML = proposals.map(proposal => this.renderProposalCard(proposal)).join('');
            document.getElementById('proposals-count').textContent = proposals.length;
            
        } catch (error) {
            console.error('Error loading proposals:', error);
            document.getElementById('proposals-list').innerHTML = this.getErrorState('Failed to load proposals');
        }
    }
    
    async loadCollaborations() {
        try {
            const response = await this.apiCall('/api/v1/collaborations/');
            const collaborations = await response.json();
            
            const container = document.getElementById('collaborations-list');
            if (!container) return;
            
            if (collaborations.length === 0) {
                container.innerHTML = this.getEmptyState('collaborations', 'No active collaborations', 'Start collaborating with other professionals');
                return;
            }
            
            container.innerHTML = collaborations.map(collab => this.renderCollaborationCard(collab)).join('');
            document.getElementById('collaborations-count').textContent = collaborations.length;
            document.getElementById('stats-collaborations').textContent = collaborations.length;
            
        } catch (error) {
            console.error('Error loading collaborations:', error);
            document.getElementById('collaborations-list').innerHTML = this.getErrorState('Failed to load collaborations');
        }
    }
    
    async loadStudies() {
        try {
            const response = await this.apiCall('/api/v1/studies/');
            const studies = await response.json();
            
            const container = document.getElementById('studies-list');
            if (!container) return;
            
            if (studies.length === 0) {
                container.innerHTML = this.getEmptyState('studies', 'No research studies', 'Create your first research study');
                return;
            }
            
            container.innerHTML = studies.map(study => this.renderStudyCard(study)).join('');
            document.getElementById('studies-count').textContent = studies.length;
            
        } catch (error) {
            console.error('Error loading studies:', error);
            document.getElementById('studies-list').innerHTML = this.getErrorState('Failed to load studies');
        }
    }
    
    // Modern Card Renderers
    renderCaseCard(caseItem) {
        const statusColors = {
            'active': 'bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-200',
            'pending': 'bg-yellow-100 dark:bg-yellow-900/50 text-yellow-800 dark:text-yellow-200',
            'completed': 'bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-200',
            'cancelled': 'bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-200'
        };
        
        const status = caseItem.status || 'pending';
        const statusClass = statusColors[status] || statusColors['pending'];
        
        return `
            <div class="floating-card bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm rounded-2xl p-6 border border-white/20 dark:border-slate-700/50 group cursor-pointer">
                <div class="flex items-start justify-between mb-4">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
                            <i data-lucide="folder" class="h-5 w-5 text-white"></i>
                        </div>
                        <div>
                            <h3 class="font-semibold text-slate-900 dark:text-white">${caseItem.case_number || 'Case #' + (caseItem.id || 'Unknown')}</h3>
                            <p class="text-sm text-slate-500 dark:text-slate-400">${caseItem.patient_id || 'Patient ID not set'}</p>
                        </div>
                    </div>
                    <span class="px-3 py-1 rounded-full text-xs font-medium ${statusClass}">${status}</span>
                </div>
                
                <div class="space-y-3 mb-4">
                    <div class="flex items-center text-sm text-slate-600 dark:text-slate-400">
                        <i data-lucide="user" class="h-4 w-4 mr-2"></i>
                        <span>${caseItem.procedure_type || 'Procedure not specified'}</span>
                    </div>
                    <div class="flex items-center text-sm text-slate-600 dark:text-slate-400">
                        <i data-lucide="calendar" class="h-4 w-4 mr-2"></i>
                        <span>${caseItem.created_at ? new Date(caseItem.created_at).toLocaleDateString() : 'Date not set'}</span>
                    </div>
                    ${caseItem.diagnosis ? `
                    <div class="flex items-start text-sm text-slate-600 dark:text-slate-400">
                        <i data-lucide="clipboard" class="h-4 w-4 mr-2 mt-0.5"></i>
                        <span class="line-clamp-2">${caseItem.diagnosis}</span>
                    </div>
                    ` : ''}
                </div>
                
                <div class="flex items-center justify-between pt-4 border-t border-slate-200 dark:border-slate-700">
                    <div class="flex items-center space-x-2">
                        ${caseItem.priority ? `
                        <span class="px-2 py-1 text-xs font-medium rounded-md bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400">
                            ${caseItem.priority}
                        </span>
                        ` : ''}
                    </div>
                    <button class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors group-hover:bg-blue-50 dark:group-hover:bg-blue-900/50">
                        <i data-lucide="arrow-right" class="h-4 w-4 text-slate-400 group-hover:text-blue-600 dark:group-hover:text-blue-400"></i>
                    </button>
                </div>
            </div>
        `;
    }
    
    renderProposalCard(proposal) {
        return `
            <div class="floating-card bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm rounded-2xl p-6 border border-white/20 dark:border-slate-700/50 group cursor-pointer">
                <div class="flex items-start justify-between mb-4">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
                            <i data-lucide="file-plus" class="h-5 w-5 text-white"></i>
                        </div>
                        <div>
                            <h3 class="font-semibold text-slate-900 dark:text-white">${proposal.title || 'Untitled Proposal'}</h3>
                            <p class="text-sm text-slate-500 dark:text-slate-400">${proposal.type || 'Surgical Proposal'}</p>
                        </div>
                    </div>
                    <span class="px-3 py-1 rounded-full text-xs font-medium bg-purple-100 dark:bg-purple-900/50 text-purple-800 dark:text-purple-200">
                        ${proposal.status || 'Draft'}
                    </span>
                </div>
                
                <p class="text-sm text-slate-600 dark:text-slate-400 mb-4 line-clamp-3">
                    ${proposal.description || 'No description available'}
                </p>
                
                <div class="flex items-center justify-between pt-4 border-t border-slate-200 dark:border-slate-700">
                    <div class="flex items-center space-x-2">
                        <i data-lucide="clock" class="h-4 w-4 text-slate-400"></i>
                        <span class="text-xs text-slate-500 dark:text-slate-400">
                            ${proposal.created_at ? new Date(proposal.created_at).toLocaleDateString() : 'Date not set'}
                        </span>
                    </div>
                    <button class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                        <i data-lucide="arrow-right" class="h-4 w-4 text-slate-400"></i>
                    </button>
                </div>
            </div>
        `;
    }
    
    renderCollaborationCard(collab) {
        return `
            <div class="floating-card bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm rounded-2xl p-6 border border-white/20 dark:border-slate-700/50 group cursor-pointer">
                <div class="flex items-start justify-between mb-4">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 bg-gradient-to-r from-green-500 to-teal-600 rounded-xl flex items-center justify-center">
                            <i data-lucide="users" class="h-5 w-5 text-white"></i>
                        </div>
                        <div>
                            <h3 class="font-semibold text-slate-900 dark:text-white">${collab.name || 'Collaboration'}</h3>
                            <p class="text-sm text-slate-500 dark:text-slate-400">${collab.participants || '0'} participants</p>
                        </div>
                    </div>
                    <span class="px-3 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-200">
                        ${collab.status || 'Active'}
                    </span>
                </div>
                
                <p class="text-sm text-slate-600 dark:text-slate-400 mb-4 line-clamp-2">
                    ${collab.description || 'Collaborative research project'}
                </p>
                
                <div class="flex items-center justify-between pt-4 border-t border-slate-200 dark:border-slate-700">
                    <div class="flex -space-x-2">
                        ${Array.from({length: Math.min(collab.participants || 3, 4)}, (_, i) => `
                            <div class="w-6 h-6 bg-gradient-to-r from-blue-400 to-purple-500 rounded-full border-2 border-white dark:border-slate-800 flex items-center justify-center">
                                <span class="text-xs text-white">${String.fromCharCode(65 + i)}</span>
                            </div>
                        `).join('')}
                        ${(collab.participants || 3) > 4 ? `
                            <div class="w-6 h-6 bg-slate-200 dark:bg-slate-600 rounded-full border-2 border-white dark:border-slate-800 flex items-center justify-center">
                                <span class="text-xs text-slate-600 dark:text-slate-300">+${(collab.participants || 3) - 4}</span>
                            </div>
                        ` : ''}
                    </div>
                    <button class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                        <i data-lucide="arrow-right" class="h-4 w-4 text-slate-400"></i>
                    </button>
                </div>
            </div>
        `;
    }
    
    renderStudyCard(study) {
        return `
            <div class="floating-card bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm rounded-2xl p-6 border border-white/20 dark:border-slate-700/50 group cursor-pointer">
                <div class="flex items-start justify-between mb-4">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 bg-gradient-to-r from-orange-500 to-red-600 rounded-xl flex items-center justify-center">
                            <i data-lucide="microscope" class="h-5 w-5 text-white"></i>
                        </div>
                        <div>
                            <h3 class="font-semibold text-slate-900 dark:text-white">${study.title || 'Research Study'}</h3>
                            <p class="text-sm text-slate-500 dark:text-slate-400">${study.type || 'Clinical Study'}</p>
                        </div>
                    </div>
                    <span class="px-3 py-1 rounded-full text-xs font-medium bg-orange-100 dark:bg-orange-900/50 text-orange-800 dark:text-orange-200">
                        ${study.phase || 'Phase I'}
                    </span>
                </div>
                
                <p class="text-sm text-slate-600 dark:text-slate-400 mb-4 line-clamp-3">
                    ${study.description || 'Research study in progress'}
                </p>
                
                <div class="flex items-center justify-between pt-4 border-t border-slate-200 dark:border-slate-700">
                    <div class="flex items-center space-x-4">
                        <div class="flex items-center space-x-1">
                            <i data-lucide="users" class="h-4 w-4 text-slate-400"></i>
                            <span class="text-xs text-slate-500 dark:text-slate-400">${study.participants || '0'}</span>
                        </div>
                        <div class="flex items-center space-x-1">
                            <i data-lucide="calendar" class="h-4 w-4 text-slate-400"></i>
                            <span class="text-xs text-slate-500 dark:text-slate-400">
                                ${study.duration || '6 months'}
                            </span>
                        </div>
                    </div>
                    <button class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                        <i data-lucide="arrow-right" class="h-4 w-4 text-slate-400"></i>
                    </button>
                </div>
            </div>
        `;
    }
    
    // Modern UI States
    getEmptyState(type, title, description) {
        const icons = {
            'cases': 'folder-open',
            'proposals': 'file-plus',
            'collaborations': 'users',
            'studies': 'microscope'
        };
        
        return `
            <div class="col-span-full flex flex-col items-center justify-center py-16 text-center">
                <div class="w-16 h-16 bg-slate-100 dark:bg-slate-700 rounded-2xl flex items-center justify-center mb-4">
                    <i data-lucide="${icons[type] || 'folder'}" class="h-8 w-8 text-slate-400"></i>
                </div>
                <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-2">${title}</h3>
                <p class="text-slate-500 dark:text-slate-400 mb-6 max-w-sm">${description}</p>
                <button class="neo-button px-6 py-3 rounded-xl text-blue-600 dark:text-blue-400 font-medium hover:text-blue-700 dark:hover:text-blue-300 flex items-center space-x-2">
                    <i data-lucide="plus" class="h-4 w-4"></i>
                    <span>Create ${type.slice(0, -1)}</span>
                </button>
            </div>
        `;
    }
    
    getErrorState(message) {
        return `
            <div class="col-span-full flex flex-col items-center justify-center py-16 text-center">
                <div class="w-16 h-16 bg-red-100 dark:bg-red-900/50 rounded-2xl flex items-center justify-center mb-4">
                    <i data-lucide="alert-circle" class="h-8 w-8 text-red-500"></i>
                </div>
                <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-2">Error Loading Data</h3>
                <p class="text-slate-500 dark:text-slate-400 mb-6">${message}</p>
                <button onclick="location.reload()" class="neo-button px-6 py-3 rounded-xl text-blue-600 dark:text-blue-400 font-medium hover:text-blue-700 dark:hover:text-blue-300 flex items-center space-x-2">
                    <i data-lucide="refresh-cw" class="h-4 w-4"></i>
                    <span>Try Again</span>
                </button>
            </div>
        `;
    }
    
    // Loading States
    showLoadingOverlay() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.remove('hidden');
        }
    }
    
    hideLoadingOverlay() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
    }
    
    // Modern API Helper
    async apiCall(url, options = {}) {
        try {
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
            
            return response;
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }

    // Initialize with data loading
    async initializeData() {
        try {
            // Load initial section (cases)
            await this.showSection('cases');
            
            // Load stats
            await this.loadStats();
            
        } catch (error) {
            console.error('Error initializing data:', error);
            this.showNotification('Failed to load initial data', 'error');
        }
    }
    
    async loadStats() {
        try {
            // You can implement actual stats loading here
            // For now, using mock data
            const stats = {
                activeCases: 24,
                pendingReviews: 7,
                collaborations: 12,
                successRate: '94.5%'
            };
            
            document.getElementById('stats-active-cases').textContent = stats.activeCases;
            document.getElementById('stats-pending-reviews').textContent = stats.pendingReviews;
            document.getElementById('stats-collaborations').textContent = stats.collaborations;
            document.getElementById('stats-success-rate').textContent = stats.successRate;
            
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.surgifyApp = new SurgifyApp();
    
    // Initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});

// Global function for tab switching (called from HTML onclick)
function showSection(sectionName) {
    if (window.surgifyApp) {
        window.surgifyApp.showSection(sectionName);
    }
}

// Global function for theme toggle (backup)
function toggleTheme() {
    if (window.surgifyApp) {
        window.surgifyApp.toggleTheme();
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SurgifyApp;
}
