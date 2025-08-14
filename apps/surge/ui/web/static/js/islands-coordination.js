/**
 * Enhanced Islands Bootstrap with Dash/Interact Coordination
 * High-End OR Edition with perioperative system capabilities
 */

class SurgeIslandsBridge {
    constructor() {
        this.mountedIslands = new Map();
        this.islandComponents = new Map();
        this.eventBus = new EventTarget();
        this.sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        this.projectCoordination = {
            dash: new Map(),
            interact: new Map()
        };
        // OR-specific state management
        this.orState = {
            activeCases: new Map(),
            preferences: new Map(),
            instruments: new Map(),
            anesthesiaRecords: new Map(),
            checklists: new Map(),
            imagingAssets: new Map()
        };
        this.setupProjectCoordination();
        this.setupHighEndCoordination();
        
        // Setup online/offline sync handling
        window.addEventListener('online', () => this.processSyncQueue());
        window.addEventListener('offline', () => console.log('Offline mode - queuing updates'));
    }
            checklists: new Map()
        };
        this.setupProjectCoordination();
        this.setupORCoordination();
        this.setupHighEndCoordination();
    }

    // Setup coordination with existing Dash and Interact projects
    setupProjectCoordination() {
        // Dash project coordination - Analytics & Reporting
        window.addEventListener('dash:stateChange', (event) => {
            this.coordinateDashState(event.detail);
        });
        
        window.addEventListener('dash:action', (event) => {
            this.forwardDashAction(event.detail);
        });
        
        // Interact project coordination - Intra-op Tools
        window.addEventListener('interact:stateChange', (event) => {
            this.coordinateInteractState(event.detail);
        });
        
        window.addEventListener('interact:action', (event) => {
            this.forwardInteractAction(event.detail);
        });
        
        // Unified platform events
        window.addEventListener('surge:projectUpdate', (event) => {
            this.handleProjectUpdate(event.detail);
        });
    }

    // Setup OR-specific coordination for high-end features
    setupORCoordination() {
        // Case management events
        window.addEventListener('case:statusChange', (event) => {
            this.handleCaseStatusChange(event.detail);
        });

        // Instrument tracking events
        window.addEventListener('instrument:count', (event) => {
            this.handleInstrumentCount(event.detail);
        });

        // Anesthesia record events
        window.addEventListener('anesthesia:vital', (event) => {
            this.handleAnesthesiaVital(event.detail);
        });

        // Checklist events
        window.addEventListener('checklist:step', (event) => {
            this.handleChecklistStep(event.detail);
        });

        // Preference card events
        window.addEventListener('preference:update', (event) => {
            this.handlePreferenceUpdate(event.detail);
        });

        // PACS/DICOM events
        window.addEventListener('imaging:update', (event) => {
            this.handleImagingUpdate(event.detail);
        });

        // Telementoring events
        window.addEventListener('telementor:session', (event) => {
            this.handleTelementorSession(event.detail);
        });
    }

    // Enhanced coordination for high-end OR features
    setupHighEndCoordination() {
        // OR Board coordination
        window.addEventListener('orboard:state', (event) => {
            this.coordinateORBoardState(event.detail);
        });
        
        window.addEventListener('orboard:room_selected', (event) => {
            this.handleRoomSelection(event.detail);
        });
        
        window.addEventListener('orboard:case_update', (event) => {
            this.handleCaseUpdate(event.detail);
        });

        // Instrument tracking coordination
        window.addEventListener('instruments:count_update', (event) => {
            this.coordinateInstrumentCount(event.detail);
        });

        // Anesthesia record coordination
        window.addEventListener('anesthesia:vital_update', (event) => {
            this.coordinateVitals(event.detail);
        });

        // Checklist coordination
        window.addEventListener('checklist:item_update', (event) => {
            this.coordinateChecklist(event.detail);
        });

        // Safety alerts coordination
        window.addEventListener('safety:alert', (event) => {
            this.coordinateSafetyAlert(event.detail);
        });
    }

    // Coordinate OR Board state across islands
    coordinateORBoardState(state) {
        const { rooms } = state;
        
        // Update Dash analytics with current OR status
        this.eventBus.dispatchEvent(new CustomEvent('dash:or_state_update', {
            detail: { rooms, timestamp: Date.now() }
        }));
        
        // Update Interact workflows with active cases
        const activeCases = rooms.filter(r => r.caseId).map(r => ({
            roomId: r.id,
            caseId: r.caseId,
            status: r.status,
            phase: r.phase
        }));
        
        this.eventBus.dispatchEvent(new CustomEvent('interact:active_cases_update', {
            detail: { activeCases, timestamp: Date.now() }
        }));
    }

    // Handle room selection for cross-island focus
    handleRoomSelection(selection) {
        const { roomId, caseId, room } = selection;
        
        // Notify all islands about the selected room/case
        this.broadcastToIslands('focus_case', {
            roomId,
            caseId,
            room,
            timestamp: Date.now()
        });
    }

    // Handle case updates and propagate to relevant islands
    handleCaseUpdate(update) {
        const { caseId, roomId, phase, checklist, instruments, vitals } = update;
        
        // Update OR Board
        this.eventBus.dispatchEvent(new CustomEvent('orboard:sync_update', {
            detail: { caseId, roomId, phase, checklist, instruments, vitals }
        }));
        
        // Update Dash analytics
        this.eventBus.dispatchEvent(new CustomEvent('dash:case_metrics_update', {
            detail: { caseId, roomId, phase, checklist, instruments }
        }));
    }

    // Coordinate instrument counts across systems
    coordinateInstrumentCount(countData) {
        const { caseId, instrumentId, count, type, discrepancy } = countData;
        
        // Update OR Board instrument status
        this.eventBus.dispatchEvent(new CustomEvent('orboard:instrument_update', {
            detail: { caseId, instrumentId, count, type, discrepancy }
        }));
        
        // Update Dash safety metrics
        this.eventBus.dispatchEvent(new CustomEvent('dash:safety_metric_update', {
            detail: { 
                type: 'instrument_discrepancy', 
                caseId, 
                severity: discrepancy ? 'high' : 'low',
                count 
            }
        }));
    }

    // Coordinate vital signs updates
    coordinateVitals(vitalsData) {
        const { caseId, vitals, alerts } = vitalsData;
        
        // Update OR Board vital display
        this.eventBus.dispatchEvent(new CustomEvent('orboard:vitals_update', {
            detail: { caseId, vitals }
        }));
        
        // Update Dash monitoring metrics
        this.eventBus.dispatchEvent(new CustomEvent('dash:vitals_trend_update', {
            detail: { caseId, vitals, alerts }
        }));
        
        // If there are critical alerts, notify all islands
        if (alerts && alerts.length > 0) {
            this.broadcastToIslands('critical_alert', {
                caseId,
                alerts,
                timestamp: Date.now()
            });
        }
    }

    // Coordinate checklist updates
    coordinateChecklist(checklistData) {
        const { caseId, itemId, completed, role, signature } = checklistData;
        
        // Update OR Board checklist progress
        this.eventBus.dispatchEvent(new CustomEvent('orboard:checklist_update', {
            detail: { caseId, itemId, completed, role, signature }
        }));
        
        // Update Dash compliance metrics
        this.eventBus.dispatchEvent(new CustomEvent('dash:compliance_update', {
            detail: { 
                type: 'checklist_completion',
                caseId,
                completed,
                role
            }
        }));
    }

    // Coordinate safety alerts across all islands
    coordinateSafetyAlert(alertData) {
        const { type, severity, caseId, roomId, message, requiresAction } = alertData;
        
        // High-priority broadcast to all islands
        this.broadcastToIslands('safety_alert', {
            type,
            severity,
            caseId,
            roomId,
            message,
            requiresAction,
            timestamp: Date.now()
        });
        
        // Log to audit trail
        this.logAuditEvent('safety_alert', {
            type,
            severity,
            caseId,
            roomId,
            message
        });
    }

    // Enhanced component loading with project awareness and OR capabilities
    async loadIslandComponent(islandType, componentName, projectContext = null) {
        const key = `${islandType}:${componentName}`;
        
        if (this.islandComponents.has(key)) {
            return this.islandComponents.get(key);
        }

        let component;
        
        try {
            switch (islandType) {
                case 'dash':
                    // Analytics & Reporting Island
                    const { default: DashAdapter } = await import('/static/islands/DashAdapter.js');
                    component = DashAdapter;
                    this.projectCoordination.dash.set(componentName, key);
                    break;
                    
                case 'interact':
                    // Intra-op Tools Island
                    const { default: InteractAdapter } = await import('/static/islands/InteractAdapter.js');
                    component = InteractAdapter;
                    this.projectCoordination.interact.set(componentName, key);
                    break;
                    
                case 'calendar':
                    // OR Scheduling Calendar
                    const { default: Calendar } = await import('/static/islands/unified/Calendar.js');
                    component = Calendar;
                    break;
                    
                case 'or-board':
                    // Live OR Board
                    const { default: ORBoard } = await import('/static/islands/unified/ORBoard.js');
                    component = ORBoard;
                    break;
                    
                case 'consent':
                    // E-Sign Consent Pad
                    const { default: ConsentPad } = await import('/static/islands/unified/ConsentPad.js');
                    component = ConsentPad;
                    break;

                case 'pacs':
                    // PACS/DICOM Mini-Viewer
                    const { default: PACSViewer } = await import('/static/islands/unified/PACSViewer.js');
                    component = PACSViewer;
                    break;

                case 'risk-calc':
                    // Risk Calculator
                    const { default: RiskCalc } = await import('/static/islands/unified/RiskCalc.js');
                    component = RiskCalc;
                    break;

                case 'telementor':
                    // Telementoring Widget
                    const { default: Telementor } = await import('/static/islands/unified/Telementor.js');
                    component = Telementor;
                    break;
                    
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

    // OR-specific event handlers
    handleCaseStatusChange(detail) {
        const { caseId, status, timestamp } = detail;
        this.orState.activeCases.set(caseId, { status, timestamp });
        
        // Broadcast to relevant islands
        this.broadcastToIslands('case:statusChange', detail, ['or-board', 'dash', 'interact']);
        
        // Update HTMX components
        this.updateHTMXComponent('#case-status-' + caseId, { status });
    }

    handleInstrumentCount(detail) {
        const { caseId, instrumentId, count, type } = detail;
        const key = `${caseId}-${instrumentId}`;
        this.orState.instruments.set(key, { count, type, timestamp: Date.now() });
        
        // Broadcast to interact islands for real-time updates
        this.broadcastToIslands('instrument:count', detail, ['interact']);
    }

    handleAnesthesiaVital(detail) {
        const { caseId, vital, value, timestamp } = detail;
        if (!this.orState.anesthesiaRecords.has(caseId)) {
            this.orState.anesthesiaRecords.set(caseId, { vitals: [] });
        }
        
        const record = this.orState.anesthesiaRecords.get(caseId);
        record.vitals.push({ vital, value, timestamp });
        
        // Broadcast to dash for analytics
        this.broadcastToIslands('anesthesia:vital', detail, ['dash']);
    }

    handleChecklistStep(detail) {
        const { caseId, checklistId, stepId, completed, signature } = detail;
        const key = `${caseId}-${checklistId}`;
        if (!this.orState.checklists.has(key)) {
            this.orState.checklists.set(key, { steps: new Map() });
        }
        
        const checklist = this.orState.checklists.get(key);
        checklist.steps.set(stepId, { completed, signature, timestamp: Date.now() });
        
        // Broadcast to interact islands
        this.broadcastToIslands('checklist:step', detail, ['interact']);
    }

    // Utility methods for OR coordination
    broadcastToIslands(eventType, data, islandTypes) {
        this.mountedIslands.forEach((island, islandId) => {
            if (islandTypes.includes(island.projectType)) {
                this.emitToIsland(islandId, eventType, data);
            }
        });
    }

    updateHTMXComponent(selector, data) {
        const element = document.querySelector(selector);
        if (element) {
            // Trigger HTMX update with new data
            htmx.trigger(element, 'island:update', data);
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
