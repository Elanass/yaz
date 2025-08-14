/**
 * Islands Bootstrap - Surgery Platform
 * Coordinates FastHTML + HTMX with React Islands (Dash/Interact)
 */

class IslandsBridge {
    constructor() {
        this.mountedIslands = new Map();
        this.islandComponents = new Map();
        this.eventBus = new EventTarget();
    }

    async loadIslandComponent(islandType, componentName) {
        const key = `${islandType}:${componentName}`;
        
        if (this.islandComponents.has(key)) {
            return this.islandComponents.get(key);
        }

        let component;
        
        switch (islandType) {
            case 'dash':
                const { DashApp } = await import('/islands/DashAdapter.js');
                component = DashApp;
                break;
                
            case 'interact':
                const { InteractApp } = await import('/islands/InteractAdapter.js');
                component = InteractApp;
                break;
                
            case 'calendar':
                const { Calendar } = await import('/islands/unified/Calendar.js');
                component = Calendar;
                break;
                
            case 'or-board':
                const { ORBoard } = await import('/islands/unified/ORBoard.js');
                component = ORBoard;
                break;
                
            case 'consent':
                const { ConsentPad } = await import('/islands/unified/ConsentPad.js');
                component = ConsentPad;
                break;
                
            default:
                console.warn(`Unknown island type: ${islandType}`);
                return null;
        }
        
        this.islandComponents.set(key, component);
        return component;
    }

    async mountIsland(container, config) {
        const { type, component, props = {} } = config;
        const islandId = container.getAttribute('data-island-id') || `island-${Date.now()}`;
        
        try {
            const Component = await this.loadIslandComponent(type, component);
            if (!Component) return;

            // Mount the React component
            const { createRoot } = await import('https://esm.sh/react-dom@18/client');
            const { createElement } = await import('https://esm.sh/react@18');
            
            const root = createRoot(container);
            const element = createElement(Component, {
                ...props,
                islandId,
                onUpdate: (data) => this.handleIslandUpdate(islandId, data),
                onNavigate: (path) => this.handleNavigation(path)
            });
            
            root.render(element);
            
            this.mountedIslands.set(islandId, {
                root,
                config,
                container
            });
            
            container.setAttribute('data-island-mounted', 'true');
            console.log(`Mounted island: ${type}:${component || 'default'} (${islandId})`);
            
        } catch (error) {
            console.error(`Failed to mount island ${type}:`, error);
            container.innerHTML = `<div class="error">Failed to load ${type} component</div>`;
        }
    }

    handleIslandUpdate(islandId, data) {
        // React island wants to update HTMX content
        this.eventBus.dispatchEvent(new CustomEvent('island:update', {
            detail: { islandId, data }
        }));
        
        // Trigger HTMX update if endpoint specified
        if (data.endpoint) {
            window.dispatchEvent(new CustomEvent('react:update', {
                detail: {
                    endpoint: data.endpoint,
                    data: data.payload,
                    target: data.target
                }
            }));
        }
    }

    handleNavigation(path) {
        // Use HTMX for navigation to maintain server-side rendering
        if (path.startsWith('/')) {
            htmx.ajax('GET', path, { target: 'body', swap: 'outerHTML' });
        } else {
            window.location.href = path;
        }
    }

    async scanForNewIslands(container = document) {
        const islandContainers = container.querySelectorAll('[data-island]:not([data-island-mounted])');
        
        for (const islandContainer of islandContainers) {
            const islandType = islandContainer.getAttribute('data-island');
            const propsScript = islandContainer.querySelector('script[type="application/json"]');
            const props = propsScript ? JSON.parse(propsScript.textContent) : {};
            
            await this.mountIsland(islandContainer, {
                type: islandType,
                component: props.component,
                props: props.props || {}
            });
        }
    }

    updateIslandProps(islandId, newProps) {
        const island = this.mountedIslands.get(islandId);
        if (island) {
            // Re-render with new props
            const { createElement } = window.React;
            const Component = island.config.component;
            
            island.root.render(createElement(Component, {
                ...newProps,
                islandId,
                onUpdate: (data) => this.handleIslandUpdate(islandId, data),
                onNavigate: (path) => this.handleNavigation(path)
            }));
        }
    }
}

// Global islands bridge instance
window.islandsBridge = new IslandsBridge();

// Initialize function called from templates
export async function initializeIslands(islandsConfig) {
    console.log('Initializing islands:', islandsConfig);
    
    // Scan for islands in the DOM
    await window.islandsBridge.scanForNewIslands();
    
    // Listen for HTMX events
    document.addEventListener('htmx:afterSwap', async (event) => {
        await window.islandsBridge.scanForNewIslands(event.detail.target);
    });
    
    // Listen for island update events
    window.islandsBridge.eventBus.addEventListener('island:update', (event) => {
        console.log('Island update:', event.detail);
    });
}

// Make available globally
window.initializeIslands = initializeIslands;
