/**
 * Enhanced Islands Bootstrap with Dash/Interact Coordination
 * High-End OR System Integration
 * Coordinates FastHTML + HTMX with React Islands
 */

class SurgeIslandsBridge {
    constructor() {
        this.mountedIslands = new Map();
        this.islandComponents = new Map();
        this.eventBus = new EventTarget();
        this.projectCoordination = {
            dash: new Map(),
            interact: new Map()
        };
        this.setupProjectCoordination();
        this.setupORSystemIntegration();
    }

    // Setup coordination with existing Dash and Interact projects
    setupProjectCoordination() {
        // Dash project coordination - Analytics & OR Management
        window.addEventListener('dash:stateChange', (event) => {
            this.coordinateDashState(event.detail);
        });
        
        window.addEventListener('dash:analyticsUpdate', (event) => {
            this.forwardAnalyticsUpdate(event.detail);
        });
        
        // Interact project coordination - Case Management & Workflows
        window.addEventListener('interact:stateChange', (event) => {
            this.coordinateInteractState(event.detail);
        });
        
        window.addEventListener('interact:caseUpdate', (event) => {
            this.forwardCaseUpdate(event.detail);
        });
        
        // Unified platform events for OR system
        window.addEventListener('surge:projectUpdate', (event) => {
            this.handleProjectUpdate(event.detail);
        });

        // Cross-island communication
        window.addEventListener('island:update', (event) => {
            this.handleIslandUpdate(event.detail);
        });
    }

    // Setup OR System specific integrations
    setupORSystemIntegration() {
        // Case status updates
        window.addEventListener('case:update', (event) => {
            this.broadcastCaseUpdate(event.detail);
        });

        // Analytics updates
        window.addEventListener('analytics:update', (event) => {
            this.broadcastAnalyticsUpdate(event.detail);
        });

        // OR board updates
        window.addEventListener('or:update', (event) => {
            this.broadcastORUpdate(event.detail);
        });

        // Alert system
        window.addEventListener('alert:new', (event) => {
            this.handleNewAlert(event.detail);
        });

        // HTMX integration for server sync
        if (window.htmx) {
            window.htmx.on('htmx:afterSwap', (event) => {
                this.handleHTMXSwap(event);
            });
        }
    }

    // Enhanced component loading with project awareness
    async loadIslandComponent(islandType, componentName, projectContext = null) {
        const key = `${islandType}:${componentName}`;
        
        if (this.islandComponents.has(key)) {
            return this.islandComponents.get(key);
        }

        try {
            let modulePath;
            switch (islandType) {
                case 'dash':
                    modulePath = `/islands/dash/dist/assets/index.js`;
                    break;
                case 'interact':
                    modulePath = `/islands/interact/dist/assets/index.js`;
                    break;
                default:
                    modulePath = `/static/components/${componentName}.js`;
            }

            const module = await import(modulePath);
            const component = module.default || module[componentName];
            
            this.islandComponents.set(key, component);
            return component;
        } catch (error) {
            console.warn(`Failed to load island component ${key}:`, error);
            return null;
        }
    }

    // Coordinate Dash analytics state
    coordinateDashState(dashState) {
        // Update interact island with relevant analytics
        const interactState = this.projectCoordination.interact.get('currentState') || {};
        
        // Share relevant analytics data
        const sharedData = {
            roomUtilization: dashState.analytics?.summary?.roomUtilization,
            activeCases: dashState.analytics?.summary?.activeCases,
            alerts: dashState.alerts
        };

        this.projectCoordination.interact.set('dashAnalytics', sharedData);
        this.eventBus.dispatchEvent(new CustomEvent('interact:updateFromDash', { 
            detail: sharedData 
        }));
    }

    // Coordinate Interact case state
    coordinateInteractState(interactState) {
        // Update dash island with case updates
        const dashState = this.projectCoordination.dash.get('currentState') || {};
        
        // Share case status changes for analytics
        const caseUpdates = {
            caseEvents: interactState.caseEvents,
            statusChanges: interactState.statusChanges,
            instrumentCounts: interactState.instrumentCounts
        };

        this.projectCoordination.dash.set('caseUpdates', caseUpdates);
        this.eventBus.dispatchEvent(new CustomEvent('dash:updateFromInteract', { 
            detail: caseUpdates 
        }));
    }

    // Forward analytics updates to all interested components
    forwardAnalyticsUpdate(analyticsData) {
        // Update HTMX components
        if (window.htmx) {
            window.htmx.trigger(document.body, 'analytics:refresh', analyticsData);
        }
        
        // Update dashboard stats
        this.updateDashboardStats(analyticsData);
    }

    // Forward case updates to all interested components
    forwardCaseUpdate(caseData) {
        // Update HTMX components
        if (window.htmx) {
            window.htmx.trigger(document.body, 'case:refresh', caseData);
        }
        
        // Update OR board
        this.updateORBoard(caseData);
    }

    // Broadcast case updates to all islands
    broadcastCaseUpdate(caseData) {
        // Update Dash analytics
        this.eventBus.dispatchEvent(new CustomEvent('dash:caseUpdate', { 
            detail: caseData 
        }));
        
        // Update server via HTMX
        if (window.htmx) {
            window.htmx.ajax('POST', '/api/v1/events/case-update', {
                values: { caseData: JSON.stringify(caseData) }
            });
        }
    }

    // Broadcast analytics updates
    broadcastAnalyticsUpdate(analyticsData) {
        // Update Interact workstation
        this.eventBus.dispatchEvent(new CustomEvent('interact:analyticsUpdate', { 
            detail: analyticsData 
        }));
        
        // Update HTMX dashboard components
        const statsElements = document.querySelectorAll('[data-analytics-stat]');
        statsElements.forEach(el => {
            const stat = el.getAttribute('data-analytics-stat');
            if (analyticsData.summary[stat] !== undefined) {
                el.textContent = analyticsData.summary[stat];
            }
        });
    }

    // Handle new alerts
    handleNewAlert(alertData) {
        // Show alert in UI
        this.showAlert(alertData);
        
        // Update both islands
        this.eventBus.dispatchEvent(new CustomEvent('dash:newAlert', { 
            detail: alertData 
        }));
        this.eventBus.dispatchEvent(new CustomEvent('interact:newAlert', { 
            detail: alertData 
        }));
        
        // Sync with server
        if (window.htmx) {
            window.htmx.ajax('POST', '/api/v1/alerts', {
                values: { alert: JSON.stringify(alertData) }
            });
        }
    }

    // Handle HTMX swaps and re-initialize islands if needed
    handleHTMXSwap(event) {
        const target = event.detail.target;
        const islandElements = target.querySelectorAll('[data-island]');
        
        islandElements.forEach(el => {
            const islandType = el.getAttribute('data-island');
            const propsId = el.getAttribute('data-island-props');
            
            if (propsId) {
                const propsScript = document.getElementById(propsId);
                if (propsScript) {
                    try {
                        const props = JSON.parse(propsScript.textContent);
                        this.mountIsland(el, islandType, props);
                    } catch (error) {
                        console.warn('Failed to parse island props:', error);
                    }
                }
            }
        });
    }

    // Show alert in UI
    showAlert(alertData) {
        const alertContainer = document.getElementById('alert-container') || this.createAlertContainer();
        
        const alertEl = document.createElement('div');
        alertEl.className = `alert alert-${alertData.severity} mb-2 p-3 rounded border-l-4 ${
            alertData.severity === 'critical' ? 'border-red-500 bg-red-50' :
            alertData.severity === 'high' ? 'border-orange-500 bg-orange-50' :
            alertData.severity === 'medium' ? 'border-yellow-500 bg-yellow-50' :
            'border-blue-500 bg-blue-50'
        }`;
        
        alertEl.innerHTML = `
            <div class="flex justify-between items-start">
                <div>
                    <p class="font-medium">${alertData.type.replace('_', ' ').toUpperCase()}</p>
                    <p class="text-sm">${alertData.message}</p>
                    <p class="text-xs text-gray-500">${new Date(alertData.timestamp).toLocaleString()}</p>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" class="text-gray-400 hover:text-gray-600">×</button>
            </div>
        `;
        
        alertContainer.appendChild(alertEl);
        
        // Auto-remove after 10 seconds for non-critical alerts
        if (alertData.severity !== 'critical') {
            setTimeout(() => {
                if (alertEl.parentNode) {
                    alertEl.remove();
                }
            }, 10000);
        }
    }

    // Create alert container if it doesn't exist
    createAlertContainer() {
        const container = document.createElement('div');
        container.id = 'alert-container';
        container.className = 'fixed top-4 right-4 z-50 max-w-sm';
        document.body.appendChild(container);
        return container;
    }

    // Mount a React island
    async mountIsland(element, islandType, props = {}) {
        if (this.mountedIslands.has(element)) {
            return;
        }

        try {
            const component = await this.loadIslandComponent(islandType, islandType);
            if (!component) {
                console.warn(`Failed to load component for island type: ${islandType}`);
                return;
            }

            // Use React 18 createRoot if available, otherwise ReactDOM.render
            if (window.React && window.ReactDOM) {
                if (window.ReactDOM.createRoot) {
                    const root = window.ReactDOM.createRoot(element);
                    root.render(window.React.createElement(component, props));
                    this.mountedIslands.set(element, { root, component, props });
                } else {
                    window.ReactDOM.render(
                        window.React.createElement(component, props),
                        element
                    );
                    this.mountedIslands.set(element, { component, props });
                }
            }
        } catch (error) {
            console.error(`Failed to mount island ${islandType}:`, error);
            // Show fallback content
            element.innerHTML = `
                <div class="p-4 border border-red-200 rounded bg-red-50">
                    <p class="text-red-600">Failed to load ${islandType} component</p>
                    <button onclick="location.reload()" class="mt-2 px-3 py-1 bg-red-600 text-white rounded text-sm">
                        Retry
                    </button>
                </div>
            `;
        }
    }

    // Initialize all islands on page load
    async initializeIslands(islandConfig = {}) {
        const islandElements = document.querySelectorAll('[data-island]');
        
        for (const element of islandElements) {
            const islandType = element.getAttribute('data-island');
            const propsId = element.getAttribute('data-island-props') || `props-${islandType}`;
            
            let props = islandConfig[islandType] || {};
            
            // Try to get props from script tag
            const propsScript = document.getElementById(propsId);
            if (propsScript) {
                try {
                    props = { ...props, ...JSON.parse(propsScript.textContent) };
                } catch (error) {
                    console.warn(`Failed to parse props for ${islandType}:`, error);
                }
            }
            
            await this.mountIsland(element, islandType, props);
        }
        
        console.log('SURGE Islands initialized successfully');
    }
}

// Initialize the bridge
const surgeIslandsBridge = new SurgeIslandsBridge();

// Export for global access
window.surgeIslandsBridge = surgeIslandsBridge;

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        const config = window.surgePlatform?.islands || {};
        surgeIslandsBridge.initializeIslands(config);
    });
} else {
    const config = window.surgePlatform?.islands || {};
    surgeIslandsBridge.initializeIslands(config);
}

// Export the initialization function
export const initializeIslands = (config) => surgeIslandsBridge.initializeIslands(config);

        let component;
        
        try {
            switch (islandType) {
                case 'dash':
                    const { default: DashAdapter } = await import('/static/islands/DashAdapter.js');
                    component = DashAdapter;
                    this.projectCoordination.dash.set(componentName, key);
                    break;
                    
                case 'interact':
                    const { default: InteractAdapter } = await import('/static/islands/InteractAdapter.js');
                    component = InteractAdapter;
                    this.projectCoordination.interact.set(componentName, key);
                    break;
                    
                case 'calendar':
                    const { default: Calendar } = await import('/static/islands/unified/Calendar.js');
                    component = Calendar;
                    break;
                    
                case 'or-board':
                    const { default: ORBoard } = await import('/static/islands/unified/ORBoard.js');
                    component = ORBoard;
                    break;
                    
                case 'consent':
                    // Future component
                    console.log('ConsentPad component not yet implemented');
                    return null;
                    
                default:
                    console.warn(`Unknown island type: ${islandType}`);
                    return null;
            }
            
            this.islandComponents.set(key, component);
            console.log(`Loaded island component: ${key}`, { projectContext });
            return component;
            
        } catch (error) {
            console.error(`Failed to load island component ${key}:`, error);
            return null;
        }
    }

    // Enhanced island mounting with project coordination
    async mountIsland(containerId, config) {
        try {
            const container = document.getElementById(containerId);
            if (!container) {
                console.warn(`Container ${containerId} not found`);
                return false;
            }

            // Load React dependencies
            const React = await import('https://esm.sh/react@18');
            const ReactDOM = await import('https://esm.sh/react-dom@18');

            // Load component with project context
            const Component = await this.loadIslandComponent(
                config.type, 
                config.component || 'default',
                config.projectContext
            );
            
            if (!Component) {
                console.error(`Component not found for island: ${containerId}`);
                return false;
            }

            // Enhanced props with coordination
            const enhancedProps = {
                ...config.props,
                islandId: containerId,
                onNavigate: (path) => this.handleIslandNavigation(containerId, path, config),
                onStateChange: (state) => this.handleIslandStateChange(containerId, state, config),
                onAction: (action, data) => this.handleIslandAction(containerId, action, data, config),
                // Project coordination props
                dashConfig: window.surgePlatform?.dashConfig,
                interactConfig: window.surgePlatform?.interactConfig,
                coordinationBridge: {
                    toDash: (action, data) => this.coordinateToDash(action, data, containerId),
                    toInteract: (action, data) => this.coordinateToInteract(action, data, containerId),
                    toHTMX: (endpoint, data, options) => this.coordinateToHTMX(endpoint, data, options, config)
                }
            };

            // Create and mount React element
            const element = React.createElement(Component, enhancedProps);
            const root = ReactDOM.createRoot(container);
            root.render(element);

            // Store island reference with enhanced metadata
            this.mountedIslands.set(containerId, {
                root,
                config,
                container,
                projectType: config.type,
                projectContext: config.projectContext,
                mountedAt: Date.now()
            });

            console.log(`Island mounted: ${containerId}`, config);
            
            // Emit coordination event
            this.emitCoordinationEvent('islandMounted', {
                islandId: containerId,
                config,
                projectType: config.type
            });

            return true;
            
        } catch (error) {
            console.error(`Failed to mount island ${containerId}:`, error);
            return false;
        }
    }

    // Project coordination methods
    coordinateDashState(detail) {
        const { component, state } = detail;
        
        // Find related islands
        this.mountedIslands.forEach((island, islandId) => {
            if (island.projectType === 'dash' || island.config.dashRelated) {
                this.emitToIsland(islandId, 'dashStateChange', { component, state });
            }
        });
    }

    forwardDashAction(detail) {
        const { action, data, target } = detail;
        
        if (target) {
            this.emitToIsland(target, 'dashAction', { action, data });
        } else {
            // Broadcast to all dash-related islands
            this.mountedIslands.forEach((island, islandId) => {
                if (island.projectType === 'dash' || island.config.dashRelated) {
                    this.emitToIsland(islandId, 'dashAction', { action, data });
                }
            });
        }
    }

    coordinateInteractState(detail) {
        const { component, state } = detail;
        
        // Find related islands
        this.mountedIslands.forEach((island, islandId) => {
            if (island.projectType === 'interact' || island.config.interactRelated) {
                this.emitToIsland(islandId, 'interactStateChange', { component, state });
            }
        });
    }

    forwardInteractAction(detail) {
        const { action, data, target } = detail;
        
        if (target) {
            this.emitToIsland(target, 'interactAction', { action, data });
        } else {
            // Broadcast to all interact-related islands
            this.mountedIslands.forEach((island, islandId) => {
                if (island.projectType === 'interact' || island.config.interactRelated) {
                    this.emitToIsland(islandId, 'interactAction', { action, data });
                }
            });
        }
    }

    // Coordination bridge methods
    coordinateToDash(action, data, sourceIslandId) {
        window.dispatchEvent(new CustomEvent('surge:toDash', {
            detail: { action, data, source: sourceIslandId }
        }));
    }

    coordinateToInteract(action, data, sourceIslandId) {
        window.dispatchEvent(new CustomEvent('surge:toInteract', {
            detail: { action, data, source: sourceIslandId }
        }));
    }

    coordinateToHTMX(endpoint, data, options = {}, config = {}) {
        let targetEndpoint = endpoint;
        
        // Route based on project type
        if (config.type === 'dash') {
            targetEndpoint = `/api/v1/dash${endpoint}`;
        } else if (config.type === 'interact') {
            targetEndpoint = `/api/v1/interact${endpoint}`;
        }
        
        if (window.htmx) {
            htmx.ajax(options.method || 'POST', targetEndpoint, {
                values: data,
                target: options.target || 'body',
                ...options
            });
        }
    }

    // Enhanced navigation handling
    handleIslandNavigation(islandId, path, config) {
        console.log(`Island navigation: ${islandId} -> ${path}`);
        
        // Project-aware navigation
        if (config.type === 'dash') {
            window.dispatchEvent(new CustomEvent('dash:navigate', {
                detail: { path, source: islandId }
            }));
        } else if (config.type === 'interact') {
            window.dispatchEvent(new CustomEvent('interact:navigate', {
                detail: { path, source: islandId }
            }));
        } else {
            // Standard HTMX navigation
            if (window.htmx) {
                htmx.ajax('GET', path, { target: 'main' });
            } else {
                window.location.href = path;
            }
        }
    }

    // Enhanced state change handling
    handleIslandStateChange(islandId, state, config) {
        console.log(`Island state change: ${islandId}`, state);
        
        // Update stored state
        const island = this.mountedIslands.get(islandId);
        if (island) {
            island.state = state;
        }
        
        // Emit coordination events
        this.emitCoordinationEvent('islandStateChange', {
            islandId,
            state,
            projectType: config.type
        });
        
        // Project-specific coordination
        if (config.type === 'dash') {
            window.dispatchEvent(new CustomEvent('dash:stateFromIsland', {
                detail: { islandId, state }
            }));
        } else if (config.type === 'interact') {
            window.dispatchEvent(new CustomEvent('interact:stateFromIsland', {
                detail: { islandId, state }
            }));
        }
    }

    // Enhanced action handling
    handleIslandAction(islandId, action, data, config) {
        console.log(`Island action: ${islandId} -> ${action}`, data);
        
        this.emitCoordinationEvent('islandAction', {
            islandId,
            action,
            data,
            projectType: config.type
        });
    }

    // Utility methods
    emitToIsland(islandId, eventType, data) {
        window.dispatchEvent(new CustomEvent(`island:${islandId}:${eventType}`, {
            detail: data
        }));
    }

    emitCoordinationEvent(eventType, data) {
        window.dispatchEvent(new CustomEvent(`surge:${eventType}`, {
            detail: data
        }));
    }

    handleProjectUpdate(detail) {
        const { project, component, action, data } = detail;
        
        console.log(`Project update: ${project}`, { component, action, data });
        
        // Route to appropriate islands
        this.mountedIslands.forEach((island, islandId) => {
            if (island.projectType === project || island.config[`${project}Related`]) {
                this.emitToIsland(islandId, 'projectUpdate', { project, component, action, data });
            }
        });
    }

    // Enhanced scanning for new islands
    scanForNewIslands(container = document) {
        console.log('Scanning for new islands with project coordination...');
        
        const islandElements = container.querySelectorAll('[data-island]');
        const dashElements = container.querySelectorAll('[data-dash-component]');
        const interactElements = container.querySelectorAll('[data-interact-component]');
        
        // Mount new islands
        islandElements.forEach(async (element) => {
            const islandId = element.id;
            const islandType = element.dataset.island;
            const islandProps = element.dataset.props ? JSON.parse(element.dataset.props) : {};
            const projectContext = element.dataset.projectContext;
            
            if (!this.mountedIslands.has(islandId)) {
                await this.mountIsland(islandId, {
                    type: islandType,
                    props: islandProps,
                    projectContext,
                    dashRelated: element.dataset.dashRelated === 'true',
                    interactRelated: element.dataset.interactRelated === 'true'
                });
            }
        });
        
        // Handle Dash elements
        if (dashElements.length > 0) {
            window.dispatchEvent(new CustomEvent('surge:dashElementsFound', {
                detail: { elements: dashElements, container }
            }));
        }
        
        // Handle Interact elements
        if (interactElements.length > 0) {
            window.dispatchEvent(new CustomEvent('surge:interactElementsFound', {
                detail: { elements: interactElements, container }
            }));
        }
    }

    // Cleanup and unmounting
    unmountIsland(islandId) {
        const island = this.mountedIslands.get(islandId);
        if (island) {
            island.root.unmount();
            this.mountedIslands.delete(islandId);
            
            this.emitCoordinationEvent('islandUnmounted', {
                islandId,
                projectType: island.projectType
            });
            
            console.log(`Island unmounted: ${islandId}`);
            return true;
        }
        return false;
    }

    // Public API
    getIslandState(islandId) {
        const island = this.mountedIslands.get(islandId);
        return island ? island.state : null;
    }

    getAllIslands() {
        return Array.from(this.mountedIslands.keys());
    }

    getIslandsByProject(projectType) {
        return Array.from(this.mountedIslands.entries())
            .filter(([_, island]) => island.projectType === projectType)
            .map(([islandId, _]) => islandId);
    }
}

// Global instance
const surgeBridge = new SurgeIslandsBridge();

// Enhanced initialization
export async function initializeIslands(islandsConfig, coordinationConfig = {}) {
    try {
        console.log('Initializing islands with enhanced coordination...', islandsConfig);
        
        // Store coordination config globally
        if (coordinationConfig.dashConfig) {
            window.surgePlatform.dashConfig = coordinationConfig.dashConfig;
        }
        if (coordinationConfig.interactConfig) {
            window.surgePlatform.interactConfig = coordinationConfig.interactConfig;
        }
        
        // Mount configured islands
        for (const [islandId, config] of Object.entries(islandsConfig)) {
            await surgeBridge.mountIsland(islandId, config);
        }
        
        // Setup HTMX integration
        setupHTMXIntegration();
        
        // Expose global bridge
        window.islandsBridge = surgeBridge;
        window.surgeBridge = surgeBridge;
        
        console.log('Enhanced islands coordination initialized successfully');
        return true;
        
    } catch (error) {
        console.error('Failed to initialize enhanced islands:', error);
        return false;
    }
}

// HTMX integration setup
function setupHTMXIntegration() {
    // Enhanced HTMX event handling
    document.addEventListener('htmx:afterSwap', (event) => {
        surgeBridge.scanForNewIslands(event.detail.target);
        
        // Notify all islands of content change
        surgeBridge.emitCoordinationEvent('htmxContentSwapped', {
            target: event.detail.target,
            timestamp: Date.now()
        });
    });
    
    document.addEventListener('htmx:beforeRequest', (event) => {
        surgeBridge.emitCoordinationEvent('htmxBeforeRequest', {
            target: event.detail.target,
            verb: event.detail.verb,
            path: event.detail.path
        });
    });
}

// Export main functions
export const scanForNewIslands = (container) => surgeBridge.scanForNewIslands(container);
export const mountIsland = (containerId, config) => surgeBridge.mountIsland(containerId, config);
export const unmountIsland = (islandId) => surgeBridge.unmountIsland(islandId);

// Auto-initialize if config exists
if (typeof window !== 'undefined') {
    window.addEventListener('DOMContentLoaded', () => {
        if (window.surgePlatform?.islands) {
            initializeIslands(window.surgePlatform.islands, {
                dashConfig: window.surgePlatform.dashConfig,
                interactConfig: window.surgePlatform.interactConfig
            });
        }
    });
}
