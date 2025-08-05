// Ingestion Island Component
class IngestionIsland {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.uploads = [];
        this.isProcessing = false;
        this.init();
    }

    init() {
        this.render();
        this.bindEvents();
        this.setupFileDropZone();
    }

    render() {
        this.container.innerHTML = `
            <div class="island-container bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
                <div class="island-header bg-gradient-to-r from-blue-500 to-blue-600 text-white p-6">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-3">
                            <div class="w-10 h-10 bg-white bg-opacity-20 rounded-lg flex items-center justify-center">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                                </svg>
                            </div>
                            <div>
                                <h2 class="text-xl font-semibold">Data Ingestion</h2>
                                <p class="text-blue-100 text-sm">Upload CSV cohort data or enter manually</p>
                            </div>
                        </div>
                        <div id="ingestion-status" class="flex items-center space-x-2">
                            <div class="w-3 h-3 bg-green-400 rounded-full"></div>
                            <span class="text-sm">Ready</span>
                        </div>
                    </div>
                </div>

                <div class="island-content p-6">
                    <!-- Upload Methods -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                        <!-- CSV Upload -->
                        <div class="upload-method">
                            <h3 class="text-lg font-medium text-gray-900 mb-3">CSV File Upload</h3>
                            <div id="csv-dropzone" class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors cursor-pointer">
                                <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                </svg>
                                <p class="text-sm text-gray-600 mb-2">Drag and drop your CSV file here, or</p>
                                <button type="button" class="text-blue-600 hover:text-blue-500 font-medium">Browse files</button>
                                <input type="file" id="csv-input" accept=".csv,.xlsx,.xls" class="hidden">
                                <p class="text-xs text-gray-500 mt-2">Supports CSV, Excel (.xlsx, .xls)</p>
                            </div>
                        </div>

                        <!-- Manual Entry -->
                        <div class="upload-method">
                            <h3 class="text-lg font-medium text-gray-900 mb-3">Manual Data Entry</h3>
                            <div class="bg-gray-50 rounded-lg p-6">
                                <div class="space-y-4">
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-2">Patient ID</label>
                                        <input type="text" id="patient-id" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                                    </div>
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-2">Age</label>
                                        <input type="number" id="patient-age" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                                    </div>
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-2">Stage</label>
                                        <select id="patient-stage" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                                            <option value="">Select stage</option>
                                            <option value="IA">IA</option>
                                            <option value="IB">IB</option>
                                            <option value="II">II</option>
                                            <option value="III">III</option>
                                            <option value="IV">IV</option>
                                        </select>
                                    </div>
                                    <button type="button" id="add-manual-entry" class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors">
                                        Add Patient
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Domain Selection -->
                    <div class="mb-6 p-4 bg-blue-50 rounded-lg">
                        <h3 class="text-lg font-medium text-gray-900 mb-3">Study Domain</h3>
                        <div class="flex flex-wrap gap-3">
                            <label class="inline-flex items-center">
                                <input type="radio" name="domain" value="local" class="form-radio text-blue-600" checked>
                                <span class="ml-2 text-sm text-gray-700">Local Study</span>
                            </label>
                            <label class="inline-flex items-center">
                                <input type="radio" name="domain" value="multi-center" class="form-radio text-blue-600">
                                <span class="ml-2 text-sm text-gray-700">Multi-center Study</span>
                            </label>
                        </div>
                    </div>

                    <!-- Upload Status -->
                    <div id="upload-status-list" class="space-y-3">
                        <!-- Dynamic upload status items will be added here -->
                    </div>
                </div>
            </div>
        `;
    }

    setupFileDropZone() {
        const dropzone = document.getElementById('csv-dropzone');
        const fileInput = document.getElementById('csv-input');

        dropzone.addEventListener('click', () => fileInput.click());
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('border-blue-400', 'bg-blue-50');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('border-blue-400', 'bg-blue-50');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('border-blue-400', 'bg-blue-50');
            const files = Array.from(e.dataTransfer.files);
            this.handleFileUpload(files);
        });

        fileInput.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            this.handleFileUpload(files);
        });
    }

    bindEvents() {
        document.getElementById('add-manual-entry').addEventListener('click', () => {
            this.addManualEntry();
        });
    }

    handleFileUpload(files) {
        files.forEach(file => {
            if (this.validateFile(file)) {
                const uploadId = this.generateUploadId();
                const upload = {
                    id: uploadId,
                    file: file,
                    status: 'uploading',
                    progress: 0,
                    startTime: Date.now()
                };
                
                this.uploads.push(upload);
                this.addUploadStatus(upload);
                this.processFile(upload);
            }
        });
    }

    validateFile(file) {
        const validTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
        const maxSize = 10 * 1024 * 1024; // 10MB

        if (!validTypes.includes(file.type) && !file.name.match(/\.(csv|xlsx|xls)$/i)) {
            this.showNotification('Invalid file type. Please upload CSV or Excel files.', 'error');
            return false;
        }

        if (file.size > maxSize) {
            this.showNotification('File too large. Maximum size is 10MB.', 'error');
            return false;
        }

        return true;
    }

    async processFile(upload) {
        try {
            this.updateUploadStatus(upload.id, 'processing', 25);
            
            // Simulate file processing
            const reader = new FileReader();
            reader.onload = async (e) => {
                const content = e.target.result;
                
                this.updateUploadStatus(upload.id, 'analyzing', 50);
                
                // Parse CSV content
                const data = this.parseCSV(content);
                
                this.updateUploadStatus(upload.id, 'uploading', 75);
                
                // Send to API
                const domain = document.querySelector('input[name="domain"]:checked').value;
                await this.sendToAPI(data, domain, upload.id);
                
                this.updateUploadStatus(upload.id, 'completed', 100);
                this.showNotification(`Successfully processed ${data.length} records`, 'success');
            };
            
            reader.readAsText(upload.file);
        } catch (error) {
            this.updateUploadStatus(upload.id, 'failed', 0);
            this.showNotification('Failed to process file: ' + error.message, 'error');
        }
    }

    parseCSV(content) {
        const lines = content.split('\n');
        const headers = lines[0].split(',').map(h => h.trim());
        const data = [];

        for (let i = 1; i < lines.length; i++) {
            if (lines[i].trim()) {
                const values = lines[i].split(',').map(v => v.trim());
                const record = {};
                headers.forEach((header, index) => {
                    record[header] = values[index] || '';
                });
                data.push(record);
            }
        }

        return data;
    }

    async sendToAPI(data, domain, uploadId) {
        const response = await fetch('/api/v1/data/ingest', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                data: data,
                domain: domain,
                uploadId: uploadId,
                timestamp: new Date().toISOString()
            })
        });

        if (!response.ok) {
            throw new Error('Failed to upload data to server');
        }

        return await response.json();
    }

    addManualEntry() {
        const patientId = document.getElementById('patient-id').value;
        const age = document.getElementById('patient-age').value;
        const stage = document.getElementById('patient-stage').value;

        if (!patientId || !age || !stage) {
            this.showNotification('Please fill in all fields', 'warning');
            return;
        }

        const entry = {
            patient_id: patientId,
            age: parseInt(age),
            stage: stage,
            entry_method: 'manual',
            timestamp: new Date().toISOString()
        };

        const domain = document.querySelector('input[name="domain"]:checked').value;
        this.sendToAPI([entry], domain, this.generateUploadId());

        // Clear form
        document.getElementById('patient-id').value = '';
        document.getElementById('patient-age').value = '';
        document.getElementById('patient-stage').value = '';

        this.showNotification('Patient data added successfully', 'success');
    }

    addUploadStatus(upload) {
        const statusList = document.getElementById('upload-status-list');
        const statusItem = document.createElement('div');
        statusItem.id = `upload-${upload.id}`;
        statusItem.className = 'upload-status-item p-4 bg-gray-50 rounded-lg';
        
        statusItem.innerHTML = `
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <div class="status-icon w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <svg class="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                    </div>
                    <div>
                        <p class="text-sm font-medium text-gray-900">${upload.file.name}</p>
                        <p class="text-xs text-gray-500">${this.formatFileSize(upload.file.size)}</p>
                    </div>
                </div>
                <div class="text-right">
                    <p class="status-text text-sm font-medium text-blue-600">Uploading...</p>
                    <div class="w-32 bg-gray-200 rounded-full h-2 mt-1">
                        <div class="progress-bar bg-blue-600 h-2 rounded-full transition-all duration-300" style="width: 0%"></div>
                    </div>
                </div>
            </div>
        `;
        
        statusList.appendChild(statusItem);
    }

    updateUploadStatus(uploadId, status, progress) {
        const statusItem = document.getElementById(`upload-${uploadId}`);
        if (!statusItem) return;

        const statusText = statusItem.querySelector('.status-text');
        const progressBar = statusItem.querySelector('.progress-bar');
        const statusIcon = statusItem.querySelector('.status-icon');

        const statusMessages = {
            uploading: 'Uploading...',
            processing: 'Processing...',
            analyzing: 'Analyzing data...',
            completed: 'Completed',
            failed: 'Failed'
        };

        statusText.textContent = statusMessages[status] || status;
        progressBar.style.width = `${progress}%`;

        if (status === 'completed') {
            statusIcon.innerHTML = `
                <svg class="w-4 h-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
            `;
            statusIcon.className = 'status-icon w-8 h-8 bg-green-100 rounded-full flex items-center justify-center';
            statusText.className = 'status-text text-sm font-medium text-green-600';
            progressBar.className = 'progress-bar bg-green-600 h-2 rounded-full transition-all duration-300';
        } else if (status === 'failed') {
            statusIcon.innerHTML = `
                <svg class="w-4 h-4 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            `;
            statusIcon.className = 'status-icon w-8 h-8 bg-red-100 rounded-full flex items-center justify-center';
            statusText.className = 'status-text text-sm font-medium text-red-600';
            progressBar.className = 'progress-bar bg-red-600 h-2 rounded-full transition-all duration-300';
        }
    }

    generateUploadId() {
        return 'upload_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    showNotification(message, type = 'info') {
        // Integration with existing notification system
        if (window.surgifyApp && window.surgifyApp.showNotification) {
            window.surgifyApp.showNotification(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('ingestion-island')) {
        window.ingestionIsland = new IngestionIsland('ingestion-island');
    }
});
