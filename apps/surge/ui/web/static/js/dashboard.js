/**
 * SURGE Dashboard - Modern Medical AI Platform
 * High-performance, accessible dashboard with real-time updates
 */

class SurgeDashboard {
  constructor() {
    this.isInitialized = false;
    this.searchTimeout = null;
    this.notificationCount = 3;
    this.theme = localStorage.getItem('surge-theme') || 'light';
    
    // Performance monitoring
    this.performanceMetrics = {
      loadStart: performance.now(),
      interactions: 0,
      errors: 0
    };
    
    this.init();
  }

  /**
   * Initialize dashboard components
   */
  init() {
    if (this.isInitialized) return;
    
    try {
      // Set initial theme
      this.applyTheme(this.theme);
      
      // Setup event listeners
      this.setupEventListeners();
      
      // Initialize components
      this.initializeSearch();
      this.initializeNotifications();
      this.initializeMetrics();
      this.initializeRealTimeUpdates();
      
      // Load initial data
      this.loadDashboardData();
      
      this.isInitialized = true;
      this.trackPerformance('dashboard_initialized');
      
      console.log('✅ SURGE Dashboard initialized successfully');
    } catch (error) {
      this.handleError('Dashboard initialization failed', error);
    }
  }

  /**
   * Setup all event listeners
   */
  setupEventListeners() {
    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
      themeToggle.addEventListener('click', () => this.toggleTheme());
    }

    // Global search
    const searchInput = document.getElementById('global-search');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
      searchInput.addEventListener('keydown', (e) => this.handleSearchKeydown(e));
    }

    // User menu
    const userMenuBtn = document.getElementById('user-menu-btn');
    if (userMenuBtn) {
      userMenuBtn.addEventListener('click', () => this.toggleUserMenu());
    }

    // Notifications
    const notificationsBtn = document.getElementById('notifications-btn');
    if (notificationsBtn) {
      notificationsBtn.addEventListener('click', () => this.toggleNotifications());
    }

    // Quick actions
    const quickActionBtns = document.querySelectorAll('.quick-action-btn');
    quickActionBtns.forEach(btn => {
      btn.addEventListener('click', (e) => this.handleQuickAction(e.target.closest('.quick-action-btn')));
    });

    // Hero actions
    const newCaseBtn = document.getElementById('new-case-btn');
    const quickSearchBtn = document.getElementById('quick-search-btn');
    
    if (newCaseBtn) {
      newCaseBtn.addEventListener('click', () => this.openNewCaseModal());
    }
    
    if (quickSearchBtn) {
      quickSearchBtn.addEventListener('click', () => this.focusGlobalSearch());
    }

    // Refresh buttons
    const refreshInsights = document.getElementById('refresh-insights');
    if (refreshInsights) {
      refreshInsights.addEventListener('click', () => this.refreshAIInsights());
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));

    // Click outside to close dropdowns
    document.addEventListener('click', (e) => this.handleOutsideClick(e));

    // Performance monitoring
    window.addEventListener('load', () => this.trackPerformance('page_loaded'));
    
    // Error handling
    window.addEventListener('error', (e) => this.handleError('JavaScript error', e.error));
    window.addEventListener('unhandledrejection', (e) => this.handleError('Unhandled promise rejection', e.reason));
  }

  /**
   * Theme management
   */
  toggleTheme() {
    const newTheme = this.theme === 'light' ? 'dark' : 'light';
    this.applyTheme(newTheme);
    this.trackInteraction('theme_toggle', { theme: newTheme });
  }

  applyTheme(theme) {
    this.theme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('surge-theme', theme);
    
    // Update theme toggle icons
    const lightIcon = document.querySelector('.theme-icon-light');
    const darkIcon = document.querySelector('.theme-icon-dark');
    
    if (lightIcon && darkIcon) {
      if (theme === 'dark') {
        lightIcon.classList.add('hidden');
        darkIcon.classList.remove('hidden');
      } else {
        lightIcon.classList.remove('hidden');
        darkIcon.classList.add('hidden');
      }
    }
  }

  /**
   * Search functionality
   */
  initializeSearch() {
    // Setup search suggestions
    this.searchSuggestions = [
      { type: 'patient', label: 'John Doe', id: 'P001' },
      { type: 'case', label: 'Gastric Surgery - C123', id: 'C123' },
      { type: 'report', label: 'Monthly Analytics Report', id: 'R456' }
    ];
  }

  handleSearch(query) {
    clearTimeout(this.searchTimeout);
    
    if (query.length < 2) {
      this.hideSearchSuggestions();
      return;
    }

    this.searchTimeout = setTimeout(() => {
      this.performSearch(query);
    }, 300);
  }

  performSearch(query) {
    // Filter suggestions based on query
    const filtered = this.searchSuggestions.filter(item => 
      item.label.toLowerCase().includes(query.toLowerCase())
    );
    
    this.showSearchSuggestions(filtered);
    this.trackInteraction('search', { query: query.length > 20 ? query.substring(0, 20) + '...' : query });
  }

  showSearchSuggestions(suggestions) {
    // Implementation for showing search dropdown
    console.log('Search suggestions:', suggestions);
  }

  hideSearchSuggestions() {
    // Implementation for hiding search dropdown
  }

  handleSearchKeydown(e) {
    if (e.key === 'Escape') {
      e.target.blur();
      this.hideSearchSuggestions();
    } else if (e.key === 'Enter') {
      this.executeSearch(e.target.value);
    }
  }

  executeSearch(query) {
    if (query.trim()) {
      window.location.href = `/search?q=${encodeURIComponent(query)}`;
    }
  }

  focusGlobalSearch() {
    const searchInput = document.getElementById('global-search');
    if (searchInput) {
      searchInput.focus();
      searchInput.select();
    }
  }

  /**
   * Notifications
   */
  initializeNotifications() {
    this.notifications = [
      { id: 1, type: 'info', title: 'Surgery scheduled', message: 'John Doe - 2:30 PM today', time: '5 min ago' },
      { id: 2, type: 'warning', title: 'Review required', message: 'Case C123 needs approval', time: '15 min ago' },
      { id: 3, type: 'success', title: 'Analysis complete', message: 'MRI scan results ready', time: '30 min ago' }
    ];
    
    this.updateNotificationBadge();
  }

  toggleNotifications() {
    // Implementation for notification dropdown
    console.log('Toggle notifications');
    this.trackInteraction('notifications_toggle');
  }

  updateNotificationBadge() {
    const badge = document.querySelector('.notification-badge');
    if (badge) {
      badge.textContent = this.notificationCount;
      badge.style.display = this.notificationCount > 0 ? 'block' : 'none';
    }
  }

  /**
   * Metrics and real-time updates
   */
  initializeMetrics() {
    this.metricsData = {
      activeCases: 124,
      todaysSurgeries: 18,
      pendingReviews: 7,
      successRate: 98.7
    };
    
    this.updateMetrics();
  }

  updateMetrics() {
    // Update metric values with animation
    this.animateMetricValue('.metric-card--primary .metric-value', this.metricsData.activeCases);
    this.animateMetricValue('.metric-card--success .metric-value', this.metricsData.todaysSurgeries);
    this.animateMetricValue('.metric-card--warning .metric-value', this.metricsData.pendingReviews);
    this.animateMetricValue('.metric-card--info .metric-value', this.metricsData.successRate + '%');
  }

  animateMetricValue(selector, targetValue) {
    const element = document.querySelector(selector);
    if (!element) return;
    
    const currentValue = parseInt(element.textContent) || 0;
    const target = typeof targetValue === 'string' ? parseFloat(targetValue) : targetValue;
    
    let start = null;
    const duration = 1000;
    
    const animate = (timestamp) => {
      if (!start) start = timestamp;
      const progress = Math.min((timestamp - start) / duration, 1);
      
      const current = currentValue + (target - currentValue) * this.easeOutCubic(progress);
      element.textContent = typeof targetValue === 'string' && targetValue.includes('%') 
        ? current.toFixed(1) + '%' 
        : Math.round(current);
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    
    requestAnimationFrame(animate);
  }

  easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  initializeRealTimeUpdates() {
    // Setup WebSocket connection for real-time updates
    this.setupWebSocket();
    
    // Fallback polling for updates
    this.setupPolling();
  }

  setupWebSocket() {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/dashboard`;
      
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log('✅ WebSocket connected');
        this.trackPerformance('websocket_connected');
      };
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleRealTimeUpdate(data);
        } catch (error) {
          this.handleError('WebSocket message parsing failed', error);
        }
      };
      
      this.ws.onclose = () => {
        console.log('⚠️ WebSocket disconnected');
        // Reconnect after 5 seconds
        setTimeout(() => this.setupWebSocket(), 5000);
      };
      
      this.ws.onerror = (error) => {
        this.handleError('WebSocket error', error);
      };
    } catch (error) {
      console.log('WebSocket not available, using polling');
      this.setupPolling();
    }
  }

  setupPolling() {
    // Poll for updates every 30 seconds
    setInterval(() => {
      this.refreshDashboardData();
    }, 30000);
  }

  handleRealTimeUpdate(data) {
    switch (data.type) {
      case 'metrics_update':
        this.metricsData = { ...this.metricsData, ...data.payload };
        this.updateMetrics();
        break;
      case 'new_case':
        this.showNotification('New case added', data.payload.title);
        this.loadRecentCases();
        break;
      case 'case_update':
        this.loadRecentCases();
        break;
      case 'ai_insight':
        this.loadAIInsights();
        break;
      default:
        console.log('Unknown real-time update:', data);
    }
  }

  /**
   * Data loading
   */
  async loadDashboardData() {
    try {
      const promises = [
        this.loadRecentCases(),
        this.loadAIInsights(),
        this.loadRecentActivity()
      ];
      
      await Promise.all(promises);
      this.trackPerformance('dashboard_data_loaded');
    } catch (error) {
      this.handleError('Failed to load dashboard data', error);
    }
  }

  async loadRecentCases() {
    try {
      const response = await fetch('/api/cases/recent');
      const cases = await response.json();
      
      this.renderRecentCases(cases);
    } catch (error) {
      this.handleError('Failed to load recent cases', error);
      this.showErrorState('#recent-cases-list', 'Failed to load recent cases');
    }
  }

  async loadAIInsights() {
    try {
      const response = await fetch('/api/ai/insights');
      const insights = await response.json();
      
      this.renderAIInsights(insights);
    } catch (error) {
      this.handleError('Failed to load AI insights', error);
      this.showErrorState('#ai-insights-list', 'Failed to load AI insights');
    }
  }

  async loadRecentActivity() {
    try {
      const response = await fetch('/api/activity/recent');
      const activity = await response.json();
      
      this.renderRecentActivity(activity);
    } catch (error) {
      this.handleError('Failed to load recent activity', error);
      this.showErrorState('#recent-activity-list', 'Failed to load recent activity');
    }
  }

  /**
   * Rendering methods
   */
  renderRecentCases(cases) {
    const container = document.getElementById('recent-cases-list');
    if (!container) return;
    
    if (!cases || cases.length === 0) {
      container.innerHTML = '<div class="empty-state">No recent cases</div>';
      return;
    }
    
    const html = cases.map(case_ => `
      <div class="case-item" data-case-id="${case_.id}">
        <div class="case-info">
          <div class="case-title">${this.escapeHtml(case_.title)}</div>
          <div class="case-meta">
            <span class="case-patient">${this.escapeHtml(case_.patient_name)}</span>
            <span class="case-date">${this.formatDate(case_.created_at)}</span>
          </div>
        </div>
        <div class="case-status case-status--${case_.status}">
          ${this.escapeHtml(case_.status)}
        </div>
      </div>
    `).join('');
    
    container.innerHTML = html;
  }

  renderAIInsights(insights) {
    const container = document.getElementById('ai-insights-list');
    if (!container) return;
    
    if (!insights || insights.length === 0) {
      container.innerHTML = '<div class="empty-state">No insights available</div>';
      return;
    }
    
    const html = insights.map(insight => `
      <div class="insight-item insight-item--${insight.type}">
        <div class="insight-icon">
          <svg class="insight-icon-svg" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
        </div>
        <div class="insight-content">
          <div class="insight-title">${this.escapeHtml(insight.title)}</div>
          <div class="insight-description">${this.escapeHtml(insight.description)}</div>
          <div class="insight-confidence">Confidence: ${insight.confidence}%</div>
        </div>
      </div>
    `).join('');
    
    container.innerHTML = html;
  }

  renderRecentActivity(activity) {
    const container = document.getElementById('recent-activity-list');
    if (!container) return;
    
    if (!activity || activity.length === 0) {
      container.innerHTML = '<div class="empty-state">No recent activity</div>';
      return;
    }
    
    const html = activity.map(item => `
      <div class="activity-item">
        <div class="activity-icon activity-icon--${item.type}">
          <svg class="activity-icon-svg" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
        </div>
        <div class="activity-content">
          <div class="activity-description">${this.escapeHtml(item.description)}</div>
          <div class="activity-meta">
            <span class="activity-user">${this.escapeHtml(item.user)}</span>
            <span class="activity-time">${this.formatDate(item.timestamp)}</span>
          </div>
        </div>
      </div>
    `).join('');
    
    container.innerHTML = html;
  }

  showErrorState(selector, message) {
    const container = document.querySelector(selector);
    if (container) {
      container.innerHTML = `
        <div class="error-state">
          <svg class="error-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
          </svg>
          <span class="error-message">${this.escapeHtml(message)}</span>
          <button class="error-retry" onclick="window.dashboard.loadDashboardData()">Retry</button>
        </div>
      `;
    }
  }

  /**
   * User interactions
   */
  handleQuickAction(button) {
    const action = button.getAttribute('data-action');
    
    switch (action) {
      case 'new-patient':
        this.openNewPatientModal();
        break;
      case 'schedule-surgery':
        this.openScheduleModal();
        break;
      case 'view-reports':
        window.location.href = '/reports';
        break;
      case 'ai-analysis':
        window.location.href = '/ai-insights';
        break;
    }
    
    this.trackInteraction('quick_action', { action });
  }

  openNewCaseModal() {
    // Implementation for new case modal
    console.log('Opening new case modal');
    this.trackInteraction('new_case_modal');
  }

  openNewPatientModal() {
    // Implementation for new patient modal
    console.log('Opening new patient modal');
    this.trackInteraction('new_patient_modal');
  }

  openScheduleModal() {
    // Implementation for schedule modal
    console.log('Opening schedule modal');
    this.trackInteraction('schedule_modal');
  }

  toggleUserMenu() {
    // Implementation for user menu
    console.log('Toggle user menu');
    this.trackInteraction('user_menu_toggle');
  }

  refreshAIInsights() {
    const button = document.getElementById('refresh-insights');
    if (button) {
      button.disabled = true;
      button.textContent = 'Refreshing...';
    }
    
    this.loadAIInsights().finally(() => {
      if (button) {
        button.disabled = false;
        button.textContent = 'Refresh';
      }
    });
    
    this.trackInteraction('refresh_insights');
  }

  async refreshDashboardData() {
    try {
      // Refresh metrics
      const metricsResponse = await fetch('/api/metrics');
      const metrics = await metricsResponse.json();
      this.metricsData = { ...this.metricsData, ...metrics };
      this.updateMetrics();
      
      // Refresh other data
      await this.loadDashboardData();
    } catch (error) {
      this.handleError('Failed to refresh dashboard data', error);
    }
  }

  /**
   * Keyboard shortcuts
   */
  handleKeyboardShortcuts(e) {
    // Cmd/Ctrl + K for search
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      this.focusGlobalSearch();
    }
    
    // Escape to close dropdowns
    if (e.key === 'Escape') {
      this.closeAllDropdowns();
    }
    
    // Cmd/Ctrl + N for new case
    if ((e.metaKey || e.ctrlKey) && e.key === 'n') {
      e.preventDefault();
      this.openNewCaseModal();
    }
  }

  handleOutsideClick(e) {
    // Close dropdowns when clicking outside
    if (!e.target.closest('.search-container')) {
      this.hideSearchSuggestions();
    }
  }

  closeAllDropdowns() {
    this.hideSearchSuggestions();
    // Close other dropdowns
  }

  /**
   * Utility methods
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  }

  showNotification(title, message) {
    // Implementation for showing toast notifications
    console.log('Notification:', title, message);
  }

  /**
   * Analytics and performance
   */
  trackInteraction(action, data = {}) {
    this.performanceMetrics.interactions++;
    
    // Send to analytics service
    if (window.gtag) {
      window.gtag('event', action, {
        ...data,
        app_name: 'surge_dashboard'
      });
    }
    
    console.log('📊 Interaction:', action, data);
  }

  trackPerformance(event, data = {}) {
    const timestamp = performance.now();
    
    console.log('⚡ Performance:', event, {
      timestamp,
      loadTime: timestamp - this.performanceMetrics.loadStart,
      ...data
    });
  }

  handleError(message, error) {
    this.performanceMetrics.errors++;
    
    console.error('❌ Dashboard Error:', message, error);
    
    // Send to error tracking service
    if (window.Sentry) {
      window.Sentry.captureException(error, {
        tags: {
          component: 'dashboard',
          message: message
        }
      });
    }
  }
}

// Initialize dashboard when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new SurgeDashboard();
  });
} else {
  window.dashboard = new SurgeDashboard();
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SurgeDashboard;
}
