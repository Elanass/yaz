/**
 * Surgery Analyzer Module
 * 
 * This module provides client-side functionality for the surgery analyzer dashboard,
 * handling form dynamics, surgery type-specific fields, and visualization of analysis results.
 * 
 * Features:
 * - Dynamic form field management based on surgery type
 * - Protocol information loading
 * - Analysis results visualization with charts
 * - Offline-first capabilities with data caching
 */

class SurgeryAnalyzer {
    constructor() {
        this.apiEndpoint = '/api/v1/surgery/analyze';
        this.protocolEndpoint = '/api/v1/surgery/protocols/';
        this.initializeEventListeners();
        this.initializeOfflineSupport();
    }
    
    /**
     * Initialize all event listeners for the surgery analyzer dashboard
     */
    initializeEventListeners() {
        // Surgery type change handler
        document.getElementById('surgery_type')?.addEventListener('change', (e) => {
            this.handleSurgeryTypeChange(e.target.value);
        });
        
        // Form submission
        document.getElementById('surgery-case-form')?.addEventListener('submit', (e) => {
            // HTMX will handle the actual submission
            // This is for any pre-processing needed
            this.prepareFormData();
        });
        
        // Toggle buttons for collapsible sections
        document.querySelectorAll('.btn-toggle').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const targetId = e.target.getAttribute('data-target');
                const targetSection = document.getElementById(targetId);
                if (targetSection) {
                    targetSection.classList.toggle('collapsed');
                }
            });
        });
    }
    
    /**
     * Initialize offline support with service worker and caching
     */
    initializeOfflineSupport() {
        // Check if browser supports service workers
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('Service Worker registered with scope:', registration.scope);
                })
                .catch(error => {
                    console.error('Service Worker registration failed:', error);
                });
        }
        
        // Initialize local cache for form data
        this.setupFormCaching();
    }
    
    /**
     * Handle changes to the surgery type selection
     */
    handleSurgeryTypeChange(surgeryType) {
        // Hide all surgery-specific sections
        document.querySelectorAll('.surgery-specific-section').forEach(section => {
            section.style.display = 'none';
        });
        
        // Show the appropriate section based on surgery type
        if (surgeryType === 'gastric_flot') {
            document.getElementById('flot-section').style.display = 'block';
        }
        
        // Load protocol information
        this.loadProtocolInfo(surgeryType);
    }
    
    /**
     * Load protocol information for the selected surgery type
     */
    async loadProtocolInfo(surgeryType) {
        if (!surgeryType) return;
        
        const protocolInfoSection = document.getElementById('protocol-info');
        
        try {
            // HTMX will handle this, but as fallback we implement direct fetch
            if (!window.htmx) {
                protocolInfoSection.innerHTML = '<div class="loading">Loading protocol information...</div>';
                
                const response = await fetch(`${this.protocolEndpoint}${surgeryType}`);
                const data = await response.json();
                
                this.renderProtocolInfo(data, protocolInfoSection);
            }
        } catch (error) {
            // Handle offline case
            protocolInfoSection.innerHTML = '<div class="error">Could not load protocol information. Working offline.</div>';
            
            // Try to load from cache
            const cachedProtocol = this.getCachedProtocol(surgeryType);
            if (cachedProtocol) {
                this.renderProtocolInfo(cachedProtocol, protocolInfoSection);
            }
        }
    }
    
    /**
     * Render protocol information in the UI
     */
    renderProtocolInfo(data, container) {
        // Save to cache for offline use
        this.cacheProtocolInfo(data.surgery_type, data);
        
        // Create protocol info HTML
        const protocol = data.protocol_information || {};
        const html = `
            <div class="protocol-info">
                <h3>${protocol.recommended_protocol || 'Protocol Information'}</h3>
                <ul class="protocol-elements">
                    ${protocol.protocol_elements?.map(element => `<li>${element}</li>`).join('') || ''}
                </ul>
                ${protocol.contraindications?.length ? `
                    <div class="contraindications">
                        <h4>Contraindications</h4>
                        <ul>
                            ${protocol.contraindications.map(item => `<li>${item}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
        
        container.innerHTML = html;
    }
    
    /**
     * Prepare form data before submission
     */
    prepareFormData() {
        // Convert JSON string fields to objects
        const labValuesField = document.getElementById('lab_values');
        if (labValuesField && labValuesField.value) {
            try {
                // Validate JSON
                JSON.parse(labValuesField.value);
            } catch (e) {
                // If invalid JSON, display error
                alert('Lab values must be in valid JSON format');
                return false;
            }
        }
        
        // Save form data to local storage for offline recovery
        this.saveFormToCache();
        
        return true;
    }
    
    /**
     * Save form data to cache for offline recovery
     */
    saveFormToCache() {
        const form = document.getElementById('surgery-case-form');
        if (!form) return;
        
        const formData = new FormData(form);
        const formObject = {};
        
        for (const [key, value] of formData.entries()) {
            formObject[key] = value;
        }
        
        localStorage.setItem('surgery_analyzer_last_form', JSON.stringify(formObject));
    }
    
    /**
     * Setup form caching and recovery
     */
    setupFormCaching() {
        // Recover form data if available
        try {
            const savedForm = localStorage.getItem('surgery_analyzer_last_form');
            if (savedForm) {
                const formData = JSON.parse(savedForm);
                this.recoverFormData(formData);
            }
        } catch (e) {
            console.error('Error recovering form data', e);
        }
    }
    
    /**
     * Recover form data from cache
     */
    recoverFormData(formData) {
        const form = document.getElementById('surgery-case-form');
        if (!form) return;
        
        // Populate form fields from saved data
        Object.keys(formData).forEach(key => {
            const field = form.elements[key];
            if (field) {
                if (field.type === 'checkbox') {
                    field.checked = formData[key] === 'on';
                } else {
                    field.value = formData[key];
                }
            }
        });
        
        // Trigger surgery type change to show appropriate fields
        if (formData.surgery_type) {
            this.handleSurgeryTypeChange(formData.surgery_type);
        }
    }
    
    /**
     * Cache protocol information for offline use
     */
    cacheProtocolInfo(surgeryType, data) {
        try {
            localStorage.setItem(`protocol_${surgeryType}`, JSON.stringify(data));
        } catch (e) {
            console.error('Error caching protocol data', e);
        }
    }
    
    /**
     * Get cached protocol information
     */
    getCachedProtocol(surgeryType) {
        try {
            const cached = localStorage.getItem(`protocol_${surgeryType}`);
            return cached ? JSON.parse(cached) : null;
        } catch (e) {
            console.error('Error retrieving cached protocol', e);
            return null;
        }
    }
}

// Initialize the surgery analyzer when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const surgeryAnalyzer = new SurgeryAnalyzer();
});

// Register for offline usage
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').then(registration => {
            console.log('ServiceWorker registration successful');
        }).catch(err => {
            console.log('ServiceWorker registration failed: ', err);
        });
    });
}
