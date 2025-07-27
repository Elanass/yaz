/**
 * Gun.js Integration for Cohort Management
 * Handles offline-first data synchronization for cohort studies
 */

// Initialize Gun instance
const gun = Gun(['https://gun-server.example.com/gun']);

// Cohort data management namespace
window.CohortGun = {
    // Local storage for offline cohort data
    localCohorts: gun.get('local_cohorts'),
    
    // User's cohort studies
    userCohorts: null,
    
    // Current user context
    currentUser: null,
    
    /**
     * Initialize cohort synchronization
     */
    async init(userId) {
        this.currentUser = userId;
        this.userCohorts = gun.get(`user_cohorts_${userId}`);
        
        // Setup offline detection
        this.setupOfflineSync();
        
        // Setup real-time updates
        this.setupRealTimeSync();
        
        console.log('Cohort Gun.js initialized for user:', userId);
    },
    
    /**
     * Save cohort study locally and sync
     */
    async saveCohortStudy(cohortData) {
        const cohortId = cohortData.id || `cohort_${Date.now()}`;
        cohortData.id = cohortId;
        cohortData.lastModified = Date.now();
        cohortData.syncStatus = navigator.onLine ? 'synced' : 'pending';
        
        // Save locally
        this.userCohorts.get(cohortId).put(cohortData);
        
        // If online, sync to server
        if (navigator.onLine) {
            try {
                await this.syncToServer(cohortData);
                cohortData.syncStatus = 'synced';
                this.userCohorts.get(cohortId).put(cohortData);
            } catch (error) {
                console.error('Failed to sync cohort to server:', error);
                cohortData.syncStatus = 'error';
                this.userCohorts.get(cohortId).put(cohortData);
            }
        }
        
        return cohortData;
    },
    
    /**
     * Get cohort studies with offline support
     */
    async getCohortStudies() {
        return new Promise((resolve) => {
            const cohorts = [];
            
            this.userCohorts.once((data, key) => {
                if (data && typeof data === 'object') {
                    Object.keys(data).forEach(cohortId => {
                        if (cohortId !== '_' && data[cohortId]) {
                            cohorts.push({
                                id: cohortId,
                                ...data[cohortId]
                            });
                        }
                    });
                }
                
                // Sort by lastModified
                cohorts.sort((a, b) => (b.lastModified || 0) - (a.lastModified || 0));
                resolve(cohorts);
            });
        });
    },
    
    /**
     * Save patient data with offline support
     */
    async savePatientData(cohortId, patientData) {
        const cohortPatients = gun.get(`cohort_patients_${cohortId}`);
        const patientId = patientData.patient_id || `patient_${Date.now()}`;
        
        patientData.id = patientId;
        patientData.lastModified = Date.now();
        patientData.syncStatus = navigator.onLine ? 'synced' : 'pending';
        
        // Save locally
        cohortPatients.get(patientId).put(patientData);
        
        // Update cohort patient count
        this.updateCohortStats(cohortId);
        
        // Sync if online
        if (navigator.onLine) {
            try {
                await this.syncPatientToServer(cohortId, patientData);
            } catch (error) {
                console.error('Failed to sync patient data:', error);
            }
        }
        
        return patientData;
    },
    
    /**
     * Get patients for a cohort
     */
    async getCohortPatients(cohortId) {
        return new Promise((resolve) => {
            const patients = [];
            const cohortPatients = gun.get(`cohort_patients_${cohortId}`);
            
            cohortPatients.once((data, key) => {
                if (data && typeof data === 'object') {
                    Object.keys(data).forEach(patientId => {
                        if (patientId !== '_' && data[patientId]) {
                            patients.push({
                                id: patientId,
                                ...data[patientId]
                            });
                        }
                    });
                }
                
                resolve(patients);
            });
        });
    },
    
    /**
     * Save inference session results
     */
    async saveInferenceResults(sessionId, results) {
        const sessionResults = gun.get(`session_results_${sessionId}`);
        
        results.lastModified = Date.now();
        results.syncStatus = navigator.onLine ? 'synced' : 'pending';
        
        // Save locally
        sessionResults.put(results);
        
        // Sync if online
        if (navigator.onLine) {
            try {
                await this.syncResultsToServer(sessionId, results);
            } catch (error) {
                console.error('Failed to sync results:', error);
            }
        }
        
        return results;
    },
    
    /**
     * Get inference session results
     */
    async getInferenceResults(sessionId) {
        return new Promise((resolve) => {
            const sessionResults = gun.get(`session_results_${sessionId}`);
            
            sessionResults.once((data) => {
                resolve(data || null);
            });
        });
    },
    
    /**
     * Setup offline synchronization
     */
    setupOfflineSync() {
        // Listen for online/offline events
        window.addEventListener('online', () => {
            this.syncPendingData();
        });
        
        window.addEventListener('offline', () => {
            this.showOfflineNotification();
        });
        
        // Periodic sync when online
        setInterval(() => {
            if (navigator.onLine) {
                this.syncPendingData();
            }
        }, 30000); // Every 30 seconds
    },
    
    /**
     * Setup real-time synchronization
     */
    setupRealTimeSync() {
        // Listen for changes to user's cohorts
        this.userCohorts.on((data, key) => {
            if (key !== '_' && data) {
                this.handleCohortUpdate(key, data);
            }
        });
        
        // Listen for processing status updates
        gun.get('processing_updates').on((data, key) => {
            if (data && data.userId === this.currentUser) {
                this.handleProcessingUpdate(data);
            }
        });
    },
    
    /**
     * Sync pending data when coming back online
     */
    async syncPendingData() {
        const cohorts = await this.getCohortStudies();
        
        for (const cohort of cohorts) {
            if (cohort.syncStatus === 'pending') {
                try {
                    await this.syncToServer(cohort);
                    cohort.syncStatus = 'synced';
                    this.userCohorts.get(cohort.id).put(cohort);
                } catch (error) {
                    console.error('Failed to sync cohort:', error);
                }
            }
        }
        
        this.showSyncCompleteNotification();
    },
    
    /**
     * Sync cohort data to server
     */
    async syncToServer(cohortData) {
        const response = await fetch('/api/v1/cohorts/sync', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.getAuthToken()}`
            },
            body: JSON.stringify(cohortData)
        });
        
        if (!response.ok) {
            throw new Error(`Sync failed: ${response.statusText}`);
        }
        
        return response.json();
    },
    
    /**
     * Sync patient data to server
     */
    async syncPatientToServer(cohortId, patientData) {
        const response = await fetch(`/api/v1/cohorts/${cohortId}/patients/sync`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.getAuthToken()}`
            },
            body: JSON.stringify(patientData)
        });
        
        if (!response.ok) {
            throw new Error(`Patient sync failed: ${response.statusText}`);
        }
        
        return response.json();
    },
    
    /**
     * Sync results to server
     */
    async syncResultsToServer(sessionId, results) {
        const response = await fetch(`/api/v1/cohorts/sessions/${sessionId}/results/sync`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.getAuthToken()}`
            },
            body: JSON.stringify(results)
        });
        
        if (!response.ok) {
            throw new Error(`Results sync failed: ${response.statusText}`);
        }
        
        return response.json();
    },
    
    /**
     * Generic sync pending data utility
     */
    async genericSync(storeName, apiEndpoint) {
      const items = await this.getStoreItems(storeName);
      for (const item of items) {
        try {
          const res = await fetch(apiEndpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(item)
          });
          if (res.ok) {
            this.clearStoreItem(storeName, item.id);
          }
        } catch (err) {
          console.error(`Failed to sync ${storeName}:`, err);
        }
      }
    },
    
    /**
     * Update cohort statistics
     */
    async updateCohortStats(cohortId) {
        const patients = await this.getCohortPatients(cohortId);
        const cohort = await this.getCohortStudy(cohortId);
        
        if (cohort) {
            cohort.totalPatients = patients.length;
            cohort.lastModified = Date.now();
            this.userCohorts.get(cohortId).put(cohort);
        }
    },
    
    /**
     * Get single cohort study
     */
    async getCohortStudy(cohortId) {
        return new Promise((resolve) => {
            this.userCohorts.get(cohortId).once((data) => {
                resolve(data || null);
            });
        });
    },
    
    /**
     * Handle cohort updates from other devices/users
     */
    handleCohortUpdate(cohortId, data) {
        // Emit custom event for UI updates
        const event = new CustomEvent('cohortUpdated', {
            detail: { cohortId, data }
        });
        window.dispatchEvent(event);
    },
    
    /**
     * Handle processing status updates
     */
    handleProcessingUpdate(update) {
        // Emit custom event for UI updates
        const event = new CustomEvent('processingUpdate', {
            detail: update
        });
        window.dispatchEvent(event);
    },
    
    /**
     * Show offline notification
     */
    showOfflineNotification() {
        if (window.GastricADCI && window.GastricADCI.showNotification) {
            window.GastricADCI.showNotification(
                'You are offline. Data will be synced when connection is restored.',
                'warning'
            );
        }
    },
    
    /**
     * Show sync complete notification
     */
    showSyncCompleteNotification() {
        if (window.GastricADCI && window.GastricADCI.showNotification) {
            window.GastricADCI.showNotification(
                'Data synchronized successfully.',
                'success'
            );
        }
    },
    
    /**
     * Get authentication token
     */
    getAuthToken() {
        // Get token from localStorage or cookies
        return localStorage.getItem('authToken') || '';
    },
    
    /**
     * Clear local cohort data
     */
    async clearLocalData() {
        if (this.userCohorts) {
            this.userCohorts.put(null);
        }
        
        // Clear related data
        const cohorts = await this.getCohortStudies();
        for (const cohort of cohorts) {
            gun.get(`cohort_patients_${cohort.id}`).put(null);
        }
    },
    
    /**
     * Export cohort data for backup
     */
    async exportLocalData() {
        const cohorts = await this.getCohortStudies();
        const exportData = {
            cohorts: cohorts,
            patients: {},
            timestamp: Date.now()
        };
        
        // Get patients for each cohort
        for (const cohort of cohorts) {
            exportData.patients[cohort.id] = await this.getCohortPatients(cohort.id);
        }
        
        return exportData;
    },
    
    /**
     * Import cohort data from backup
     */
    async importLocalData(importData) {
        if (!importData.cohorts) return;
        
        // Import cohorts
        for (const cohort of importData.cohorts) {
            await this.saveCohortStudy(cohort);
        }
        
        // Import patients
        if (importData.patients) {
            for (const cohortId in importData.patients) {
                const patients = importData.patients[cohortId];
                for (const patient of patients) {
                    await this.savePatientData(cohortId, patient);
                }
            }
        }
    }
};

// Listen for cohort updates in the UI
window.addEventListener('cohortUpdated', (event) => {
    const { cohortId, data } = event.detail;
    
    // Update UI elements
    const cohortElement = document.querySelector(`[data-cohort-id="${cohortId}"]`);
    if (cohortElement) {
        // Update cohort display
        updateCohortDisplay(cohortElement, data);
    }
});

// Listen for processing updates
window.addEventListener('processingUpdate', (event) => {
    const update = event.detail;
    
    // Update processing status in UI
    const statusElement = document.querySelector(`[data-session-id="${update.sessionId}"]`);
    if (statusElement) {
        updateProcessingStatus(statusElement, update);
    }
});

/**
 * Update cohort display in UI
 */
function updateCohortDisplay(element, data) {
    const statusBadge = element.querySelector('.cohort-status-badge');
    if (statusBadge) {
        statusBadge.textContent = data.status;
        statusBadge.className = `cohort-status-badge ${data.status}`;
    }
    
    const patientCount = element.querySelector('.patient-count');
    if (patientCount) {
        patientCount.textContent = data.totalPatients || 0;
    }
}

/**
 * Update processing status in UI
 */
function updateProcessingStatus(element, update) {
    const progressBar = element.querySelector('.progress-bar-fill');
    if (progressBar) {
        progressBar.style.width = `${update.progress || 0}%`;
    }
    
    const statusText = element.querySelector('.status-text');
    if (statusText) {
        statusText.textContent = update.status;
    }
}
