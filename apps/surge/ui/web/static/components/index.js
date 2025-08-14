/**
 * Surgify UI Components Library
 * A collection of reusable UI components for the Surgify platform
 */

// Import all components
import './DomainSelector.js';
import './CaseList.js';
import './CaseDetail.js';
import './NotificationBadge.js';
import './ThemeToggle.js';
import './ChatIntegration.js';

// Component registry for dynamic loading
const ComponentRegistry = {
    DomainSelector: window.DomainSelector,
    CaseList: window.CaseList,
    CaseDetail: window.CaseDetail,
    NotificationBadge: window.NotificationBadge,
    ThemeToggle: window.ThemeToggle,
    ChatIntegration: window.ChatIntegration
};

// Utility function to initialize components from HTML data attributes
function initializeComponents() {
    // Initialize DomainSelectors
    document.querySelectorAll('[data-component="domain-selector"][data-auto-init="true"]').forEach(element => {
        const options = {
            domains: element.dataset.domains ? JSON.parse(element.dataset.domains) : undefined,
            selectedDomain: element.dataset.selectedDomain,
            placeholder: element.dataset.placeholder,
            htmxEndpoint: element.dataset.htmxEndpoint,
            className: element.dataset.className
        };
        
        const selector = new ComponentRegistry.DomainSelector(element.id, options);
        selector.render();
    });

    // Initialize CaseLists
    document.querySelectorAll('[data-component="case-list"][data-auto-init="true"]').forEach(element => {
        const options = {
            cases: element.dataset.cases ? JSON.parse(element.dataset.cases) : [],
            showSearch: element.dataset.showSearch !== 'false',
            showFilters: element.dataset.showFilters !== 'false',
            showPagination: element.dataset.showPagination !== 'false',
            pageSize: element.dataset.pageSize ? parseInt(element.dataset.pageSize) : 10,
            htmxEndpoint: element.dataset.htmxEndpoint,
            className: element.dataset.className
        };
        
        const caseList = new ComponentRegistry.CaseList(element.id, options);
        caseList.render();
    });

    // Initialize CaseDetails
    document.querySelectorAll('[data-component="case-detail"][data-auto-init="true"]').forEach(element => {
        const options = {
            case: element.dataset.case ? JSON.parse(element.dataset.case) : null,
            showTabs: element.dataset.showTabs !== 'false',
            showActions: element.dataset.showActions !== 'false',
            htmxEndpoint: element.dataset.htmxEndpoint,
            className: element.dataset.className
        };
        
        const caseDetail = new ComponentRegistry.CaseDetail(element.id, options);
        caseDetail.render();
    });

    // Initialize NotificationBadges
    document.querySelectorAll('[data-component="notification-badge"][data-auto-init="true"]').forEach(element => {
        const options = {
            count: element.dataset.count ? parseInt(element.dataset.count) : 0,
            type: element.dataset.type || 'default',
            size: element.dataset.size || 'medium',
            position: element.dataset.position || 'top-right',
            htmxEndpoint: element.dataset.htmxEndpoint,
            autoUpdate: element.dataset.autoUpdate === 'true',
            className: element.dataset.className
        };
        
        const badge = new ComponentRegistry.NotificationBadge(element.id, options);
        badge.render();
    });

    // Initialize ThemeToggles
    document.querySelectorAll('[data-component="theme-toggle"][data-auto-init="true"]').forEach(element => {
        const options = {
            theme: element.dataset.theme || 'light',
            style: element.dataset.style || 'switch',
            size: element.dataset.size || 'medium',
            showLabel: element.dataset.showLabel !== 'false',
            autoDetect: element.dataset.autoDetect === 'true',
            htmxEndpoint: element.dataset.htmxEndpoint,
            className: element.dataset.className
        };
        
        const toggle = new ComponentRegistry.ThemeToggle(element.id, options);
        toggle.render();
    });

    // Initialize ChatIntegrations
    document.querySelectorAll('[data-component="chat-integration"][data-auto-init="true"]').forEach(element => {
        const options = {
            showChatwoot: element.dataset.showChatwoot !== 'false',
            showDiscord: element.dataset.showDiscord !== 'false',
            autoConnect: element.dataset.autoConnect !== 'false',
            position: element.dataset.position || 'bottom-right',
            theme: element.dataset.theme || 'light',
            className: element.dataset.className
        };
        
        const chat = new ComponentRegistry.ChatIntegration(element.id, options);
        chat.render();
    });
}

// Auto-initialize components when DOM is ready
document.addEventListener('DOMContentLoaded', initializeComponents);

// Re-initialize components after HTMX requests
document.addEventListener('htmx:afterSettle', initializeComponents);

// Component factory function
function createComponent(type, containerId, options = {}) {
    const ComponentClass = ComponentRegistry[type];
    if (!ComponentClass) {
        console.error(`Component type "${type}" not found in registry`);
        return null;
    }
    
    const component = new ComponentClass(containerId, options);
    component.render();
    return component;
}

// Batch component creation
function createComponents(components) {
    const instances = {};
    
    components.forEach(config => {
        if (config.type && config.containerId) {
            const instance = createComponent(config.type, config.containerId, config.options);
            if (instance) {
                instances[config.containerId] = instance;
            }
        }
    });
    
    return instances;
}

// Global component management
window.SurgifyComponents = {
    Registry: ComponentRegistry,
    initialize: initializeComponents,
    create: createComponent,
    createBatch: createComponents,
    
    // Individual component constructors
    DomainSelector: ComponentRegistry.DomainSelector,
    CaseList: ComponentRegistry.CaseList,
    CaseDetail: ComponentRegistry.CaseDetail,
    NotificationBadge: ComponentRegistry.NotificationBadge,
    ThemeToggle: ComponentRegistry.ThemeToggle,
    ChatIntegration: ComponentRegistry.ChatIntegration,
    
    // Utility functions
    utils: {
        // Helper to get component instance from DOM element
        getInstance: function(element) {
            return element._componentInstance || null;
        },
        
        // Helper to set component instance on DOM element
        setInstance: function(element, instance) {
            element._componentInstance = instance;
        },
        
        // Helper to clean up component instances
        cleanup: function(element) {
            const instance = element._componentInstance;
            if (instance && typeof instance.destroy === 'function') {
                instance.destroy();
            }
            delete element._componentInstance;
        }
    }
};

// Export for ES6 modules
export {
    ComponentRegistry,
    initializeComponents,
    createComponent,
    createComponents
};

export default window.SurgifyComponents;
