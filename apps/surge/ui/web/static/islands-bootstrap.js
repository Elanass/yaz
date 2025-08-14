/**
 * Islands Bootstrap - React Islands Integration for Surgery PWA
 * Manages mounting and updating React islands within FastHTML pages
 */

class IslandsManager {
    constructor() {
        this.islands = new Map();
        this.eventListeners = new Map();
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.mountIslands());
        } else {
            this.mountIslands();
        }

        // Listen for HTMX events
        document.addEventListener('htmx:afterSettle', () => this.mountIslands());
        
        // Listen for island update events from HTMX
        window.addEventListener('island:update', (event) => this.updateIsland(event.detail));
        
        // Listen for React events to trigger HTMX updates
        window.addEventListener('react:update', (event) => this.triggerHTMXUpdate(event.detail));
    }

    mountIslands() {
        // Find all island mount points
        const islandElements = document.querySelectorAll('[data-island]');
        
        islandElements.forEach(element => {
            const islandType = element.dataset.island;
            const islandId = element.id;
            
            // Skip if already mounted
            if (this.islands.has(islandId)) {
                return;
            }

            // Get props from JSON script tag
            const propsScript = document.getElementById(`island-props-${islandId.replace('island-', '')}`);
            let props = {};
            
            if (propsScript) {
                try {
                    props = JSON.parse(propsScript.textContent);
                } catch (error) {
                    console.warn(`Failed to parse props for island ${islandId}:`, error);
                }
            }

            // Mount the island
            this.mountIsland(element, islandType, props);
        });
    }

    async mountIsland(element, islandType, props = {}) {
        try {
            // Dynamically import the island component
            const island = await this.loadIslandComponent(islandType);
            
            if (island && island.mount) {
                // Mount the React component
                island.mount(element, {
                    ...props,
                    onUpdate: (data) => this.handleIslandUpdate(element.id, data),
                    onTrigger: (eventName, data) => this.triggerHTMXUpdate({ eventName, data })
                });
                
                this.islands.set(element.id, { island, element, props });
                console.log(`Mounted island: ${islandType} at #${element.id}`);
            }
        } catch (error) {
            console.error(`Failed to mount island ${islandType}:`, error);
            // Show fallback content
            this.showFallback(element, islandType);
        }
    }

    async loadIslandComponent(islandType) {
        // Map island types to their modules
        const islandModules = {
            'Calendar': () => import('./islands/Calendar.js'),
            'ORBoard': () => import('./islands/ORBoard.js'),
            'ConsentPad': () => import('./islands/ConsentPad.js'),
            'RiskCalculator': () => import('./islands/RiskCalculator.js'),
            'ImagingViewer': () => import('./islands/ImagingViewer.js'),
            'ChecklistManager': () => import('./islands/ChecklistManager.js'),
            'PatientForm': () => import('./islands/PatientForm.js'),
            'dash': () => import('./islands/DashAdapter.js'),
            'interact': () => import('./islands/InteractAdapter.js')
        };

        const moduleLoader = islandModules[islandType];
        if (!moduleLoader) {
            throw new Error(`Unknown island type: ${islandType}`);
        }

        const module = await moduleLoader();
        return module.default || module;
    }

    updateIsland(detail) {
        const { id, props } = detail;
        const islandData = this.islands.get(id);
        
        if (islandData && islandData.island.update) {
            islandData.island.update(props);
            console.log(`Updated island: ${id}`, props);
        }
    }

    handleIslandUpdate(islandId, data) {
        // Island is reporting a state change
        console.log(`Island ${islandId} updated:`, data);
        
        // Trigger custom event for HTMX to potentially react to
        window.dispatchEvent(new CustomEvent('island:change', {
            detail: { islandId, data }
        }));
    }

    triggerHTMXUpdate(detail) {
        const { eventName, data } = detail;
        
        // Use HTMX to trigger server updates
        if (window.htmx) {
            window.htmx.trigger(document.body, eventName, data);
        }
        
        console.log(`Triggered HTMX event: ${eventName}`, data);
    }

    showFallback(element, islandType) {
        element.innerHTML = `
            <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <h3 class="text-sm font-medium text-yellow-800">
                            Component Loading Failed
                        </h3>
                        <div class="mt-2 text-sm text-yellow-700">
                            <p>Unable to load ${islandType} component. Please refresh the page.</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Offline handling
    handleOffline() {
        document.getElementById('offline-indicator')?.classList.remove('hidden');
        
        // Notify all islands about offline state
        this.islands.forEach((islandData, id) => {
            if (islandData.island.handleOffline) {
                islandData.island.handleOffline();
            }
        });
    }

    handleOnline() {
        document.getElementById('offline-indicator')?.classList.add('hidden');
        
        // Notify all islands about online state
        this.islands.forEach((islandData, id) => {
            if (islandData.island.handleOnline) {
                islandData.island.handleOnline();
            }
        });
    }
}

// Initialize islands manager
const islandsManager = new IslandsManager();

// Handle online/offline events
window.addEventListener('offline', () => islandsManager.handleOffline());
window.addEventListener('online', () => islandsManager.handleOnline());

// Export for external use
window.IslandsManager = islandsManager;

export default islandsManager;
