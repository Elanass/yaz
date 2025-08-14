/**
 * CaseList Component
 * A reusable case list component with filtering, pagination, and htmx support
 */

class CaseList {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            cases: options.cases || [],
            showSearch: options.showSearch !== false,
            showFilters: options.showFilters !== false,
            showPagination: options.showPagination !== false,
            pageSize: options.pageSize || 10,
            currentPage: options.currentPage || 1,
            onCaseSelect: options.onCaseSelect || null,
            htmxEndpoint: options.htmxEndpoint || null,
            className: options.className || '',
            emptyMessage: options.emptyMessage || 'No cases found',
            ...options
        };
        this.filteredCases = [...this.options.cases];
        this.searchTerm = '';
        this.selectedStatus = 'all';
    }

    render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container with id "${this.containerId}" not found`);
            return;
        }

        const html = `
            <div class="case-list ${this.options.className}" data-component="case-list">
                ${this.renderHeader()}
                ${this.renderFilters()}
                ${this.renderCaseItems()}
                ${this.options.showPagination ? this.renderPagination() : ''}
            </div>
        `;

        container.innerHTML = html;
        this.attachEventListeners();
        this.updateDisplay();
    }

    renderHeader() {
        if (!this.options.showSearch) return '';
        
        return `
            <div class="case-list-header mb-6">
                <div class="flex items-center justify-between">
                    <h3 class="text-lg font-semibold text-gray-900">Cases</h3>
                    <div class="flex items-center space-x-3">
                        <div class="relative">
                            <input 
                                type="text" 
                                placeholder="Search cases..." 
                                class="case-search-input w-64 pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            >
                            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                                </svg>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderFilters() {
        if (!this.options.showFilters) return '';

        const statuses = ['all', 'active', 'completed', 'pending', 'cancelled'];
        
        return `
            <div class="case-list-filters mb-4">
                <div class="flex items-center space-x-4">
                    <span class="text-sm font-medium text-gray-700">Filter by status:</span>
                    <div class="flex space-x-2">
                        ${statuses.map(status => `
                            <button 
                                class="status-filter px-3 py-1 text-sm rounded-full border transition-colors ${status === this.selectedStatus ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-gray-100 text-gray-700 border-gray-300 hover:bg-gray-200'}"
                                data-status="${status}"
                            >
                                ${status.charAt(0).toUpperCase() + status.slice(1)}
                            </button>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    renderCaseItems() {
        const startIndex = (this.options.currentPage - 1) * this.options.pageSize;
        const endIndex = startIndex + this.options.pageSize;
        const casesToShow = this.filteredCases.slice(startIndex, endIndex);

        if (casesToShow.length === 0) {
            return `
                <div class="case-list-empty text-center py-12">
                    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    <p class="mt-4 text-lg text-gray-600">${this.options.emptyMessage}</p>
                </div>
            `;
        }

        return `
            <div class="case-list-items space-y-3">
                ${casesToShow.map(caseItem => this.renderCaseItem(caseItem)).join('')}
            </div>
        `;
    }

    renderCaseItem(caseItem) {
        const statusColors = {
            active: 'bg-green-100 text-green-800',
            completed: 'bg-blue-100 text-blue-800',
            pending: 'bg-yellow-100 text-yellow-800',
            cancelled: 'bg-red-100 text-red-800'
        };

        return `
            <div 
                class="case-item bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer"
                data-case-id="${caseItem.id}"
                ${this.options.htmxEndpoint ? `hx-get="${this.options.htmxEndpoint}/${caseItem.id}" hx-target="#case-detail"` : ''}
            >
                <div class="flex items-center justify-between">
                    <div class="flex-1">
                        <div class="flex items-center space-x-3">
                            <h4 class="text-base font-medium text-gray-900">${caseItem.title || `Case #${caseItem.id}`}</h4>
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[caseItem.status] || 'bg-gray-100 text-gray-800'}">
                                ${caseItem.status || 'Unknown'}
                            </span>
                        </div>
                        <div class="mt-1">
                            <p class="text-sm text-gray-600">${caseItem.description || 'No description available'}</p>
                            <div class="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                                ${caseItem.patient ? `<span>Patient: ${caseItem.patient}</span>` : ''}
                                ${caseItem.date ? `<span>Date: ${new Date(caseItem.date).toLocaleDateString()}</span>` : ''}
                                ${caseItem.physician ? `<span>Physician: ${caseItem.physician}</span>` : ''}
                            </div>
                        </div>
                    </div>
                    <div class="ml-4">
                        <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                    </div>
                </div>
            </div>
        `;
    }

    renderPagination() {
        const totalPages = Math.ceil(this.filteredCases.length / this.options.pageSize);
        if (totalPages <= 1) return '';

        const currentPage = this.options.currentPage;
        const pages = [];
        
        // Generate page numbers
        for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {
            pages.push(i);
        }

        return `
            <div class="case-list-pagination mt-6 flex items-center justify-between">
                <div class="text-sm text-gray-700">
                    Showing ${(currentPage - 1) * this.options.pageSize + 1} to ${Math.min(currentPage * this.options.pageSize, this.filteredCases.length)} of ${this.filteredCases.length} results
                </div>
                <div class="flex items-center space-x-2">
                    <button 
                        class="pagination-btn px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 ${currentPage === 1 ? 'opacity-50 cursor-not-allowed' : ''}"
                        data-page="${currentPage - 1}"
                        ${currentPage === 1 ? 'disabled' : ''}
                    >
                        Previous
                    </button>
                    ${pages.map(page => `
                        <button 
                            class="pagination-btn px-3 py-2 text-sm border rounded-md transition-colors ${page === currentPage ? 'bg-blue-600 text-white border-blue-600' : 'border-gray-300 hover:bg-gray-50'}"
                            data-page="${page}"
                        >
                            ${page}
                        </button>
                    `).join('')}
                    <button 
                        class="pagination-btn px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 ${currentPage === totalPages ? 'opacity-50 cursor-not-allowed' : ''}"
                        data-page="${currentPage + 1}"
                        ${currentPage === totalPages ? 'disabled' : ''}
                    >
                        Next
                    </button>
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        const container = document.getElementById(this.containerId);

        // Search functionality
        const searchInput = container.querySelector('.case-search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchTerm = e.target.value.toLowerCase();
                this.filterCases();
                this.updateDisplay();
            });
        }

        // Status filters
        const statusFilters = container.querySelectorAll('.status-filter');
        statusFilters.forEach(filter => {
            filter.addEventListener('click', (e) => {
                this.selectedStatus = e.target.dataset.status;
                this.updateFilterButtons();
                this.filterCases();
                this.updateDisplay();
            });
        });

        // Case item clicks
        const caseItems = container.querySelectorAll('.case-item');
        caseItems.forEach(item => {
            item.addEventListener('click', (e) => {
                if (!e.target.closest('[hx-get]')) {
                    const caseId = item.dataset.caseId;
                    const caseData = this.options.cases.find(c => c.id == caseId);
                    
                    if (this.options.onCaseSelect) {
                        this.options.onCaseSelect(caseData);
                    }

                    // Dispatch custom event
                    container.dispatchEvent(new CustomEvent('caseSelected', {
                        detail: { case: caseData },
                        bubbles: true
                    }));
                }
            });
        });

        // Pagination
        const paginationBtns = container.querySelectorAll('.pagination-btn');
        paginationBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                if (!btn.disabled) {
                    this.options.currentPage = parseInt(e.target.dataset.page);
                    this.updateDisplay();
                }
            });
        });
    }

    filterCases() {
        this.filteredCases = this.options.cases.filter(caseItem => {
            const matchesSearch = !this.searchTerm || 
                (caseItem.title && caseItem.title.toLowerCase().includes(this.searchTerm)) ||
                (caseItem.description && caseItem.description.toLowerCase().includes(this.searchTerm)) ||
                (caseItem.patient && caseItem.patient.toLowerCase().includes(this.searchTerm));

            const matchesStatus = this.selectedStatus === 'all' || caseItem.status === this.selectedStatus;

            return matchesSearch && matchesStatus;
        });

        // Reset to first page when filtering
        this.options.currentPage = 1;
    }

    updateDisplay() {
        const container = document.getElementById(this.containerId);
        const itemsContainer = container.querySelector('.case-list-items') || container.querySelector('.case-list-empty')?.parentElement;
        const paginationContainer = container.querySelector('.case-list-pagination');

        if (itemsContainer) {
            itemsContainer.innerHTML = this.renderCaseItems();
            this.attachCaseItemListeners();
        }

        if (paginationContainer && this.options.showPagination) {
            paginationContainer.outerHTML = this.renderPagination();
            this.attachPaginationListeners();
        }
    }

    updateFilterButtons() {
        const container = document.getElementById(this.containerId);
        const filterBtns = container.querySelectorAll('.status-filter');
        
        filterBtns.forEach(btn => {
            const isSelected = btn.dataset.status === this.selectedStatus;
            btn.className = `status-filter px-3 py-1 text-sm rounded-full border transition-colors ${
                isSelected 
                    ? 'bg-blue-100 text-blue-800 border-blue-300' 
                    : 'bg-gray-100 text-gray-700 border-gray-300 hover:bg-gray-200'
            }`;
        });
    }

    attachCaseItemListeners() {
        const container = document.getElementById(this.containerId);
        const caseItems = container.querySelectorAll('.case-item');
        
        caseItems.forEach(item => {
            item.addEventListener('click', (e) => {
                if (!e.target.closest('[hx-get]')) {
                    const caseId = item.dataset.caseId;
                    const caseData = this.options.cases.find(c => c.id == caseId);
                    
                    if (this.options.onCaseSelect) {
                        this.options.onCaseSelect(caseData);
                    }

                    container.dispatchEvent(new CustomEvent('caseSelected', {
                        detail: { case: caseData },
                        bubbles: true
                    }));
                }
            });
        });
    }

    attachPaginationListeners() {
        const container = document.getElementById(this.containerId);
        const paginationBtns = container.querySelectorAll('.pagination-btn');
        
        paginationBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                if (!btn.disabled) {
                    this.options.currentPage = parseInt(e.target.dataset.page);
                    this.updateDisplay();
                }
            });
        });
    }

    // Public methods
    setCases(cases) {
        this.options.cases = cases;
        this.filterCases();
        this.updateDisplay();
    }

    addCase(caseItem) {
        this.options.cases.push(caseItem);
        this.filterCases();
        this.updateDisplay();
    }

    updateCase(caseId, updatedCase) {
        const index = this.options.cases.findIndex(c => c.id == caseId);
        if (index !== -1) {
            this.options.cases[index] = { ...this.options.cases[index], ...updatedCase };
            this.filterCases();
            this.updateDisplay();
        }
    }

    removeCase(caseId) {
        this.options.cases = this.options.cases.filter(c => c.id != caseId);
        this.filterCases();
        this.updateDisplay();
    }
}

// HTMX integration
document.addEventListener('htmx:afterRequest', function(event) {
    const caseLists = document.querySelectorAll('[data-component="case-list"]');
    caseLists.forEach(list => {
        // Handle dynamic updates from HTMX
        if (event.detail.target.contains(list)) {
            // Component will maintain its state
        }
    });
});

// Export for module usage
window.CaseList = CaseList;
