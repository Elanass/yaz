/**
 * CaseDetail Component
 * A reusable case detail view component with tabs, actions, and htmx support
 */

class CaseDetail {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            case: options.case || null,
            showTabs: options.showTabs !== false,
            showActions: options.showActions !== false,
            tabs: options.tabs || ['overview', 'clinical', 'imaging', 'notes'],
            activeTab: options.activeTab || 'overview',
            htmxEndpoint: options.htmxEndpoint || null,
            className: options.className || '',
            onAction: options.onAction || null,
            editable: options.editable !== false,
            ...options
        };
        this.isEditing = false;
    }

    render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container with id "${this.containerId}" not found`);
            return;
        }

        if (!this.options.case) {
            container.innerHTML = this.renderEmptyState();
            return;
        }

        const html = `
            <div class="case-detail ${this.options.className}" data-component="case-detail">
                ${this.renderHeader()}
                ${this.options.showTabs ? this.renderTabs() : ''}
                ${this.renderContent()}
                ${this.options.showActions ? this.renderActions() : ''}
            </div>
        `;

        container.innerHTML = html;
        this.attachEventListeners();
    }

    renderEmptyState() {
        return `
            <div class="case-detail-empty text-center py-12">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                <h3 class="mt-4 text-lg font-medium text-gray-900">No case selected</h3>
                <p class="mt-2 text-sm text-gray-500">Select a case from the list to view its details</p>
            </div>
        `;
    }

    renderHeader() {
        const caseItem = this.options.case;
        const statusColors = {
            active: 'bg-green-100 text-green-800',
            completed: 'bg-blue-100 text-blue-800',
            pending: 'bg-yellow-100 text-yellow-800',
            cancelled: 'bg-red-100 text-red-800'
        };

        return `
            <div class="case-detail-header bg-white border-b border-gray-200 px-6 py-4">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-4">
                        <div>
                            <h2 class="text-xl font-semibold text-gray-900">
                                ${caseItem.title || `Case #${caseItem.id}`}
                            </h2>
                            <div class="mt-1 flex items-center space-x-3">
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[caseItem.status] || 'bg-gray-100 text-gray-800'}">
                                    ${caseItem.status || 'Unknown'}
                                </span>
                                ${caseItem.priority ? `<span class="text-sm text-gray-500">Priority: ${caseItem.priority}</span>` : ''}
                                ${caseItem.date ? `<span class="text-sm text-gray-500">Created: ${new Date(caseItem.date).toLocaleDateString()}</span>` : ''}
                            </div>
                        </div>
                    </div>
                    <div class="flex items-center space-x-2">
                        ${this.options.editable ? `
                            <button class="edit-toggle-btn px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                ${this.isEditing ? 'Cancel' : 'Edit'}
                            </button>
                        ` : ''}
                        <button class="close-detail-btn p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    renderTabs() {
        return `
            <div class="case-detail-tabs bg-white border-b border-gray-200">
                <nav class="px-6 -mb-px flex space-x-8">
                    ${this.options.tabs.map(tab => `
                        <button 
                            class="tab-btn py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                                tab === this.options.activeTab 
                                    ? 'border-blue-500 text-blue-600' 
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }"
                            data-tab="${tab}"
                        >
                            ${tab.charAt(0).toUpperCase() + tab.slice(1)}
                        </button>
                    `).join('')}
                </nav>
            </div>
        `;
    }

    renderContent() {
        return `
            <div class="case-detail-content bg-white">
                <div class="tab-content p-6">
                    ${this.renderTabContent(this.options.activeTab)}
                </div>
            </div>
        `;
    }

    renderTabContent(tab) {
        const caseItem = this.options.case;
        
        switch (tab) {
            case 'overview':
                return this.renderOverviewTab(caseItem);
            case 'clinical':
                return this.renderClinicalTab(caseItem);
            case 'imaging':
                return this.renderImagingTab(caseItem);
            case 'notes':
                return this.renderNotesTab(caseItem);
            default:
                return `<div class="text-gray-500">Content for ${tab} tab</div>`;
        }
    }

    renderOverviewTab(caseItem) {
        return `
            <div class="overview-tab">
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div class="space-y-4">
                        <h3 class="text-lg font-medium text-gray-900">Patient Information</h3>
                        <div class="bg-gray-50 rounded-lg p-4 space-y-3">
                            ${this.renderField('Patient ID', caseItem.patientId, 'patientId')}
                            ${this.renderField('Patient Name', caseItem.patient, 'patient')}
                            ${this.renderField('Age', caseItem.age, 'age')}
                            ${this.renderField('Gender', caseItem.gender, 'gender')}
                            ${this.renderField('MRN', caseItem.mrn, 'mrn')}
                        </div>
                    </div>
                    <div class="space-y-4">
                        <h3 class="text-lg font-medium text-gray-900">Case Details</h3>
                        <div class="bg-gray-50 rounded-lg p-4 space-y-3">
                            ${this.renderField('Physician', caseItem.physician, 'physician')}
                            ${this.renderField('Department', caseItem.department, 'department')}
                            ${this.renderField('Priority', caseItem.priority, 'priority')}
                            ${this.renderField('Description', caseItem.description, 'description', 'textarea')}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderClinicalTab(caseItem) {
        return `
            <div class="clinical-tab">
                <div class="space-y-6">
                    <div>
                        <h3 class="text-lg font-medium text-gray-900 mb-4">Clinical Data</h3>
                        <div class="bg-gray-50 rounded-lg p-4 space-y-3">
                            ${this.renderField('Diagnosis', caseItem.diagnosis, 'diagnosis')}
                            ${this.renderField('Symptoms', caseItem.symptoms, 'symptoms', 'textarea')}
                            ${this.renderField('Medical History', caseItem.medicalHistory, 'medicalHistory', 'textarea')}
                            ${this.renderField('Medications', caseItem.medications, 'medications', 'textarea')}
                        </div>
                    </div>
                    <div>
                        <h3 class="text-lg font-medium text-gray-900 mb-4">Vital Signs</h3>
                        <div class="bg-gray-50 rounded-lg p-4">
                            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                                ${this.renderField('Blood Pressure', caseItem.bloodPressure, 'bloodPressure')}
                                ${this.renderField('Heart Rate', caseItem.heartRate, 'heartRate')}
                                ${this.renderField('Temperature', caseItem.temperature, 'temperature')}
                                ${this.renderField('Respiratory Rate', caseItem.respiratoryRate, 'respiratoryRate')}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderImagingTab(caseItem) {
        const images = caseItem.images || [];
        
        return `
            <div class="imaging-tab">
                <div class="space-y-6">
                    <div class="flex items-center justify-between">
                        <h3 class="text-lg font-medium text-gray-900">Medical Images</h3>
                        <button class="upload-image-btn px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500">
                            Upload Image
                        </button>
                    </div>
                    
                    ${images.length > 0 ? `
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            ${images.map(image => `
                                <div class="image-item bg-gray-100 rounded-lg p-4">
                                    <img src="${image.url}" alt="${image.name}" class="w-full h-48 object-cover rounded-md mb-3">
                                    <div class="space-y-1">
                                        <p class="font-medium text-sm text-gray-900">${image.name}</p>
                                        <p class="text-xs text-gray-500">${image.type} • ${image.date}</p>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    ` : `
                        <div class="text-center py-8">
                            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                            </svg>
                            <p class="mt-2 text-sm text-gray-500">No images uploaded yet</p>
                        </div>
                    `}
                </div>
            </div>
        `;
    }

    renderNotesTab(caseItem) {
        const notes = caseItem.notes || [];
        
        return `
            <div class="notes-tab">
                <div class="space-y-6">
                    <div class="flex items-center justify-between">
                        <h3 class="text-lg font-medium text-gray-900">Case Notes</h3>
                        <button class="add-note-btn px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500">
                            Add Note
                        </button>
                    </div>
                    
                    <div class="add-note-form hidden bg-gray-50 rounded-lg p-4">
                        <textarea 
                            class="new-note-text w-full p-3 border border-gray-300 rounded-md resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
                            rows="4" 
                            placeholder="Enter your note..."
                        ></textarea>
                        <div class="mt-3 flex justify-end space-x-2">
                            <button class="cancel-note-btn px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
                                Cancel
                            </button>
                            <button class="save-note-btn px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700">
                                Save Note
                            </button>
                        </div>
                    </div>
                    
                    <div class="notes-list space-y-4">
                        ${notes.length > 0 ? notes.map(note => `
                            <div class="note-item bg-white border border-gray-200 rounded-lg p-4">
                                <div class="flex items-start justify-between">
                                    <div class="flex-1">
                                        <p class="text-sm text-gray-900">${note.content}</p>
                                        <div class="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                                            <span>By: ${note.author}</span>
                                            <span>${new Date(note.date).toLocaleString()}</span>
                                        </div>
                                    </div>
                                    <button class="delete-note-btn p-1 text-gray-400 hover:text-red-600">
                                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        `).join('') : `
                            <div class="text-center py-8">
                                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                                </svg>
                                <p class="mt-2 text-sm text-gray-500">No notes added yet</p>
                            </div>
                        `}
                    </div>
                </div>
            </div>
        `;
    }

    renderField(label, value, fieldName, type = 'text') {
        if (this.isEditing) {
            if (type === 'textarea') {
                return `
                    <div class="field-group">
                        <label class="block text-sm font-medium text-gray-700 mb-1">${label}</label>
                        <textarea 
                            class="field-input w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
                            data-field="${fieldName}"
                            rows="3"
                        >${value || ''}</textarea>
                    </div>
                `;
            } else {
                return `
                    <div class="field-group">
                        <label class="block text-sm font-medium text-gray-700 mb-1">${label}</label>
                        <input 
                            type="${type}" 
                            class="field-input w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
                            data-field="${fieldName}"
                            value="${value || ''}"
                        >
                    </div>
                `;
            }
        } else {
            return `
                <div class="field-group">
                    <span class="text-sm font-medium text-gray-700">${label}:</span>
                    <span class="text-sm text-gray-900 ml-2">${value || 'Not specified'}</span>
                </div>
            `;
        }
    }

    renderActions() {
        return `
            <div class="case-detail-actions bg-gray-50 px-6 py-4 border-t border-gray-200">
                <div class="flex items-center justify-between">
                    <div class="flex space-x-3">
                        ${this.isEditing ? `
                            <button 
                                class="save-case-btn px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                ${this.options.htmxEndpoint ? `hx-put="${this.options.htmxEndpoint}/${this.options.case.id}"` : ''}
                            >
                                Save Changes
                            </button>
                        ` : `
                            <button class="action-btn px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500" data-action="complete">
                                Mark Complete
                            </button>
                            <button class="action-btn px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500" data-action="assign">
                                Assign
                            </button>
                        `}
                    </div>
                    <div class="text-sm text-gray-500">
                        Last updated: ${this.options.case.lastUpdated ? new Date(this.options.case.lastUpdated).toLocaleString() : 'Never'}
                    </div>
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        const container = document.getElementById(this.containerId);

        // Tab switching
        const tabBtns = container.querySelectorAll('.tab-btn');
        tabBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Edit toggle
        const editToggleBtn = container.querySelector('.edit-toggle-btn');
        if (editToggleBtn) {
            editToggleBtn.addEventListener('click', () => {
                this.toggleEdit();
            });
        }

        // Close detail
        const closeBtn = container.querySelector('.close-detail-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.close();
            });
        }

        // Action buttons
        const actionBtns = container.querySelectorAll('.action-btn');
        actionBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                this.handleAction(action);
            });
        });

        // Notes functionality
        this.attachNotesListeners();

        // Save case
        const saveCaseBtn = container.querySelector('.save-case-btn');
        if (saveCaseBtn) {
            saveCaseBtn.addEventListener('click', () => {
                this.saveCase();
            });
        }
    }

    attachNotesListeners() {
        const container = document.getElementById(this.containerId);
        
        // Add note
        const addNoteBtn = container.querySelector('.add-note-btn');
        const addNoteForm = container.querySelector('.add-note-form');
        const cancelNoteBtn = container.querySelector('.cancel-note-btn');
        const saveNoteBtn = container.querySelector('.save-note-btn');

        if (addNoteBtn && addNoteForm) {
            addNoteBtn.addEventListener('click', () => {
                addNoteForm.classList.remove('hidden');
            });
        }

        if (cancelNoteBtn && addNoteForm) {
            cancelNoteBtn.addEventListener('click', () => {
                addNoteForm.classList.add('hidden');
                addNoteForm.querySelector('.new-note-text').value = '';
            });
        }

        if (saveNoteBtn) {
            saveNoteBtn.addEventListener('click', () => {
                this.addNote();
            });
        }

        // Delete notes
        const deleteNoteBtns = container.querySelectorAll('.delete-note-btn');
        deleteNoteBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Implementation for deleting notes
                if (confirm('Are you sure you want to delete this note?')) {
                    e.target.closest('.note-item').remove();
                }
            });
        });
    }

    switchTab(tab) {
        this.options.activeTab = tab;
        
        // Update tab buttons
        const container = document.getElementById(this.containerId);
        const tabBtns = container.querySelectorAll('.tab-btn');
        tabBtns.forEach(btn => {
            const isActive = btn.dataset.tab === tab;
            btn.className = `tab-btn py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                isActive 
                    ? 'border-blue-500 text-blue-600' 
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`;
        });

        // Update content
        const contentContainer = container.querySelector('.tab-content');
        contentContainer.innerHTML = this.renderTabContent(tab);

        if (tab === 'notes') {
            this.attachNotesListeners();
        }
    }

    toggleEdit() {
        this.isEditing = !this.isEditing;
        this.render();
    }

    handleAction(action) {
        if (this.options.onAction) {
            this.options.onAction(action, this.options.case);
        }

        // Dispatch custom event
        const container = document.getElementById(this.containerId);
        container.dispatchEvent(new CustomEvent('caseAction', {
            detail: { action, case: this.options.case },
            bubbles: true
        }));
    }

    addNote() {
        const container = document.getElementById(this.containerId);
        const noteText = container.querySelector('.new-note-text').value;
        
        if (noteText.trim()) {
            const newNote = {
                id: Date.now(),
                content: noteText,
                author: 'Current User', // Should come from auth context
                date: new Date().toISOString()
            };

            if (!this.options.case.notes) {
                this.options.case.notes = [];
            }
            
            this.options.case.notes.unshift(newNote);
            this.switchTab('notes'); // Refresh the notes tab
        }
    }

    saveCase() {
        const container = document.getElementById(this.containerId);
        const fieldInputs = container.querySelectorAll('.field-input');
        
        fieldInputs.forEach(input => {
            const fieldName = input.dataset.field;
            this.options.case[fieldName] = input.value;
        });

        this.options.case.lastUpdated = new Date().toISOString();
        this.isEditing = false;
        this.render();

        // Dispatch save event
        container.dispatchEvent(new CustomEvent('caseSaved', {
            detail: { case: this.options.case },
            bubbles: true
        }));
    }

    close() {
        const container = document.getElementById(this.containerId);
        container.innerHTML = this.renderEmptyState();

        // Dispatch close event
        container.dispatchEvent(new CustomEvent('caseDetailClosed', {
            bubbles: true
        }));
    }

    // Public methods
    setCase(caseData) {
        this.options.case = caseData;
        this.isEditing = false;
        this.options.activeTab = 'overview';
        this.render();
    }

    updateCase(updates) {
        if (this.options.case) {
            this.options.case = { ...this.options.case, ...updates };
            this.render();
        }
    }
}

// HTMX integration
document.addEventListener('htmx:afterRequest', function(event) {
    const caseDetails = document.querySelectorAll('[data-component="case-detail"]');
    caseDetails.forEach(detail => {
        // Handle updates from HTMX
        if (event.detail.target.contains(detail)) {
            // Component will maintain its state
        }
    });
});

// Export for module usage
window.CaseDetail = CaseDetail;
