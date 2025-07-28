/**
 * Gastric ADCI Platform JavaScript
 * Main application functionality and utilities
 */

// Global app configuration
window.YazApp = {
    version: '1.0.0',
    apiBaseUrl: '/api',
    debug: true
};

// Utility functions
const utils = {
    /**
     * Format number as percentage
     */
    formatPercent: (value, decimals = 1) => {
        return (value * 100).toFixed(decimals) + '%';
    },

    /**
     * Format ADCI score with appropriate styling
     */
    formatADCIScore: (score) => {
        const formattedScore = score.toFixed(1);
        if (score >= 80) return `<span class="text-green-600 font-bold">${formattedScore}</span>`;
        if (score >= 65) return `<span class="text-yellow-600 font-bold">${formattedScore}</span>`;
        return `<span class="text-red-600 font-bold">${formattedScore}</span>`;
    },

    /**
     * Show notification
     */
    showNotification: (message, type = 'info', duration = 5000) => {
        const notification = document.createElement('div');
        notification.className = `notification ${type} fixed top-4 right-4 z-50 max-w-sm`;
        notification.innerHTML = `
            <div class="flex items-center">
                <div class="flex-1">${message}</div>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-gray-500 hover:text-gray-700">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, duration);
        }
    },

    /**
     * Debounce function calls
     */
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Copy text to clipboard
     */
    copyToClipboard: async (text) => {
        try {
            await navigator.clipboard.writeText(text);
            utils.showNotification('Copied to clipboard', 'success');
        } catch (err) {
            console.error('Failed to copy text: ', err);
            utils.showNotification('Failed to copy to clipboard', 'error');
        }
    }
};

// HTMX event handlers
document.addEventListener('htmx:configRequest', (event) => {
    // Add CSRF token if available
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    if (csrfToken) {
        event.detail.headers['X-CSRFToken'] = csrfToken.getAttribute('content');
    }
});

document.addEventListener('htmx:beforeRequest', (event) => {
    // Show loading state
    const element = event.detail.elt;
    element.classList.add('htmx-request');
    
    // Add loading spinner if target has loading-spinner class
    const spinner = element.querySelector('.loading-spinner');
    if (spinner) {
        spinner.style.display = 'inline-block';
    }
});

document.addEventListener('htmx:afterRequest', (event) => {
    // Hide loading state
    const element = event.detail.elt;
    element.classList.remove('htmx-request');
    
    // Hide loading spinner
    const spinner = element.querySelector('.loading-spinner');
    if (spinner) {
        spinner.style.display = 'none';
    }
    
    // Handle response
    const xhr = event.detail.xhr;
    if (xhr.status >= 200 && xhr.status < 300) {
        // Success
        utils.showNotification('Request completed successfully', 'success', 3000);
    } else if (xhr.status >= 400) {
        // Error
        try {
            const response = JSON.parse(xhr.responseText);
            utils.showNotification(response.message || 'An error occurred', 'error');
        } catch (e) {
            utils.showNotification('An error occurred', 'error');
        }
    }
});

// Clinical data processing functions
const clinical = {
    /**
     * Calculate risk level from ADCI score
     */
    calculateRiskLevel: (adciScore) => {
        if (adciScore >= 85) return { level: 'low', class: 'risk-low', text: 'Low Risk' };
        if (adciScore >= 65) return { level: 'medium', class: 'risk-medium', text: 'Medium Risk' };
        return { level: 'high', class: 'risk-high', text: 'High Risk' };
    },

    /**
     * Generate clinical recommendation
     */
    generateRecommendation: (adciScore, flotEligible = false) => {
        if (adciScore >= 85) {
            return flotEligible ? 
                'Proceed with FLOT protocol + surgery' : 
                'Proceed with standard treatment protocol';
        }
        if (adciScore >= 65) {
            return 'Consider neoadjuvant therapy with close monitoring';
        }
        return 'Requires multidisciplinary team review and risk assessment';
    },

    /**
     * Validate clinical data
     */
    validateClinicalData: (data) => {
        const errors = [];
        
        if (!data.value || data.value < 0 || data.value > 100) {
            errors.push('Clinical value must be between 0 and 100');
        }
        
        if (!data.title || data.title.trim().length < 5) {
            errors.push('Title must be at least 5 characters long');
        }
        
        if (!data.author || data.author.trim().length < 2) {
            errors.push('Author name is required');
        }
        
        return errors;
    }
};

// Data visualization utilities
const charts = {
    /**
     * Create ADCI score distribution chart
     */
    createADCIDistribution: (canvasId, data) => {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        // Process data into score ranges
        const ranges = {
            'High (85-100)': data.filter(d => d.adci_score >= 85).length,
            'Medium (65-84)': data.filter(d => d.adci_score >= 65 && d.adci_score < 85).length,
            'Low (0-64)': data.filter(d => d.adci_score < 65).length
        };
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(ranges),
                datasets: [{
                    data: Object.values(ranges),
                    backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'ADCI Score Distribution'
                    }
                }
            }
        });
    },

    /**
     * Create evidence score timeline
     */
    createEvidenceTimeline: (canvasId, insights) => {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: insights.map((_, i) => `Insight ${i + 1}`),
                datasets: [{
                    label: 'Evidence Score',
                    data: insights.map(i => i.evidence_score),
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Evidence Score Trends'
                    }
                }
            }
        });
    }
};

// Export handling
const exports = {
    /**
     * Download data as CSV
     */
    downloadCSV: (data, filename = 'clinical_data.csv') => {
        if (!data || data.length === 0) {
            utils.showNotification('No data to export', 'warning');
            return;
        }
        
        const headers = Object.keys(data[0]);
        const csvContent = [
            headers.join(','),
            ...data.map(row => headers.map(header => 
                JSON.stringify(row[header] || '')
            ).join(','))
        ].join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        link.click();
        
        utils.showNotification('Data exported successfully', 'success');
    },

    /**
     * Generate and download report
     */
    generateReport: async (format = 'json') => {
        try {
            const response = await fetch(`/api/reports?format=${format}`);
            const data = await response.json();
            
            if (data.success) {
                const filename = `clinical_report_${new Date().toISOString().split('T')[0]}.${format}`;
                
                if (format === 'json') {
                    const blob = new Blob([JSON.stringify(data.data, null, 2)], { 
                        type: 'application/json' 
                    });
                    const link = document.createElement('a');
                    link.href = URL.createObjectURL(blob);
                    link.download = filename;
                    link.click();
                } else {
                    // Handle other formats
                    exports.downloadCSV(data.data.cases || [], filename);
                }
                
                utils.showNotification('Report generated successfully', 'success');
            } else {
                utils.showNotification(data.message || 'Failed to generate report', 'error');
            }
        } catch (error) {
            console.error('Report generation error:', error);
            utils.showNotification('Failed to generate report', 'error');
        }
    }
};

// Search and filter functionality
const search = {
    /**
     * Initialize search functionality
     */
    init: () => {
        const searchInput = document.querySelector('[name="query"]');
        if (searchInput) {
            searchInput.addEventListener('input', utils.debounce((e) => {
                // Search is handled by HTMX, this is for additional client-side processing
                console.log('Search query:', e.target.value);
            }, 300));
        }
    },

    /**
     * Apply client-side filters
     */
    applyFilters: (data, filters) => {
        return data.filter(item => {
            // Apply risk level filter
            if (filters.riskLevel && filters.riskLevel !== 'all') {
                const risk = clinical.calculateRiskLevel(item.adci_score);
                if (risk.level !== filters.riskLevel) return false;
            }
            
            // Apply FLOT eligibility filter
            if (filters.flotEligible !== undefined) {
                if (item.flot_eligible !== filters.flotEligible) return false;
            }
            
            // Apply score range filter
            if (filters.minScore !== undefined) {
                if (item.adci_score < filters.minScore) return false;
            }
            
            if (filters.maxScore !== undefined) {
                if (item.adci_score > filters.maxScore) return false;
            }
            
            return true;
        });
    }
};

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    console.log('Gastric ADCI Platform initialized');
    
    // Initialize search functionality
    search.init();
    
    // Add global error handler
    window.addEventListener('error', (event) => {
        if (window.YazApp.debug) {
            console.error('Global error:', event.error);
        }
    });
    
    // Add unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
        if (window.YazApp.debug) {
            console.error('Unhandled promise rejection:', event.reason);
        }
    });
    
    // Make utilities available globally
    window.YazApp.utils = utils;
    window.YazApp.clinical = clinical;
    window.YazApp.charts = charts;
    window.YazApp.exports = exports;
    window.YazApp.search = search;
});

// Service Worker registration for PWA
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then((registration) => {
                console.log('SW registered: ', registration);
            })
            .catch((registrationError) => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
