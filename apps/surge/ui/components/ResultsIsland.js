/**
 * Results Island Component
 * Real-time analytics and results display with interactive charts
 */

class ResultsIsland {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            showCharts: true,
            showMetrics: true,
            showExport: true,
            refreshInterval: 30000, // 30 seconds
            chartTypes: ['line', 'bar', 'pie'],
            ...options
        };
        this.data = options.data || {};
        this.refreshTimer = null;
    }

    render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container with id "${this.containerId}" not found`);
            return;
        }

        const html = `
            <div class="results-island bg-white rounded-lg shadow-lg p-6" data-component="results-island">
                ${this.renderHeader()}
                ${this.renderMetrics()}
                ${this.options.showCharts ? this.renderCharts() : ''}
                ${this.renderDataTable()}
                ${this.options.showExport ? this.renderExportOptions() : ''}
                ${this.renderTextContent()}
                ${this.renderImageGallery()}
            </div>
        `;

        container.innerHTML = html;
        this.attachEventListeners();
        this.startAutoRefresh();
        this.initializeCharts();
    }

    renderHeader() {
        return `
            <div class="results-header flex justify-between items-center mb-6">
                <div>
                    <h2 class="text-2xl font-bold text-gray-900">Analytics Results</h2>
                    <p class="text-gray-600">Real-time cohort analysis and outcomes</p>
                </div>
                <div class="flex items-center space-x-4">
                    <button class="refresh-btn btn-secondary" title="Refresh Data">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                        </svg>
                    </button>
                    <div class="last-updated text-sm text-gray-500">
                        Last updated: <span class="timestamp">Loading...</span>
                    </div>
                </div>
            </div>
        `;
    }

    renderMetrics() {
        const metrics = this.data.metrics || {};
        return `
            <div class="metrics-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <div class="metric-card bg-blue-50 rounded-lg p-4">
                    <div class="flex items-center">
                        <div class="metric-icon bg-blue-100 rounded-lg p-3">
                            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                            </svg>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-600">Total Cases</p>
                            <p class="text-2xl font-semibold text-gray-900">${metrics.totalCases || 0}</p>
                        </div>
                    </div>
                </div>

                <div class="metric-card bg-green-50 rounded-lg p-4">
                    <div class="flex items-center">
                        <div class="metric-icon bg-green-100 rounded-lg p-3">
                            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-600">Success Rate</p>
                            <p class="text-2xl font-semibold text-gray-900">${metrics.successRate || 0}%</p>
                        </div>
                    </div>
                </div>

                <div class="metric-card bg-yellow-50 rounded-lg p-4">
                    <div class="flex items-center">
                        <div class="metric-icon bg-yellow-100 rounded-lg p-3">
                            <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-600">Avg Duration</p>
                            <p class="text-2xl font-semibold text-gray-900">${metrics.avgDuration || 0}min</p>
                        </div>
                    </div>
                </div>

                <div class="metric-card bg-purple-50 rounded-lg p-4">
                    <div class="flex items-center">
                        <div class="metric-icon bg-purple-100 rounded-lg p-3">
                            <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                            </svg>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-600">Improvement</p>
                            <p class="text-2xl font-semibold text-gray-900">+${metrics.improvement || 0}%</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderCharts() {
        return `
            <div class="charts-section mb-8">
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div class="chart-container bg-gray-50 rounded-lg p-4">
                        <h3 class="text-lg font-semibold text-gray-900 mb-4">Outcome Trends</h3>
                        <canvas id="${this.containerId}-trend-chart" width="400" height="200"></canvas>
                    </div>
                    <div class="chart-container bg-gray-50 rounded-lg p-4">
                        <h3 class="text-lg font-semibold text-gray-900 mb-4">Case Distribution</h3>
                        <canvas id="${this.containerId}-distribution-chart" width="400" height="200"></canvas>
                    </div>
                </div>
            </div>
        `;
    }

    renderDataTable() {
        const cases = this.data.cases || [];
        return `
            <div class="data-table-section">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">Recent Cases</h3>
                <div class="overflow-x-auto">
                    <table class="min-w-full bg-white border border-gray-200 rounded-lg">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Case ID</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Patient</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Procedure</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Outcome</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-200">
                            ${cases.slice(0, 10).map(case_ => `
                                <tr class="hover:bg-gray-50 cursor-pointer" data-case-id="${case_.id}">
                                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${case_.id}</td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${case_.patient || 'Anonymous'}</td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${case_.procedure || 'N/A'}</td>
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${this.getOutcomeColor(case_.outcome)}">
                                            ${case_.outcome || 'Pending'}
                                        </span>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${this.formatDate(case_.date)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    renderExportOptions() {
        return `
            <div class="export-section mt-6 pt-6 border-t border-gray-200">
                <div class="flex justify-between items-center">
                    <h3 class="text-lg font-semibold text-gray-900">Export Results</h3>
                    <div class="flex space-x-2">
                        <button class="export-btn btn-secondary" data-format="csv">
                            Export CSV
                        </button>
                        <button class="export-btn btn-secondary" data-format="pdf">
                            Export PDF
                        </button>
                        <button class="export-btn btn-secondary" data-format="excel">
                            Export Excel
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    renderTextContent() {
        const textData = this.data.textContent || {};
        if (!textData || Object.keys(textData).length === 0) {
            return '';
        }

        return `
            <div class="text-content-section mb-8">
                <h3 class="text-xl font-semibold text-gray-900 mb-4">Text Analysis</h3>
                <div class="text-content-grid grid grid-cols-1 lg:grid-cols-2 gap-6">
                    ${this.renderTextEntries(textData)}
                </div>
            </div>
        `;
    }

    renderTextEntries(textData) {
        let html = '';
        
        // Clinical Notes
        if (textData.clinicalNotes && textData.clinicalNotes.length > 0) {
            html += `
                <div class="text-entry-card bg-blue-50 rounded-lg p-4">
                    <h4 class="font-semibold text-blue-900 mb-2">Clinical Notes</h4>
                    <div class="text-entries max-h-48 overflow-y-auto">
                        ${textData.clinicalNotes.map(note => `
                            <div class="text-entry mb-3 p-3 bg-white rounded border">
                                <div class="text-entry-header flex justify-between items-start mb-2">
                                    <span class="text-sm font-medium text-gray-700">${note.title || 'Clinical Note'}</span>
                                    <span class="text-xs text-gray-500">${note.timestamp || ''}</span>
                                </div>
                                <div class="text-entry-content text-sm text-gray-600">
                                    ${this.truncateText(note.content, 200)}
                                </div>
                                ${note.tags && note.tags.length > 0 ? `
                                    <div class="text-entry-tags mt-2">
                                        ${note.tags.map(tag => `<span class="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded mr-1">${tag}</span>`).join('')}
                                    </div>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        // Pathology Reports
        if (textData.pathologyReports && textData.pathologyReports.length > 0) {
            html += `
                <div class="text-entry-card bg-red-50 rounded-lg p-4">
                    <h4 class="font-semibold text-red-900 mb-2">Pathology Reports</h4>
                    <div class="text-entries max-h-48 overflow-y-auto">
                        ${textData.pathologyReports.map(report => `
                            <div class="text-entry mb-3 p-3 bg-white rounded border">
                                <div class="text-entry-header flex justify-between items-start mb-2">
                                    <span class="text-sm font-medium text-gray-700">${report.title || 'Pathology Report'}</span>
                                    <span class="text-xs text-gray-500">${report.timestamp || ''}</span>
                                </div>
                                <div class="text-entry-content text-sm text-gray-600">
                                    ${this.truncateText(report.content, 200)}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        // Generated Text Summaries
        if (textData.generatedSummaries && textData.generatedSummaries.length > 0) {
            html += `
                <div class="text-entry-card bg-green-50 rounded-lg p-4">
                    <h4 class="font-semibold text-green-900 mb-2">AI-Generated Summaries</h4>
                    <div class="text-entries max-h-48 overflow-y-auto">
                        ${textData.generatedSummaries.map(summary => `
                            <div class="text-entry mb-3 p-3 bg-white rounded border">
                                <div class="text-entry-header flex justify-between items-start mb-2">
                                    <span class="text-sm font-medium text-gray-700">${summary.type || 'Summary'}</span>
                                    <span class="text-xs text-gray-500">${summary.audience || 'General'}</span>
                                </div>
                                <div class="text-entry-content text-sm text-gray-600">
                                    ${this.truncateText(summary.content, 300)}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        return html;
    }

    renderImageGallery() {
        const imageData = this.data.imageContent || {};
        if (!imageData || Object.keys(imageData).length === 0) {
            return '';
        }

        return `
            <div class="image-gallery-section mb-8">
                <h3 class="text-xl font-semibold text-gray-900 mb-4">Medical Images & Visualizations</h3>
                <div class="image-gallery-grid">
                    ${this.renderImageCategories(imageData)}
                </div>
            </div>
        `;
    }

    renderImageCategories(imageData) {
        let html = '';

        // Medical Images
        if (imageData.medicalImages && imageData.medicalImages.length > 0) {
            html += `
                <div class="image-category mb-6">
                    <h4 class="font-semibold text-gray-800 mb-3">Medical Images</h4>
                    <div class="image-grid grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                        ${imageData.medicalImages.map(image => this.renderImageCard(image, 'medical')).join('')}
                    </div>
                </div>
            `;
        }

        // Generated Visualizations
        if (imageData.generatedVisualizations && imageData.generatedVisualizations.length > 0) {
            html += `
                <div class="image-category mb-6">
                    <h4 class="font-semibold text-gray-800 mb-3">Generated Visualizations</h4>
                    <div class="image-grid grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                        ${imageData.generatedVisualizations.map(image => this.renderImageCard(image, 'visualization')).join('')}
                    </div>
                </div>
            `;
        }

        // Domain-Specific Images
        if (imageData.domainImages) {
            Object.keys(imageData.domainImages).forEach(domain => {
                if (imageData.domainImages[domain] && imageData.domainImages[domain].length > 0) {
                    html += `
                        <div class="image-category mb-6">
                            <h4 class="font-semibold text-gray-800 mb-3">${domain.charAt(0).toUpperCase() + domain.slice(1)} Images</h4>
                            <div class="image-grid grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                                ${imageData.domainImages[domain].map(image => this.renderImageCard(image, domain)).join('')}
                            </div>
                        </div>
                    `;
                }
            });
        }

        return html;
    }

    renderImageCard(image, category) {
        const categoryColors = {
            'medical': 'border-blue-200 bg-blue-50',
            'visualization': 'border-green-200 bg-green-50',
            'surgery': 'border-red-200 bg-red-50',
            'logistics': 'border-yellow-200 bg-yellow-50',
            'insurance': 'border-purple-200 bg-purple-50',
        };

        const borderClass = categoryColors[category] || 'border-gray-200 bg-gray-50';

        return `
            <div class="image-card ${borderClass} rounded-lg border overflow-hidden cursor-pointer hover:shadow-md transition-shadow"
                 data-image-id="${image.id || ''}" onclick="this.showImageModal('${image.id || ''}', '${image.path || ''}', '${image.title || ''}')">
                <div class="image-container aspect-square relative">
                    <img src="${image.thumbnail || image.path}" 
                         alt="${image.title || 'Medical image'}"
                         class="w-full h-full object-cover"
                         onerror="this.src='/static/images/placeholder.png'">
                    <div class="image-overlay absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-20 transition-all flex items-center justify-center">
                        <svg class="w-8 h-8 text-white opacity-0 hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"></path>
                        </svg>
                    </div>
                </div>
                <div class="image-info p-3">
                    <p class="text-sm font-medium text-gray-800 truncate">${image.title || 'Untitled'}</p>
                    <p class="text-xs text-gray-600">${image.type || category}</p>
                    ${image.timestamp ? `<p class="text-xs text-gray-500">${new Date(image.timestamp).toLocaleDateString()}</p>` : ''}
                </div>
            </div>
        `;
    }

    showImageModal(imageId, imagePath, imageTitle) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="max-w-4xl max-h-full m-4 bg-white rounded-lg overflow-hidden">
                <div class="flex justify-between items-center p-4 border-b">
                    <h3 class="text-lg font-semibold">${imageTitle}</h3>
                    <button class="close-modal text-gray-500 hover:text-gray-700">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                <div class="p-4">
                    <img src="${imagePath}" alt="${imageTitle}" class="max-w-full max-h-[70vh] mx-auto">
                </div>
            </div>
        `;

        // Add event listeners
        modal.querySelector('.close-modal').addEventListener('click', () => {
            document.body.removeChild(modal);
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });

        document.body.appendChild(modal);
    }

    attachEventListeners() {
        const container = document.getElementById(this.containerId);

        // Refresh button
        const refreshBtn = container.querySelector('.refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }

        // Export buttons
        const exportBtns = container.querySelectorAll('.export-btn');
        exportBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const format = e.target.dataset.format;
                this.exportData(format);
            });
        });

        // Table row clicks
        const tableRows = container.querySelectorAll('tbody tr[data-case-id]');
        tableRows.forEach(row => {
            row.addEventListener('click', (e) => {
                const caseId = e.currentTarget.dataset.caseId;
                this.showCaseDetail(caseId);
            });
        });
    }

    initializeCharts() {
        if (!this.options.showCharts) return;

        // Initialize trend chart
        const trendCanvas = document.getElementById(`${this.containerId}-trend-chart`);
        if (trendCanvas && window.Chart) {
            this.trendChart = new Chart(trendCanvas, {
                type: 'line',
                data: {
                    labels: this.data.trendLabels || [],
                    datasets: [{
                        label: 'Success Rate',
                        data: this.data.trendData || [],
                        borderColor: 'rgb(59, 130, 246)',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4
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
                    }
                }
            });
        }

        // Initialize distribution chart
        const distributionCanvas = document.getElementById(`${this.containerId}-distribution-chart`);
        if (distributionCanvas && window.Chart) {
            this.distributionChart = new Chart(distributionCanvas, {
                type: 'doughnut',
                data: {
                    labels: this.data.distributionLabels || [],
                    datasets: [{
                        data: this.data.distributionData || [],
                        backgroundColor: [
                            'rgba(59, 130, 246, 0.8)',
                            'rgba(16, 185, 129, 0.8)',
                            'rgba(245, 158, 11, 0.8)',
                            'rgba(239, 68, 68, 0.8)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
    }

    startAutoRefresh() {
        if (this.options.refreshInterval > 0) {
            this.refreshTimer = setInterval(() => {
                this.refreshData();
            }, this.options.refreshInterval);
        }
    }

    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    async refreshData() {
        try {
            const container = document.getElementById(this.containerId);
            const refreshBtn = container.querySelector('.refresh-btn');
            const timestamp = container.querySelector('.timestamp');

            // Show loading state
            if (refreshBtn) {
                refreshBtn.classList.add('animate-spin');
                refreshBtn.disabled = true;
            }

            // Fetch new data
            const response = await fetch('/api/v1/results/refresh', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });

            if (response.ok) {
                const newData = await response.json();
                this.data = { ...this.data, ...newData };
                
                // Update charts
                this.updateCharts();
                
                // Update metrics
                this.updateMetrics();
                
                // Update timestamp
                if (timestamp) {
                    timestamp.textContent = new Date().toLocaleString();
                }

                // Dispatch custom event
                container.dispatchEvent(new CustomEvent('dataRefreshed', {
                    detail: { data: this.data },
                    bubbles: true
                }));
            }
        } catch (error) {
            console.error('Error refreshing data:', error);
        } finally {
            const container = document.getElementById(this.containerId);
            const refreshBtn = container.querySelector('.refresh-btn');
            if (refreshBtn) {
                refreshBtn.classList.remove('animate-spin');
                refreshBtn.disabled = false;
            }
        }
    }

    updateCharts() {
        if (this.trendChart) {
            this.trendChart.data.labels = this.data.trendLabels || [];
            this.trendChart.data.datasets[0].data = this.data.trendData || [];
            this.trendChart.update();
        }

        if (this.distributionChart) {
            this.distributionChart.data.labels = this.data.distributionLabels || [];
            this.distributionChart.data.datasets[0].data = this.data.distributionData || [];
            this.distributionChart.update();
        }
    }

    updateMetrics() {
        const container = document.getElementById(this.containerId);
        const metrics = this.data.metrics || {};

        // Update metric values
        const metricCards = container.querySelectorAll('.metric-card');
        metricCards.forEach((card, index) => {
            const valueElement = card.querySelector('.text-2xl');
            if (valueElement) {
                switch (index) {
                    case 0:
                        valueElement.textContent = metrics.totalCases || 0;
                        break;
                    case 1:
                        valueElement.textContent = `${metrics.successRate || 0}%`;
                        break;
                    case 2:
                        valueElement.textContent = `${metrics.avgDuration || 0}min`;
                        break;
                    case 3:
                        valueElement.textContent = `+${metrics.improvement || 0}%`;
                        break;
                }
            }
        });
    }

    exportData(format) {
        const exportData = {
            metrics: this.data.metrics,
            cases: this.data.cases,
            timestamp: new Date().toISOString(),
            format: format
        };

        // Create download link
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
            type: 'application/json'
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `results-export-${Date.now()}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    showCaseDetail(caseId) {
        // Dispatch event for case selection
        const container = document.getElementById(this.containerId);
        container.dispatchEvent(new CustomEvent('caseSelected', {
            detail: { caseId: caseId },
            bubbles: true
        }));
    }

    // Helper methods
    getOutcomeColor(outcome) {
        const colors = {
            'Success': 'bg-green-100 text-green-800',
            'Partial': 'bg-yellow-100 text-yellow-800',
            'Failed': 'bg-red-100 text-red-800',
            'Pending': 'bg-gray-100 text-gray-800'
        };
        return colors[outcome] || colors['Pending'];
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleDateString();
    }

    getAuthToken() {
        return localStorage.getItem('authToken') || '';
    }

    // Public methods
    setData(data) {
        this.data = { ...this.data, ...data };
        this.updateCharts();
        this.updateMetrics();
    }

    getData() {
        return this.data;
    }

    destroy() {
        this.stopAutoRefresh();
        if (this.trendChart) {
            this.trendChart.destroy();
        }
        if (this.distributionChart) {
            this.distributionChart.destroy();
        }
    }
}

// Export for use in other modules
window.ResultsIsland = ResultsIsland;
