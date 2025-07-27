/**
 * Gastric ADCI Platform - Main Application JavaScript
 * Handles PWA functionality, HTMX interactions, and UI enhancements
 */

// Application state
window.GastricADCI = {
    version: '1.0.0',
    isOnline: navigator.onLine,
    isInstalled: false,
    user: null,
    config: {
        apiBaseUrl: '/api/v1',
        wsUrl: 'ws://localhost:8000/ws',
        debugMode: window.location.hostname === 'localhost'
    }
};

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializePWA();
    initializeHTMX();
    initializeOfflineDetection();
    initializeNotifications();
    initializeKeyboardShortcuts();
    
    console.log('Gastric ADCI Platform initialized');
    
    // Initialize cohort management if on cohort pages
    if (window.location.pathname.includes('/cohorts')) {
        initializeCohortManagement();
    }
});

/**
 * PWA Functionality
 */
function initializePWA() {
    // Register service worker
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered:', registration);
                
                // Check for updates
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            showUpdateAvailableNotification();
                        }
                    });
                });
            })
            .catch(error => {
                console.error('SW registration failed:', error);
            });
    }
    
    // Handle PWA install prompt
    let deferredPrompt;
    
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        showInstallPrompt();
    });
    
    // Install button handler
    const installButton = document.getElementById('pwa-install-button');
    if (installButton) {
        installButton.addEventListener('click', async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                
                if (outcome === 'accepted') {
                    console.log('PWA installation accepted');
                    hideInstallPrompt();
                } else {
                    console.log('PWA installation declined');
                }
                
                deferredPrompt = null;
            }
        });
    }
    
    // Detect if app is installed
    window.addEventListener('appinstalled', () => {
        console.log('PWA installed successfully');
        window.GastricADCI.isInstalled = true;
        hideInstallPrompt();
        showNotification('App installed successfully!', 'success');
    });
    
    // Detect standalone mode
    if (window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone) {
        window.GastricADCI.isInstalled = true;
        document.body.classList.add('pwa-standalone');
    }
}

function showInstallPrompt() {
    const prompt = document.getElementById('pwa-install-prompt');
    if (prompt) {
        prompt.style.display = 'block';
        setTimeout(() => prompt.classList.add('visible'), 100);
    }
}

function hideInstallPrompt() {
    const prompt = document.getElementById('pwa-install-prompt');
    if (prompt) {
        prompt.classList.remove('visible');
        setTimeout(() => prompt.style.display = 'none', 300);
    }
}

function showUpdateAvailableNotification() {
    showNotification(
        'A new version is available. Please refresh to update.',
        'info',
        {
            action: 'Refresh',
            handler: () => window.location.reload()
        }
    );
}

/**
 * HTMX Enhancements
 */
function initializeHTMX() {
    // Global HTMX configuration
    htmx.config.timeout = 30000; // 30 second timeout
    htmx.config.retryCount = 3;
    htmx.config.retryDelay = 1000;
    
    // Add loading indicators
    document.body.addEventListener('htmx:beforeRequest', function(evt) {
        const target = evt.target;
        showLoadingState(target);
        
        // Add authentication header if user is logged in
        if (window.GastricADCI.user) {
            evt.detail.headers['Authorization'] = `Bearer ${window.GastricADCI.user.token}`;
        }
    });
    
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        const target = evt.target;
        hideLoadingState(target);
        
        // Handle authentication errors
        if (evt.detail.xhr.status === 401) {
            handleAuthenticationError();
        }
        
        // Handle network errors
        if (evt.detail.xhr.status === 0) {
            showNetworkErrorNotification();
        }
    });
    
    // Handle response errors
    document.body.addEventListener('htmx:responseError', function(evt) {
        console.error('HTMX Response Error:', evt.detail);
        showNotification('Request failed. Please try again.', 'error');
    });
    
    // Handle network errors
    document.body.addEventListener('htmx:sendError', function(evt) {
        console.error('HTMX Send Error:', evt.detail);
        
        if (!navigator.onLine) {
            showNotification('You are offline. Changes will be synced when connection is restored.', 'warning');
            // Store request for later sync
            storeOfflineRequest(evt.detail);
        } else {
            showNotification('Network error. Please check your connection.', 'error');
        }
    });
}

function showLoadingState(element) {
    element.classList.add('htmx-request');
    
    // Add spinner for buttons
    if (element.tagName === 'BUTTON') {
        const spinner = document.createElement('span');
        spinner.className = 'loading-spinner';
        spinner.setAttribute('data-loading', 'true');
        element.prepend(spinner);
        element.disabled = true;
    }
    
    // Add loading overlay for larger elements
    if (element.classList.contains('loading-overlay')) {
        const overlay = document.createElement('div');
        overlay.className = 'absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center';
        overlay.innerHTML = '<div class="loading-spinner"></div>';
        overlay.setAttribute('data-loading-overlay', 'true');
        element.style.position = 'relative';
        element.appendChild(overlay);
    }
}

function hideLoadingState(element) {
    element.classList.remove('htmx-request');
    
    // Remove spinner from buttons
    if (element.tagName === 'BUTTON') {
        const spinner = element.querySelector('[data-loading="true"]');
        if (spinner) {
            spinner.remove();
        }
        element.disabled = false;
    }
    
    // Remove loading overlay
    const overlay = element.querySelector('[data-loading-overlay="true"]');
    if (overlay) {
        overlay.remove();
    }
}

/**
 * Offline Detection and Handling
 */
function initializeOfflineDetection() {
    window.addEventListener('online', () => {
        window.GastricADCI.Utilities.showNotification('You are back online.', 'success');
    });

    window.addEventListener('offline', () => {
        window.GastricADCI.Utilities.showNotification('You are offline. Some features may be limited.', 'warning');
    });
    
    // Check initial connection state
    updateConnectionState();
}

function handleOnline() {
    console.log('Connection restored');
    window.GastricADCI.isOnline = true;
    updateConnectionState();
    
    // Sync offline data
    syncOfflineData();
    
    showNotification('Connection restored. Syncing data...', 'success');
}

function handleOffline() {
    console.log('Connection lost');
    window.GastricADCI.isOnline = false;
    updateConnectionState();
    
    showNotification('You are now offline. Some features may be limited.', 'warning');
}

function updateConnectionState() {
    const indicator = document.getElementById('offline-indicator');
    
    if (!navigator.onLine) {
        if (indicator) {
            indicator.classList.add('visible');
        }
        document.body.classList.add('offline');
    } else {
        if (indicator) {
            indicator.classList.remove('visible');
        }
        document.body.classList.remove('offline');
    }
}

/**
 * Offline Data Management
 */
function storeOfflineRequest(requestData) {
    if (!('indexedDB' in window)) return;
    
    const request = indexedDB.open('GastricADCI_OfflineDB', 1);
    
    request.onupgradeneeded = function(event) {
        const db = event.target.result;
        
        if (!db.objectStoreNames.contains('offlineRequests')) {
            const store = db.createObjectStore('offlineRequests', { keyPath: 'id', autoIncrement: true });
            store.createIndex('timestamp', 'timestamp', { unique: false });
            store.createIndex('type', 'type', { unique: false });
        }
    };
    
    request.onsuccess = function(event) {
        const db = event.target.result;
        const transaction = db.transaction(['offlineRequests'], 'readwrite');
        const store = transaction.objectStore('offlineRequests');
        
        const data = {
            url: requestData.url,
            method: requestData.method,
            headers: requestData.headers,
            body: requestData.body,
            timestamp: Date.now(),
            type: 'htmx-request'
        };
        
        store.add(data);
    };
}

window.GastricADCI.Utilities = {
    /**
     * Generic offline sync handler
     */
    async syncOfflineData(dbName, storeName, apiEndpoint) {
        const request = indexedDB.open(dbName, 1);

        request.onsuccess = function(event) {
            const db = event.target.result;
            const transaction = db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);

            const getAllRequest = store.getAll();

            getAllRequest.onsuccess = async function() {
                const items = getAllRequest.result;

                for (const item of items) {
                    try {
                        const response = await fetch(apiEndpoint, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(item),
                        });

                        if (response.ok) {
                            const deleteTransaction = db.transaction([storeName], 'readwrite');
                            const deleteStore = deleteTransaction.objectStore(storeName);
                            deleteStore.delete(item.id);
                        }
                    } catch (error) {
                        console.error('Failed to sync offline data:', error);
                    }
                }
            };
        };
    },

    /**
     * Notification utility
     */
    showNotification(message, type = 'info') {
        const notificationElement = document.createElement('div');
        notificationElement.className = `notification ${type}`;
        notificationElement.innerText = message;
        document.body.appendChild(notificationElement);

        setTimeout(() => {
            notificationElement.remove();
        }, 5000);
    },
};

/**
 * Notification System
 */
function initializeNotifications() {
    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission().then(permission => {
            console.log('Notification permission:', permission);
        });
    }
    
    // Create notification container if it doesn't exist
    if (!document.getElementById('notification-container')) {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'fixed top-4 right-4 z-50 space-y-2';
        document.body.appendChild(container);
    }
}

function showNotification(message, type = 'info', options = {}) {
    const container = document.getElementById('notification-container');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `notification max-w-sm bg-white border border-gray-200 rounded-lg shadow-lg p-4 transform transition-all duration-300 translate-x-full`;
    
    // Type-specific styling
    const typeClasses = {
        success: 'border-green-200 bg-green-50',
        error: 'border-red-200 bg-red-50',
        warning: 'border-yellow-200 bg-yellow-50',
        info: 'border-blue-200 bg-blue-50'
    };
    
    notification.className += ` ${typeClasses[type] || typeClasses.info}`;
    
    // Create icon
    const icon = document.createElement('div');
    icon.className = 'flex-shrink-0';
    
    const iconSvg = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };
    
    icon.textContent = iconSvg[type] || iconSvg.info;
    
    // Create content
    const content = document.createElement('div');
    content.className = 'ml-3 flex-1';
    content.textContent = message;
    
    // Create close button
    const closeButton = document.createElement('button');
    closeButton.className = 'ml-3 flex-shrink-0 text-gray-400 hover:text-gray-600';
    closeButton.innerHTML = '✕';
    closeButton.onclick = () => hideNotification(notification);
    
    // Create action button if provided
    if (options.action && options.handler) {
        const actionButton = document.createElement('button');
        actionButton.className = 'ml-3 text-blue-600 hover:text-blue-800 font-medium';
        actionButton.textContent = options.action;
        actionButton.onclick = () => {
            options.handler();
            hideNotification(notification);
        };
        content.appendChild(actionButton);
    }
    
    notification.appendChild(icon);
    notification.appendChild(content);
    notification.appendChild(closeButton);
    
    container.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
    }, 100);
    
    // Auto-hide after 5 seconds (unless it has an action)
    if (!options.action) {
        setTimeout(() => {
            hideNotification(notification);
        }, 5000);
    }
}

function hideNotification(notification) {
    notification.classList.add('translate-x-full');
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 300);
}

/**
 * Error Handlers
 */
function handleAuthenticationError() {
    window.GastricADCI.user = null;
    localStorage.removeItem('gastric_adci_user');
    
    showNotification('Your session has expired. Please log in again.', 'warning', {
        action: 'Login',
        handler: () => window.location.href = '/auth/login'
    });
}

function showNetworkErrorNotification() {
    if (!navigator.onLine) {
        showNotification('You appear to be offline. Please check your connection.', 'error');
    } else {
        showNotification('Network error occurred. Please try again.', 'error');
    }
}

/**
 * Keyboard Shortcuts
 */
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K: Global search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('[data-search="global"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Ctrl/Cmd + D: Open decision support
        if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
            e.preventDefault();
            if (window.GastricADCI.user && ['practitioner', 'researcher'].includes(window.GastricADCI.user.role)) {
                window.location.href = '/decision-support';
            }
        }
        
        // Ctrl/Cmd + P: Open protocols
        if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
            e.preventDefault();
            if (window.GastricADCI.user) {
                window.location.href = '/protocols';
            }
        }
        
        // Escape: Close modals/dropdowns
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('[data-modal="true"][style*="block"]');
            modals.forEach(modal => {
                modal.style.display = 'none';
            });
            
            const dropdowns = document.querySelectorAll('[data-dropdown="true"].visible');
            dropdowns.forEach(dropdown => {
                dropdown.classList.remove('visible');
            });
        }
    });
}

/**
 * Clinical Decision Support Utilities
 */
window.GastricADCI.DecisionSupport = {
    /**
     * Calculate confidence level from score
     */
    getConfidenceLevel(score) {
        if (score >= 0.85) return 'very-high';
        if (score >= 0.7) return 'high';
        if (score >= 0.5) return 'medium';
        return 'low';
    },
    
    /**
     * Format confidence score for display
     */
    formatConfidence(score) {
        return `${Math.round(score * 100)}%`;
    },
    
    /**
     * Validate clinical parameters
     */
    validateParameters(parameters) {
        const errors = [];
        
        // Required fields
        const required = ['tumor_stage', 'histology', 'performance_status'];
        required.forEach(field => {
            if (!parameters[field]) {
                errors.push(`${field.replace('_', ' ')} is required`);
            }
        });
        
        // TNM stage validation
        if (parameters.tumor_stage && !/^T[1-4][a-c]?N[0-3][a-c]?M[0-1][a-c]?$/i.test(parameters.tumor_stage)) {
            errors.push('Invalid TNM stage format');
        }
        
        // Performance status validation
        if (parameters.performance_status) {
            const ps = parameters.performance_status;
            if (ps.ecog !== undefined && (ps.ecog < 0 || ps.ecog > 4)) {
                errors.push('ECOG score must be between 0 and 4');
            }
            if (ps.karnofsky !== undefined && (ps.karnofsky < 0 || ps.karnofsky > 100)) {
                errors.push('Karnofsky score must be between 0 and 100');
            }
        }
        
        return errors;
    },
    
    /**
     * Process decision request
     */
    async processDecision(engineName, patientId, parameters) {
        try {
            // Validate parameters
            const validationErrors = this.validateParameters(parameters);
            if (validationErrors.length > 0) {
                throw new Error(`Validation failed: ${validationErrors.join(', ')}`);
            }
            
            const response = await fetch('/api/v1/decision-engine/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${window.GastricADCI.user?.token}`
                },
                body: JSON.stringify({
                    engine_name: engineName,
                    patient_id: patientId,
                    clinical_parameters: parameters,
                    include_alternatives: true
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            return result;
            
        } catch (error) {
            console.error('Decision processing failed:', error);
            throw error;
        }
    }
};

/**
 * Chart Utilities
 */
window.GastricADCI.Charts = {
    /**
     * Create confidence chart
     */
    createConfidenceChart(canvasId, confidenceData) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return null;
        
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Confidence', 'Uncertainty'],
                datasets: [{
                    data: [confidenceData.score * 100, (1 - confidenceData.score) * 100],
                    backgroundColor: [
                        confidenceData.score >= 0.7 ? '#10b981' : confidenceData.score >= 0.5 ? '#f59e0b' : '#ef4444',
                        '#e5e7eb'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed.toFixed(1) + '%';
                            }
                        }
                    }
                }
            }
        });
    },
    
    /**
     * Create outcome timeline chart
     */
    createTimelineChart(canvasId, timelineData) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return null;
        
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: timelineData.labels,
                datasets: [{
                    label: 'Treatment Progress',
                    data: timelineData.values,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
};

/**
 * Cohort Management Functions
 */
function initializeCohortManagement() {
    initializeFileUpload();
    initializePatientForms();
    initializeResultsTable();
    initializeExportOptions();
    initializeRealTimeUpdates();
    
    console.log('Cohort management initialized');
}

/**
 * File Upload Handling
 */
function initializeFileUpload() {
    const uploadZone = document.querySelector('.cohort-upload-zone');
    const fileInput = document.querySelector('#file');
    
    if (!uploadZone || !fileInput) return;
    
    // Drag and drop functionality
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });
    
    uploadZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
    });
    
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            validateFile(files[0]);
        }
    });
    
    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            validateFile(e.target.files[0]);
        }
    });
}

/**
 * File Validation
 */
function validateFile(file) {
    const formatType = document.querySelector('input[name="format_type"]:checked')?.value;
    const maxSize = 10 * 1024 * 1024; // 10MB
    
    // Size validation
    if (file.size > maxSize) {
        showNotification('File size must be less than 10MB', 'error');
        return false;
    }
    
    // Format validation
    const validExtensions = {
        'csv': ['.csv'],
        'json': ['.json'],
        'fhir': ['.json']
    };
    
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    const allowedExtensions = validExtensions[formatType] || [];
    
    if (!allowedExtensions.includes(fileExtension)) {
        showNotification(`Invalid file type. Expected: ${allowedExtensions.join(', ')}`, 'error');
        return false;
    }
    
    // Preview file content for validation
    if (formatType === 'csv') {
        previewCSV(file);
    } else if (formatType === 'json' || formatType === 'fhir') {
        previewJSON(file);
    }
    
    return true;
}

/**
 * CSV Preview
 */
function previewCSV(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        const csv = e.target.result;
        const lines = csv.split('\n');
        const headers = lines[0].split(',');
        
        // Validate required columns
        const requiredColumns = ['patient_id', 'age', 'gender', 'clinical_parameters'];
        const missingColumns = requiredColumns.filter(col => !headers.includes(col));
        
        if (missingColumns.length > 0) {
            showNotification(`Missing required columns: ${missingColumns.join(', ')}`, 'error');
            return;
        }
        
        // Show preview
        showFilePreview('CSV', {
            headers: headers,
            rowCount: lines.length - 1,
            sample: lines.slice(1, 4)
        });
    };
    reader.readAsText(file);
}

/**
 * JSON Preview
 */
function previewJSON(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const data = JSON.parse(e.target.result);
            
            // Validate structure based on format type
            const formatType = document.querySelector('input[name="format_type"]:checked')?.value;
            
            if (formatType === 'fhir') {
                if (!data.resourceType || data.resourceType !== 'Bundle') {
                    showNotification('Invalid FHIR Bundle format', 'error');
                    return;
                }
            } else if (formatType === 'json') {
                if (!Array.isArray(data)) {
                    showNotification('JSON must be an array of patient objects', 'error');
                    return;
                }
            }
            
            showFilePreview('JSON', {
                format: formatType,
                recordCount: Array.isArray(data) ? data.length : (data.entry?.length || 0),
                structure: typeof data
            });
            
        } catch (error) {
            showNotification('Invalid JSON format', 'error');
        }
    };
    reader.readAsText(file);
}

/**
 * Show File Preview
 */
function showFilePreview(type, data) {
    const previewElement = document.getElementById('file-preview');
    if (!previewElement) return;
    
    let content = `<div class="bg-green-50 border border-green-200 rounded-lg p-4 mt-4">
        <h4 class="font-semibold text-green-800">File Preview: ${type}</h4>`;
    
    if (type === 'CSV') {
        content += `<p class="text-sm text-green-700">Headers: ${data.headers.join(', ')}</p>
                   <p class="text-sm text-green-700">Rows: ${data.rowCount}</p>`;
    } else {
        content += `<p class="text-sm text-green-700">Records: ${data.recordCount}</p>
                   <p class="text-sm text-green-700">Format: ${data.format.toUpperCase()}</p>`;
    }
    
    content += '</div>';
    previewElement.innerHTML = content;
}

/**
 * Patient Forms Management
 */
function initializePatientForms() {
    window.patientCount = 1;
    
    // Add patient form function
    window.addPatientForm = function() {
        const container = document.getElementById('patients-container');
        if (!container) return;
        
        const formHtml = createPatientFormHTML(window.patientCount);
        container.insertAdjacentHTML('beforeend', formHtml);
        window.patientCount++;
        
        // Add validation to new form
        validatePatientForm(window.patientCount - 1);
    };
    
    // Remove patient form function
    window.removePatientForm = function(index) {
        const form = document.getElementById(`patient-form-${index}`);
        if (form && window.patientCount > 1) {
            form.remove();
        }
    };
    
    // Validate all existing forms
    document.querySelectorAll('.patient-form').forEach((form, index) => {
        validatePatientForm(index);
    });
}

/**
 * Create Patient Form HTML
 */
function createPatientFormHTML(index) {
    return `
        <div id="patient-form-${index}" class="patient-form">
            <div class="p-3 border border-gray-200 rounded">
                <div class="flex justify-between items-center mb-3">
                    <h4 class="text-md font-medium">Patient ${index + 1}</h4>
                    <button type="button" class="text-red-600 hover:text-red-800 text-sm" onclick="removePatientForm(${index})">
                        Remove
                    </button>
                </div>
                <div class="flex mb-3">
                    <div class="flex-1 mr-2">
                        <label class="block text-xs font-medium mb-1">Patient ID</label>
                        <input type="text" name="patients[${index}][patient_id]" required 
                               placeholder="Unique patient identifier"
                               class="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500">
                    </div>
                    <div class="w-20 mr-2">
                        <label class="block text-xs font-medium mb-1">Age</label>
                        <input type="number" name="patients[${index}][age]" min="0" max="120" required
                               class="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500">
                    </div>
                    <div class="w-24">
                        <label class="block text-xs font-medium mb-1">Gender</label>
                        <select name="patients[${index}][gender]" required
                                class="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500">
                            <option value="male">Male</option>
                            <option value="female">Female</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                </div>
                <div class="mb-3">
                    <label class="block text-xs font-medium mb-1">Clinical Parameters (JSON)</label>
                    <textarea name="patients[${index}][clinical_parameters]" rows="3"
                              placeholder='{"tumor_stage": "T2N1M0", "histology": "adenocarcinoma", ...}'
                              class="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"></textarea>
                </div>
            </div>
        </div>
    `;
}

/**
 * Validate Patient Form
 */
function validatePatientForm(index) {
    const form = document.getElementById(`patient-form-${index}`);
    if (!form) return;
    
    const clinicalParams = form.querySelector(`textarea[name="patients[${index}][clinical_parameters]"]`);
    if (!clinicalParams) return;
    
    clinicalParams.addEventListener('blur', () => {
        const value = clinicalParams.value.trim();
        if (value) {
            try {
                JSON.parse(value);
                clinicalParams.classList.remove('border-red-300');
                clinicalParams.classList.add('border-green-300');
            } catch (error) {
                clinicalParams.classList.remove('border-green-300');
                clinicalParams.classList.add('border-red-300');
                showNotification(`Invalid JSON in Patient ${index + 1} clinical parameters`, 'error');
            }
        }
    });
}

/**
 * Results Table Management
 */
function initializeResultsTable() {
    const table = document.querySelector('.results-table');
    if (!table) return;
    
    // Add sorting functionality
    const headers = table.querySelectorAll('th[data-sortable]');
    headers.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', () => {
            const column = header.dataset.sortable;
            sortTable(table, column);
        });
    });
    
    // Add filtering functionality
    const filterInputs = document.querySelectorAll('[data-filter]');
    filterInputs.forEach(input => {
        input.addEventListener('input', debounce(() => {
            filterResults();
        }, 300));
    });
}

/**
 * Sort Table
 */
function sortTable(table, column) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aValue = a.querySelector(`[data-${column}]`)?.textContent || '';
        const bValue = b.querySelector(`[data-${column}]`)?.textContent || '';
        
        if (column === 'risk_score' || column === 'confidence') {
            return parseFloat(aValue) - parseFloat(bValue);
        }
        return aValue.localeCompare(bValue);
    });
    
    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
}

/**
 * Filter Results
 */
function filterResults() {
    const filters = {};
    document.querySelectorAll('[data-filter]').forEach(input => {
        filters[input.dataset.filter] = input.value;
    });
    
    // Trigger HTMX request with filters
    htmx.trigger(document.body, 'filter-results', { detail: filters });
}

/**
 * Export Options Management
 */
function initializeExportOptions() {
    const exportForm = document.querySelector('#export-form');
    if (!exportForm) return;
    
    // Handle export format changes
    const formatRadios = exportForm.querySelectorAll('input[name="export_format"]');
    formatRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            updateExportOptions(radio.value);
        });
    });
    
    // Handle export progress
    document.addEventListener('htmx:afterRequest', (event) => {
        if (event.detail.pathInfo.requestPath.includes('/export')) {
            handleExportResponse(event.detail.xhr.response);
        }
    });
}

/**
 * Update Export Options
 */
function updateExportOptions(format) {
    const optionsContainer = document.getElementById('export-options');
    if (!optionsContainer) return;
    
    const options = {
        'csv': ['Summary Statistics', 'Raw Data', 'Confidence Scores'],
        'pdf': ['Executive Summary', 'Charts & Graphs', 'Detailed Analysis'],
        'fhir': ['Patient Resources', 'Observation Data', 'Diagnostic Reports'],
        'excel': ['Multiple Worksheets', 'Pivot Tables', 'Charts']
    };
    
    const formatOptions = options[format] || [];
    optionsContainer.innerHTML = formatOptions.map(option => `
        <label class="flex items-center mb-2">
            <input type="checkbox" name="export_options" value="${option.toLowerCase().replace(/\s+/g, '_')}" class="mr-2">
            ${option}
        </label>
    `).join('');
}

/**
 * Handle Export Response
 */
function handleExportResponse(response) {
    try {
        const data = JSON.parse(response);
        if (data.export_id) {
            pollExportStatus(data.export_id);
        }
    } catch (error) {
        console.error('Error parsing export response:', error);
    }
}

/**
 * Poll Export Status
 */
function pollExportStatus(exportId) {
    const pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/v1/cohorts/exports/${exportId}/status`);
            const data = await response.json();
            
            updateExportProgress(data.status, data.progress);
            
            if (data.status === 'completed') {
                clearInterval(pollInterval);
                showExportDownload(exportId);
            } else if (data.status === 'failed') {
                clearInterval(pollInterval);
                showNotification('Export failed. Please try again.', 'error');
            }
        } catch (error) {
            console.error('Error polling export status:', error);
        }
    }, 2000);
}

/**
 * Update Export Progress
 */
function updateExportProgress(status, progress) {
    const statusElement = document.getElementById('export-status');
    if (!statusElement) return;
    
    statusElement.innerHTML = `
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div class="flex items-center justify-between mb-2">
                <span class="font-medium text-blue-800">Export ${status}</span>
                <span class="text-sm text-blue-600">${progress || 0}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-bar-fill" style="width: ${progress || 0}%"></div>
            </div>
        </div>
    `;
}

/**
 * Show Export Download
 */
function showExportDownload(exportId) {
    const statusElement = document.getElementById('export-status');
    if (!statusElement) return;
    
    statusElement.innerHTML = `
        <div class="bg-green-50 border border-green-200 rounded-lg p-4">
            <div class="flex items-center justify-between">
                <span class="font-medium text-green-800">Export Complete</span>
                <a href="/api/v1/cohorts/exports/${exportId}/download" 
                   class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                    Download
                </a>
            </div>
        </div>
    `;
}

/**
 * Real-time Updates
 */
function initializeRealTimeUpdates() {
    // Poll for processing status updates
    if (window.location.pathname.includes('/results')) {
        const sessionId = new URLSearchParams(window.location.search).get('session_id');
        if (sessionId) {
            pollProcessingStatus(sessionId);
        }
    }
}

/**
 * Poll Processing Status
 */
function pollProcessingStatus(sessionId) {
    const pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/v1/cohorts/sessions/${sessionId}/status`);
            const data = await response.json();
            
            updateProcessingStatus(data);
            
            if (data.status === 'completed' || data.status === 'failed') {
                clearInterval(pollInterval);
                if (data.status === 'completed') {
                    // Refresh results
                    htmx.trigger(document.body, 'refresh-results');
                }
            }
        } catch (error) {
            console.error('Error polling processing status:', error);
        }
    }, 3000);
}

/**
 * Update Processing Status
 */
function updateProcessingStatus(data) {
    const statusElement = document.querySelector('.cohort-status-badge');
    const progressElement = document.querySelector('.progress-bar-fill');
    
    if (statusElement) {
        statusElement.textContent = data.status;
        statusElement.className = `cohort-status-badge ${data.status}`;
    }
    
    if (progressElement) {
        progressElement.style.width = `${data.progress || 0}%`;
    }
}

/**
 * Utility Functions
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showNotification(message, type = 'info') {
    // Use existing notification system from main app
    if (window.GastricADCI && window.GastricADCI.showNotification) {
        window.GastricADCI.showNotification(message, type);
    } else {
        console.log(`${type.toUpperCase()}: ${message}`);
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.GastricADCI;
}
