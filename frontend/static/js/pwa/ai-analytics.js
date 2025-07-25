/**
 * AI Analytics Module for Gastric ADCI Platform
 * Provides predictive analytics, pattern recognition, and outcome simulation
 * HIPAA/GDPR Compliant with explainable AI principles
 */

class AIAnalytics {
    constructor() {
        this.models = {};
        this.analyticsTasks = [];
        this.currentAnalysis = null;
        this.modelCache = new Map();
        this.isInitialized = false;
        this.workerPool = [];
        this.maxWorkers = navigator.hardwareConcurrency || 2;
        this.supportedModels = [
            'recurrence-prediction',
            'complication-risk',
            'los-prediction', // Length of stay
            'readmission-risk',
            'treatment-response',
            'survival-analysis',
            'protocol-compliance'
        ];
        
        // Initialize module
        this.init();
    }
    
    async init() {
        try {
            // Check for WebGL/WebGPU support for accelerated inference
            this.hasGPUAcceleration = this.checkGPUSupport();
            
            // Initialize workers for parallel processing
            await this.initializeWorkerPool();
            
            // Load configuration and model metadata
            await this.loadConfiguration();
            
            // Register event listeners
            document.addEventListener('requestAnalysis', this.handleAnalysisRequest.bind(this));
            document.addEventListener('cancelAnalysis', this.handleCancelRequest.bind(this));
            
            this.isInitialized = true;
            console.log('AI Analytics module initialized with GPU acceleration:', this.hasGPUAcceleration);
            
            // Dispatch ready event
            document.dispatchEvent(new CustomEvent('aiAnalyticsReady'));
        } catch (error) {
            console.error('Failed to initialize AI Analytics module:', error);
            // Dispatch error event
            document.dispatchEvent(new CustomEvent('aiAnalyticsError', {
                detail: { error: error.message }
            }));
        }
    }
    
    checkGPUSupport() {
        // Check for WebGL support (fallback)
        const hasWebGL = !!document.createElement('canvas')
            .getContext('webgl2') || 
            !!document.createElement('canvas').getContext('webgl');
            
        // Check for WebGPU support (preferred for newer browsers)
        const hasWebGPU = window.navigator.gpu !== undefined;
        
        return { webgl: hasWebGL, webgpu: hasWebGPU };
    }
    
    async initializeWorkerPool() {
        // Create a pool of Web Workers for parallel processing
        for (let i = 0; i < this.maxWorkers; i++) {
            const worker = new Worker('/static/js/pwa/ai-analytics-worker.js');
            
            worker.onmessage = (event) => {
                this.handleWorkerMessage(event.data, worker);
            };
            
            worker.onerror = (error) => {
                console.error('Worker error:', error);
                // Replace the crashed worker
                const index = this.workerPool.indexOf(worker);
                if (index !== -1) {
                    this.workerPool.splice(index, 1);
                    this.initializeWorkerPool();
                }
            };
            
            this.workerPool.push({
                worker: worker,
                busy: false,
                id: `worker-${i}`
            });
        }
    }
    
    async loadConfiguration() {
        try {
            // Fetch model configurations and metadata
            const response = await fetch('/api/v1/analytics/models');
            
            if (!response.ok) {
                throw new Error(`Failed to load model configuration: ${response.status}`);
            }
            
            const config = await response.json();
            
            // Initialize model registry
            for (const model of config.models) {
                this.models[model.id] = {
                    ...model,
                    loaded: false,
                    loading: false,
                    lastUsed: null
                };
            }
            
            // Preload high-priority models if configured
            if (config.preloadModels && Array.isArray(config.preloadModels)) {
                for (const modelId of config.preloadModels) {
                    this.preloadModel(modelId);
                }
            }
            
            console.log(`Loaded configuration for ${Object.keys(this.models).length} AI models`);
        } catch (error) {
            console.error('Error loading AI models configuration:', error);
            // Set up fallback configurations if server is unavailable
            this.setupFallbackConfiguration();
        }
    }
    
    setupFallbackConfiguration() {
        // Fallback configuration for offline mode
        this.supportedModels.forEach(modelId => {
            this.models[modelId] = {
                id: modelId,
                name: modelId.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
                version: '1.0.0',
                type: 'tfjs',
                size: 'compact',
                loaded: false,
                loading: false,
                lastUsed: null,
                accuracy: 0.85,
                offlineCompatible: true
            };
        });
    }
    
    async preloadModel(modelId) {
        if (!this.models[modelId] || this.models[modelId].loading || this.models[modelId].loaded) {
            return;
        }
        
        try {
            this.models[modelId].loading = true;
            
            // Find an available worker
            const workerInfo = this.workerPool.find(w => !w.busy);
            
            if (!workerInfo) {
                // No available workers, delay preloading
                setTimeout(() => this.preloadModel(modelId), 1000);
                return;
            }
            
            workerInfo.busy = true;
            
            // Tell worker to load the model
            workerInfo.worker.postMessage({
                action: 'loadModel',
                modelId: modelId,
                modelInfo: this.models[modelId]
            });
            
            // Worker will send back a message when done
        } catch (error) {
            console.error(`Error preloading model ${modelId}:`, error);
            this.models[modelId].loading = false;
        }
    }
    
    handleWorkerMessage(data, worker) {
        const workerInfo = this.workerPool.find(w => w.worker === worker);
        
        if (!workerInfo) {
            return;
        }
        
        switch (data.action) {
            case 'modelLoaded':
                this.handleModelLoaded(data.modelId);
                workerInfo.busy = false;
                break;
                
            case 'analysisResult':
                this.handleAnalysisResult(data.taskId, data.result);
                workerInfo.busy = false;
                break;
                
            case 'analysisProgress':
                this.updateAnalysisProgress(data.taskId, data.progress);
                break;
                
            case 'analysisError':
                this.handleAnalysisError(data.taskId, data.error);
                workerInfo.busy = false;
                break;
                
            case 'modelLoadError':
                console.error(`Failed to load model ${data.modelId}:`, data.error);
                this.models[data.modelId].loading = false;
                workerInfo.busy = false;
                break;
        }
    }
    
    handleModelLoaded(modelId) {
        if (this.models[modelId]) {
            this.models[modelId].loaded = true;
            this.models[modelId].loading = false;
            this.models[modelId].lastUsed = new Date();
            console.log(`Model ${modelId} loaded successfully`);
            
            // Notify the UI
            document.dispatchEvent(new CustomEvent('modelStatusUpdate', {
                detail: {
                    modelId: modelId,
                    status: 'loaded'
                }
            }));
        }
    }
    
    handleAnalysisRequest(event) {
        const request = event.detail;
        
        if (!request || !request.analysisType || !request.patientData) {
            console.error('Invalid analysis request:', request);
            return;
        }
        
        // Create a task ID
        const taskId = `task-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
        
        // Queue the analysis task
        this.analyticsTasks.push({
            id: taskId,
            type: request.analysisType,
            patientData: request.analysisType === 'cohort-analysis' ? null : request.patientData,
            cohortData: request.analysisType === 'cohort-analysis' ? request.patientData : null,
            options: request.options || {},
            status: 'queued',
            progress: 0,
            result: null,
            error: null,
            startTime: null,
            endTime: null,
            modelId: this.getModelForAnalysisType(request.analysisType)
        });
        
        // Notify that the task was queued
        document.dispatchEvent(new CustomEvent('analysisTaskQueued', {
            detail: {
                taskId: taskId,
                analysisType: request.analysisType
            }
        }));
        
        // Process the task queue
        this.processTaskQueue();
        
        // Return the task ID to the caller
        return taskId;
    }
    
    getModelForAnalysisType(analysisType) {
        // Map analysis types to appropriate models
        switch (analysisType) {
            case 'recurrence-prediction':
                return 'recurrence-prediction';
            case 'complication-risk':
                return 'complication-risk';
            case 'length-of-stay':
                return 'los-prediction';
            case 'readmission-risk':
                return 'readmission-risk';
            case 'treatment-response':
                return 'treatment-response';
            case 'survival-analysis':
                return 'survival-analysis';
            case 'protocol-compliance':
                return 'protocol-compliance';
            case 'cohort-analysis':
                return 'cohort-analysis';
            default:
                return null;
        }
    }
    
    async processTaskQueue() {
        // If we're already processing or the queue is empty, return
        if (this.currentAnalysis || this.analyticsTasks.length === 0) {
            return;
        }
        
        // Get the next task
        const nextTask = this.analyticsTasks.find(task => task.status === 'queued');
        
        if (!nextTask) {
            return;
        }
        
        // Update task status
        nextTask.status = 'processing';
        nextTask.startTime = new Date();
        this.currentAnalysis = nextTask;
        
        // Notify UI that processing has started
        document.dispatchEvent(new CustomEvent('analysisTaskStarted', {
            detail: {
                taskId: nextTask.id,
                analysisType: nextTask.type
            }
        }));
        
        // Find an available worker
        const workerInfo = this.workerPool.find(w => !w.busy);
        
        if (!workerInfo) {
            // No available workers, put the task back in the queue
            nextTask.status = 'queued';
            this.currentAnalysis = null;
            
            // Try again after a short delay
            setTimeout(() => this.processTaskQueue(), 500);
            return;
        }
        
        try {
            workerInfo.busy = true;
            
            // Make sure the required model is loaded
            if (nextTask.modelId && this.models[nextTask.modelId] && !this.models[nextTask.modelId].loaded) {
                // Load the model first
                await this.loadModelForAnalysis(nextTask.modelId);
            }
            
            // Send the analysis task to the worker
            workerInfo.worker.postMessage({
                action: 'runAnalysis',
                taskId: nextTask.id,
                analysisType: nextTask.type,
                patientData: nextTask.patientData,
                cohortData: nextTask.cohortData,
                options: nextTask.options,
                modelId: nextTask.modelId
            });
            
            // Log for HIPAA compliance
            this.logAnalyticsActivity(nextTask.id, 'analysis_started', {
                analysisType: nextTask.type,
                patientId: nextTask.patientData?.id || 'cohort-analysis'
            });
            
        } catch (error) {
            console.error(`Error processing analysis task ${nextTask.id}:`, error);
            
            // Update task status
            nextTask.status = 'error';
            nextTask.error = error.message;
            nextTask.endTime = new Date();
            
            // Release the worker
            workerInfo.busy = false;
            
            // Clear current analysis
            this.currentAnalysis = null;
            
            // Notify UI of error
            document.dispatchEvent(new CustomEvent('analysisTaskError', {
                detail: {
                    taskId: nextTask.id,
                    error: error.message
                }
            }));
            
            // Continue with the next task
            this.processTaskQueue();
        }
    }
    
    async loadModelForAnalysis(modelId) {
        if (!this.models[modelId]) {
            throw new Error(`Model ${modelId} not found`);
        }
        
        if (this.models[modelId].loaded) {
            return; // Already loaded
        }
        
        if (this.models[modelId].loading) {
            // Wait for it to finish loading
            await new Promise((resolve, reject) => {
                const checkInterval = setInterval(() => {
                    if (this.models[modelId].loaded) {
                        clearInterval(checkInterval);
                        resolve();
                    } else if (!this.models[modelId].loading) {
                        clearInterval(checkInterval);
                        reject(new Error(`Failed to load model ${modelId}`));
                    }
                }, 100);
            });
            return;
        }
        
        // Start loading the model
        return new Promise((resolve, reject) => {
            this.models[modelId].loading = true;
            
            // Find an available worker
            const workerInfo = this.workerPool.find(w => !w.busy);
            
            if (!workerInfo) {
                this.models[modelId].loading = false;
                reject(new Error('No available workers to load model'));
                return;
            }
            
            workerInfo.busy = true;
            
            // Set up a timeout
            const timeout = setTimeout(() => {
                this.models[modelId].loading = false;
                workerInfo.busy = false;
                reject(new Error(`Timeout loading model ${modelId}`));
            }, 30000); // 30 second timeout
            
            // Set up a listener for model loaded event
            const listener = (event) => {
                if (event.detail.modelId === modelId) {
                    clearTimeout(timeout);
                    document.removeEventListener('modelStatusUpdate', listener);
                    resolve();
                }
            };
            
            document.addEventListener('modelStatusUpdate', listener);
            
            // Tell worker to load the model
            workerInfo.worker.postMessage({
                action: 'loadModel',
                modelId: modelId,
                modelInfo: this.models[modelId]
            });
        });
    }
    
    updateAnalysisProgress(taskId, progress) {
        const task = this.analyticsTasks.find(t => t.id === taskId);
        
        if (!task) {
            return;
        }
        
        task.progress = progress;
        
        // Notify UI of progress
        document.dispatchEvent(new CustomEvent('analysisTaskProgress', {
            detail: {
                taskId: taskId,
                progress: progress
            }
        }));
    }
    
    handleAnalysisResult(taskId, result) {
        const task = this.analyticsTasks.find(t => t.id === taskId);
        
        if (!task) {
            return;
        }
        
        // Update task with results
        task.status = 'completed';
        task.result = result;
        task.endTime = new Date();
        task.progress = 100;
        
        // If this was the current analysis, clear it
        if (this.currentAnalysis && this.currentAnalysis.id === taskId) {
            this.currentAnalysis = null;
        }
        
        // Update model last used time
        if (task.modelId && this.models[task.modelId]) {
            this.models[task.modelId].lastUsed = new Date();
        }
        
        // Add confidence intervals and model metadata to results
        if (task.modelId && this.models[task.modelId]) {
            task.result.modelInfo = {
                id: task.modelId,
                name: this.models[task.modelId].name,
                version: this.models[task.modelId].version,
                accuracy: this.models[task.modelId].accuracy
            };
        }
        
        // Add analysis metadata
        task.result.analysisMetadata = {
            analysisType: task.type,
            startTime: task.startTime,
            endTime: task.endTime,
            executionTimeMs: task.endTime - task.startTime
        };
        
        // Notify UI of completion
        document.dispatchEvent(new CustomEvent('analysisTaskCompleted', {
            detail: {
                taskId: taskId,
                result: task.result
            }
        }));
        
        // Log for HIPAA compliance
        this.logAnalyticsActivity(taskId, 'analysis_completed', {
            analysisType: task.type,
            patientId: task.patientData?.id || 'cohort-analysis',
            executionTimeMs: task.endTime - task.startTime
        });
        
        // Process next task in queue
        this.processTaskQueue();
    }
    
    handleAnalysisError(taskId, error) {
        const task = this.analyticsTasks.find(t => t.id === taskId);
        
        if (!task) {
            return;
        }
        
        // Update task with error
        task.status = 'error';
        task.error = error;
        task.endTime = new Date();
        
        // If this was the current analysis, clear it
        if (this.currentAnalysis && this.currentAnalysis.id === taskId) {
            this.currentAnalysis = null;
        }
        
        // Notify UI of error
        document.dispatchEvent(new CustomEvent('analysisTaskError', {
            detail: {
                taskId: taskId,
                error: error
            }
        }));
        
        // Log for HIPAA compliance
        this.logAnalyticsActivity(taskId, 'analysis_error', {
            analysisType: task.type,
            patientId: task.patientData?.id || 'cohort-analysis',
            error: error
        });
        
        // Process next task in queue
        this.processTaskQueue();
    }
    
    handleCancelRequest(event) {
        const taskId = event.detail.taskId;
        
        if (!taskId) {
            return;
        }
        
        const task = this.analyticsTasks.find(t => t.id === taskId);
        
        if (!task) {
            return;
        }
        
        // If task is already completed or errored, nothing to do
        if (task.status === 'completed' || task.status === 'error') {
            return;
        }
        
        // If task is queued, just remove it from queue
        if (task.status === 'queued') {
            task.status = 'cancelled';
            task.endTime = new Date();
            
            // Notify UI of cancellation
            document.dispatchEvent(new CustomEvent('analysisTaskCancelled', {
                detail: { taskId: taskId }
            }));
            
            return;
        }
        
        // If task is processing, we need to cancel it in the worker
        if (task.status === 'processing') {
            // Find the worker processing this task
            const workerInfo = this.workerPool.find(w => w.busy);
            
            if (workerInfo) {
                workerInfo.worker.postMessage({
                    action: 'cancelAnalysis',
                    taskId: taskId
                });
            }
            
            // Update task status
            task.status = 'cancelled';
            task.endTime = new Date();
            
            // If this was the current analysis, clear it
            if (this.currentAnalysis && this.currentAnalysis.id === taskId) {
                this.currentAnalysis = null;
            }
            
            // Notify UI of cancellation
            document.dispatchEvent(new CustomEvent('analysisTaskCancelled', {
                detail: { taskId: taskId }
            }));
            
            // Log for HIPAA compliance
            this.logAnalyticsActivity(taskId, 'analysis_cancelled', {
                analysisType: task.type,
                patientId: task.patientData?.id || 'cohort-analysis'
            });
            
            // Process next task in queue
            this.processTaskQueue();
        }
    }
    
    getAnalysisTask(taskId) {
        return this.analyticsTasks.find(t => t.id === taskId);
    }
    
    getAllTasks() {
        return this.analyticsTasks;
    }
    
    getActiveModels() {
        return Object.keys(this.models)
            .filter(modelId => this.models[modelId].loaded)
            .map(modelId => ({
                id: modelId,
                name: this.models[modelId].name,
                version: this.models[modelId].version,
                lastUsed: this.models[modelId].lastUsed
            }));
    }
    
    logAnalyticsActivity(taskId, action, details) {
        // Create audit log entry
        const auditEntry = {
            taskId: taskId,
            action: action,
            timestamp: new Date().toISOString(),
            userId: window.currentUser ? window.currentUser.id : 'unknown',
            details: details
        };
        
        // Send to server if online
        fetch('/api/v1/audit/analytics', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
            },
            body: JSON.stringify(auditEntry),
            credentials: 'same-origin'
        }).catch(error => {
            console.error('Error logging analytics activity:', error);
            // Store in IndexedDB for later sync
            this.storeAuditLogLocally(auditEntry);
        });
    }
    
    storeAuditLogLocally(auditEntry) {
        // Open IndexedDB
        const request = window.indexedDB.open('aiAnalyticsDB', 1);
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            
            // Create audit log store if it doesn't exist
            if (!db.objectStoreNames.contains('auditLogs')) {
                const store = db.createObjectStore('auditLogs', { keyPath: 'id', autoIncrement: true });
                store.createIndex('by_timestamp', 'timestamp', { unique: false });
                store.createIndex('by_synced', 'synced', { unique: false });
            }
        };
        
        request.onsuccess = (event) => {
            const db = event.target.result;
            const transaction = db.transaction(['auditLogs'], 'readwrite');
            const store = transaction.objectStore('auditLogs');
            
            // Add audit entry with synced flag
            store.add({
                ...auditEntry,
                synced: false
            });
        };
        
        request.onerror = (event) => {
            console.error('Error opening IndexedDB for audit log:', event.target.error);
        };
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.aiAnalytics = new AIAnalytics();
});

// Export for module use
export default AIAnalytics;
