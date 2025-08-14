/**
 * YAZ Shared Component Library
 * Reusable UI components for all YAZ applications
 */

class YazComponents {
    constructor() {
        this.components = new Map();
        this.themes = {
            light: {
                primary: '#2563eb',
                secondary: '#64748b',
                success: '#10b981',
                danger: '#ef4444',
                warning: '#f59e0b',
                info: '#3b82f6',
                background: '#ffffff',
                surface: '#f8fafc',
                text: '#1e293b',
                textMuted: '#64748b'
            },
            dark: {
                primary: '#3b82f6',
                secondary: '#94a3b8',
                success: '#34d399',
                danger: '#f87171',
                warning: '#fbbf24',
                info: '#60a5fa',
                background: '#0f172a',
                surface: '#1e293b',
                text: '#f1f5f9',
                textMuted: '#94a3b8'
            }
        };
        this.currentTheme = 'light';
        this.init();
    }
    
    init() {
        this.registerComponents();
        this.injectStyles();
        this.setupThemeToggle();
    }
    
    registerComponents() {
        // Register all component templates
        this.components.set('notification', this.notificationTemplate);
        this.components.set('modal', this.modalTemplate);
        this.components.set('card', this.cardTemplate);
        this.components.set('button', this.buttonTemplate);
        this.components.set('input', this.inputTemplate);
        this.components.set('loader', this.loaderTemplate);
        this.components.set('chart', this.chartTemplate);
        this.components.set('table', this.tableTemplate);
        this.components.set('form', this.formTemplate);
        this.components.set('header', this.headerTemplate);
        this.components.set('sidebar', this.sidebarTemplate);
        this.components.set('bottomNav', this.bottomNavTemplate);
    }
    
    // Component Templates
    notificationTemplate(options = {}) {
        const { type = 'info', title, message, duration = 5000, actions = [] } = options;
        
        const notification = document.createElement('div');
        notification.className = `yaz-notification yaz-notification-${type}`;
        notification.innerHTML = `
            <div class="yaz-notification-content">
                <div class="yaz-notification-header">
                    <i class="yaz-notification-icon fas fa-${this.getNotificationIcon(type)}"></i>
                    ${title ? `<h4 class="yaz-notification-title">${title}</h4>` : ''}
                    <button class="yaz-notification-close" onclick="this.parentElement.parentElement.parentElement.remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <p class="yaz-notification-message">${message}</p>
                ${actions.length > 0 ? `
                    <div class="yaz-notification-actions">
                        ${actions.map(action => `
                            <button class="yaz-btn yaz-btn-sm yaz-btn-${action.type || 'primary'}" 
                                    onclick="${action.onclick}">
                                ${action.label}
                            </button>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
        
        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, duration);
        }
        
        return notification;
    }
    
    modalTemplate(options = {}) {
        const { title, content, size = 'md', closable = true } = options;
        
        const modal = document.createElement('div');
        modal.className = `yaz-modal yaz-modal-${size}`;
        modal.innerHTML = `
            <div class="yaz-modal-overlay" onclick="this.parentElement.remove()"></div>
            <div class="yaz-modal-content">
                <div class="yaz-modal-header">
                    <h3 class="yaz-modal-title">${title}</h3>
                    ${closable ? `
                        <button class="yaz-modal-close" onclick="this.parentElement.parentElement.parentElement.remove()">
                            <i class="fas fa-times"></i>
                        </button>
                    ` : ''}
                </div>
                <div class="yaz-modal-body">
                    ${content}
                </div>
            </div>
        `;
        
        return modal;
    }
    
    cardTemplate(options = {}) {
        const { title, content, actions = [], className = '' } = options;
        
        const card = document.createElement('div');
        card.className = `yaz-card ${className}`;
        card.innerHTML = `
            ${title ? `<div class="yaz-card-header"><h3 class="yaz-card-title">${title}</h3></div>` : ''}
            <div class="yaz-card-body">${content}</div>
            ${actions.length > 0 ? `
                <div class="yaz-card-footer">
                    ${actions.map(action => `
                        <button class="yaz-btn yaz-btn-${action.type || 'primary'}" 
                                onclick="${action.onclick}">
                            ${action.label}
                        </button>
                    `).join('')}
                </div>
            ` : ''}
        `;
        
        return card;
    }
    
    buttonTemplate(options = {}) {
        const { 
            label, 
            type = 'primary', 
            size = 'md', 
            icon, 
            onclick, 
            disabled = false,
            loading = false 
        } = options;
        
        const button = document.createElement('button');
        button.className = `yaz-btn yaz-btn-${type} yaz-btn-${size}`;
        button.disabled = disabled || loading;
        
        if (onclick) {
            button.onclick = onclick;
        }
        
        button.innerHTML = `
            ${loading ? '<i class="fas fa-spinner fa-spin"></i>' : ''}
            ${icon && !loading ? `<i class="fas fa-${icon}"></i>` : ''}
            <span>${label}</span>
        `;
        
        return button;
    }
    
    inputTemplate(options = {}) {
        const { 
            type = 'text', 
            placeholder, 
            label, 
            value = '', 
            required = false,
            error 
        } = options;
        
        const wrapper = document.createElement('div');
        wrapper.className = 'yaz-input-group';
        
        wrapper.innerHTML = `
            ${label ? `<label class="yaz-label">${label}${required ? ' *' : ''}</label>` : ''}
            <input type="${type}" 
                   class="yaz-input ${error ? 'yaz-input-error' : ''}" 
                   placeholder="${placeholder || ''}"
                   value="${value}"
                   ${required ? 'required' : ''}>
            ${error ? `<span class="yaz-input-error-text">${error}</span>` : ''}
        `;
        
        return wrapper;
    }
    
    loaderTemplate(options = {}) {
        const { size = 'md', text = 'Loading...', type = 'spinner' } = options;
        
        const loader = document.createElement('div');
        loader.className = `yaz-loader yaz-loader-${size}`;
        
        if (type === 'spinner') {
            loader.innerHTML = `
                <div class="yaz-spinner"></div>
                ${text ? `<p class="yaz-loader-text">${text}</p>` : ''}
            `;
        } else if (type === 'pulse') {
            loader.innerHTML = `
                <div class="yaz-pulse"></div>
                ${text ? `<p class="yaz-loader-text">${text}</p>` : ''}
            `;
        }
        
        return loader;
    }
    
    headerTemplate(options = {}) {
        const { title = 'YAZ Healthcare', user, notifications = 0 } = options;
        
        const header = document.createElement('header');
        header.className = 'yaz-header';
        header.innerHTML = `
            <div class="yaz-header-content">
                <div class="yaz-header-left">
                    <button class="yaz-menu-toggle md:hidden">
                        <i class="fas fa-bars"></i>
                    </button>
                    <h1 class="yaz-header-title">${title}</h1>
                </div>
                <div class="yaz-header-right">
                    <div class="yaz-header-actions">
                        <button class="yaz-header-action" id="theme-toggle">
                            <i class="fas fa-sun"></i>
                        </button>
                        <button class="yaz-header-action" id="notifications">
                            <i class="fas fa-bell"></i>
                            ${notifications > 0 ? `<span class="yaz-badge">${notifications}</span>` : ''}
                        </button>
                        ${user ? `
                            <div class="yaz-user-menu">
                                <img src="${user.avatar || '/static/assets/default-avatar.png'}" 
                                     alt="${user.name}" class="yaz-avatar">
                                <span class="yaz-user-name hidden md:block">${user.name}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
        
        return header;
    }
    
    bottomNavTemplate(options = {}) {
        const { items = [] } = options;
        
        const nav = document.createElement('nav');
        nav.className = 'yaz-bottom-nav md:hidden';
        nav.innerHTML = `
            <div class="yaz-bottom-nav-content">
                ${items.map(item => `
                    <button class="yaz-bottom-nav-item ${item.active ? 'active' : ''}" 
                            onclick="${item.onclick}">
                        <i class="fas fa-${item.icon}"></i>
                        <span>${item.label}</span>
                    </button>
                `).join('')}
            </div>
        `;
        
        return nav;
    }
    
    // Utility methods
    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    // Public API methods
    create(componentType, options = {}) {
        const template = this.components.get(componentType);
        if (!template) {
            console.error(`❌ Component type '${componentType}' not found`);
            return null;
        }
        
        return template.call(this, options);
    }
    
    notify(options) {
        const notification = this.create('notification', options);
        this.getNotificationContainer().appendChild(notification);
        return notification;
    }
    
    modal(options) {
        const modal = this.create('modal', options);
        document.body.appendChild(modal);
        return modal;
    }
    
    getNotificationContainer() {
        let container = document.getElementById('yaz-notifications');
        if (!container) {
            container = document.createElement('div');
            container.id = 'yaz-notifications';
            container.className = 'yaz-notifications-container';
            document.body.appendChild(container);
        }
        return container;
    }
    
    // Theme management
    setTheme(theme) {
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('yaz-theme', theme);
        
        // Update theme toggle icon
        const toggle = document.getElementById('theme-toggle');
        if (toggle) {
            const icon = toggle.querySelector('i');
            icon.className = theme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
        }
    }
    
    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }
    
    setupThemeToggle() {
        // Load saved theme
        const savedTheme = localStorage.getItem('yaz-theme') || 'light';
        this.setTheme(savedTheme);
        
        // Setup toggle listener
        document.addEventListener('click', (e) => {
            if (e.target.closest('#theme-toggle')) {
                this.toggleTheme();
            }
        });
    }
    
    injectStyles() {
        const style = document.createElement('style');
        style.textContent = `
            /* YAZ Component Library Styles */
            :root[data-theme="light"] {
                --yaz-primary: #2563eb;
                --yaz-secondary: #64748b;
                --yaz-success: #10b981;
                --yaz-danger: #ef4444;
                --yaz-warning: #f59e0b;
                --yaz-info: #3b82f6;
                --yaz-background: #ffffff;
                --yaz-surface: #f8fafc;
                --yaz-text: #1e293b;
                --yaz-text-muted: #64748b;
                --yaz-border: #e2e8f0;
                --yaz-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
            }
            
            :root[data-theme="dark"] {
                --yaz-primary: #3b82f6;
                --yaz-secondary: #94a3b8;
                --yaz-success: #34d399;
                --yaz-danger: #f87171;
                --yaz-warning: #fbbf24;
                --yaz-info: #60a5fa;
                --yaz-background: #0f172a;
                --yaz-surface: #1e293b;
                --yaz-text: #f1f5f9;
                --yaz-text-muted: #94a3b8;
                --yaz-border: #334155;
                --yaz-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
            }
            
            .yaz-btn {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 1rem;
                border: none;
                border-radius: 0.375rem;
                font-weight: 500;
                text-decoration: none;
                transition: all 0.2s;
                cursor: pointer;
            }
            
            .yaz-btn-primary {
                background-color: var(--yaz-primary);
                color: white;
            }
            
            .yaz-btn-primary:hover {
                background-color: color-mix(in srgb, var(--yaz-primary) 90%, black);
            }
            
            .yaz-btn-sm {
                padding: 0.25rem 0.75rem;
                font-size: 0.875rem;
            }
            
            .yaz-card {
                background: var(--yaz-surface);
                border: 1px solid var(--yaz-border);
                border-radius: 0.5rem;
                box-shadow: var(--yaz-shadow);
                overflow: hidden;
            }
            
            .yaz-card-header {
                padding: 1rem;
                border-bottom: 1px solid var(--yaz-border);
            }
            
            .yaz-card-body {
                padding: 1rem;
            }
            
            .yaz-card-footer {
                padding: 1rem;
                border-top: 1px solid var(--yaz-border);
                background: var(--yaz-background);
            }
            
            .yaz-notifications-container {
                position: fixed;
                top: 1rem;
                right: 1rem;
                z-index: 1000;
                max-width: 400px;
            }
            
            .yaz-notification {
                background: var(--yaz-surface);
                border: 1px solid var(--yaz-border);
                border-radius: 0.5rem;
                box-shadow: var(--yaz-shadow);
                margin-bottom: 0.5rem;
                padding: 1rem;
                animation: slideIn 0.3s ease-out;
            }
            
            .yaz-notification-success {
                border-left: 4px solid var(--yaz-success);
            }
            
            .yaz-notification-error {
                border-left: 4px solid var(--yaz-danger);
            }
            
            .yaz-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 1000;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .yaz-modal-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
            }
            
            .yaz-modal-content {
                background: var(--yaz-surface);
                border-radius: 0.5rem;
                box-shadow: var(--yaz-shadow);
                max-width: 90vw;
                max-height: 90vh;
                overflow: auto;
                position: relative;
            }
            
            .yaz-header {
                background: var(--yaz-surface);
                border-bottom: 1px solid var(--yaz-border);
                box-shadow: var(--yaz-shadow);
            }
            
            .yaz-header-content {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 1rem;
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .yaz-bottom-nav {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: var(--yaz-surface);
                border-top: 1px solid var(--yaz-border);
                padding: 0.5rem;
                z-index: 100;
            }
            
            .yaz-bottom-nav-content {
                display: flex;
                justify-content: space-around;
            }
            
            .yaz-bottom-nav-item {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 0.25rem;
                padding: 0.5rem;
                border: none;
                background: none;
                color: var(--yaz-text-muted);
                font-size: 0.75rem;
                cursor: pointer;
            }
            
            .yaz-bottom-nav-item.active {
                color: var(--yaz-primary);
            }
            
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @media (max-width: 768px) {
                .yaz-notifications-container {
                    left: 1rem;
                    right: 1rem;
                    max-width: none;
                }
                
                .yaz-modal-content {
                    margin: 1rem;
                    max-width: calc(100vw - 2rem);
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// Export and initialize
window.YazComponents = YazComponents;
window.yazUI = new YazComponents();
