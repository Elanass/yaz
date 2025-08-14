/**
 * DomainSelector Component
 * A reusable domain selection dropdown component with htmx support
 */

class DomainSelector {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            domains: options.domains || ['Gastric Surgery', 'Oncology', 'Pathology', 'Radiology'],
            selectedDomain: options.selectedDomain || null,
            placeholder: options.placeholder || 'Select a domain...',
            onSelect: options.onSelect || null,
            htmxEndpoint: options.htmxEndpoint || null,
            className: options.className || 'w-full',
            ...options
        };
        this.isOpen = false;
    }

    render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container with id "${this.containerId}" not found`);
            return;
        }

        const html = `
            <div class="domain-selector relative ${this.options.className}" data-component="domain-selector">
                <button 
                    type="button" 
                    class="domain-selector-trigger w-full bg-white border border-gray-300 rounded-lg px-4 py-3 text-left shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 hover:border-gray-400 transition-colors"
                    aria-haspopup="listbox"
                    aria-expanded="false"
                >
                    <span class="domain-selector-text text-gray-700">
                        ${this.options.selectedDomain || this.options.placeholder}
                    </span>
                    <span class="domain-selector-icon absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                        <svg class="w-5 h-5 text-gray-400 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                        </svg>
                    </span>
                </button>
                
                <div class="domain-selector-dropdown absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg opacity-0 scale-95 transform transition-all duration-200 origin-top hidden">
                    <ul class="py-2 max-h-60 overflow-auto" role="listbox">
                        ${this.options.domains.map(domain => `
                            <li>
                                <button 
                                    type="button"
                                    class="domain-option w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors ${domain === this.options.selectedDomain ? 'bg-blue-50 text-blue-600' : ''}"
                                    role="option"
                                    data-value="${domain}"
                                    ${this.options.htmxEndpoint ? `hx-post="${this.options.htmxEndpoint}" hx-vals='{"domain": "${domain}"}'` : ''}
                                >
                                    <span class="flex items-center justify-between">
                                        ${domain}
                                        ${domain === this.options.selectedDomain ? '<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>' : ''}
                                    </span>
                                </button>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        `;

        container.innerHTML = html;
        this.attachEventListeners();
    }

    attachEventListeners() {
        const container = document.getElementById(this.containerId);
        const trigger = container.querySelector('.domain-selector-trigger');
        const dropdown = container.querySelector('.domain-selector-dropdown');
        const options = container.querySelectorAll('.domain-option');
        const icon = container.querySelector('.domain-selector-icon svg');

        // Toggle dropdown
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggle();
        });

        // Handle option selection
        options.forEach(option => {
            option.addEventListener('click', (e) => {
                const value = e.currentTarget.dataset.value;
                this.select(value);
            });
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!container.contains(e.target)) {
                this.close();
            }
        });

        // Keyboard navigation
        container.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.close();
            }
        });
    }

    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    open() {
        const container = document.getElementById(this.containerId);
        const dropdown = container.querySelector('.domain-selector-dropdown');
        const icon = container.querySelector('.domain-selector-icon svg');
        const trigger = container.querySelector('.domain-selector-trigger');

        dropdown.classList.remove('hidden', 'opacity-0', 'scale-95');
        dropdown.classList.add('opacity-100', 'scale-100');
        icon.classList.add('rotate-180');
        trigger.setAttribute('aria-expanded', 'true');
        this.isOpen = true;
    }

    close() {
        const container = document.getElementById(this.containerId);
        const dropdown = container.querySelector('.domain-selector-dropdown');
        const icon = container.querySelector('.domain-selector-icon svg');
        const trigger = container.querySelector('.domain-selector-trigger');

        dropdown.classList.add('opacity-0', 'scale-95');
        dropdown.classList.remove('opacity-100', 'scale-100');
        icon.classList.remove('rotate-180');
        trigger.setAttribute('aria-expanded', 'false');
        
        setTimeout(() => {
            dropdown.classList.add('hidden');
        }, 200);
        
        this.isOpen = false;
    }

    select(value) {
        const container = document.getElementById(this.containerId);
        const text = container.querySelector('.domain-selector-text');
        
        this.options.selectedDomain = value;
        text.textContent = value;
        text.classList.remove('text-gray-500');
        text.classList.add('text-gray-700');
        
        // Update active state
        const options = container.querySelectorAll('.domain-option');
        options.forEach(option => {
            const isSelected = option.dataset.value === value;
            option.classList.toggle('bg-blue-50', isSelected);
            option.classList.toggle('text-blue-600', isSelected);
            
            const checkIcon = option.querySelector('svg');
            if (checkIcon) {
                checkIcon.style.display = isSelected ? 'block' : 'none';
            }
        });

        this.close();

        // Call custom callback
        if (this.options.onSelect) {
            this.options.onSelect(value);
        }

        // Dispatch custom event
        container.dispatchEvent(new CustomEvent('domainSelected', {
            detail: { domain: value },
            bubbles: true
        }));
    }

    setValue(value) {
        if (this.options.domains.includes(value)) {
            this.select(value);
        }
    }

    getValue() {
        return this.options.selectedDomain;
    }
}

// HTMX integration
document.addEventListener('htmx:afterRequest', function(event) {
    const domainSelectors = document.querySelectorAll('[data-component="domain-selector"]');
    domainSelectors.forEach(selector => {
        // Re-initialize component after HTMX requests if needed
        if (event.detail.target.contains(selector)) {
            // Component will maintain its state
        }
    });
});

// Export for module usage
window.DomainSelector = DomainSelector;
