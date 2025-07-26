/**
 * Surgical Instrument Tracking Module for Gastric ADCI Platform
 * HIPAA/GDPR Compliant real-time instrument tracking and analytics
 */

import { openDatabase } from '../utils/db-utils.js';

class InstrumentTracking {
    constructor() {
        this.instruments = new Map();
        this.scanners = [];
        this.activeCase = null;
        this.trackingHistory = [];
        this.missingInstruments = [];
        this.sterilizationStatus = new Map();
        this.instrumentSets = new Map();
        this.preferences = {};
        this.syncStatus = 'online';
        this.dbInstance = null;
        
        // Initialize module
        this.init();
    }
    
    async init() {
        try {
            // Set up IndexedDB for offline storage
            await this.setupDatabase();
            
            // Load user preferences
            await this.loadPreferences();
            
            // Register scanners
            await this.discoverScanners();
            
            // Load instrument sets
            await this.loadInstrumentSets();
            
            // Set up listeners for instrument events
            document.addEventListener('instrumentScanned', this.handleInstrumentScan.bind(this));
            document.addEventListener('caseStarted', this.handleCaseStart.bind(this));
            document.addEventListener('caseEnded', this.handleCaseEnd.bind(this));
            document.addEventListener('missingInstrumentReport', this.handleMissingInstrument.bind(this));
            
            // Set up offline/online listeners
            window.addEventListener('online', () => {
                this.syncStatus = 'online';
                this.syncOfflineData();
            });
            
            window.addEventListener('offline', () => {
                this.syncStatus = 'offline';
            });
            
            console.log('Instrument Tracking module initialized');
            
            // Dispatch ready event
            document.dispatchEvent(new CustomEvent('instrumentTrackingReady'));
        } catch (error) {
            console.error('Failed to initialize Instrument Tracking module:', error);
            document.dispatchEvent(new CustomEvent('instrumentTrackingError', {
                detail: { error: error.message }
            }));
        }
    }
    
    async setupDatabase() {
        try {
            this.dbInstance = await openDatabase('instrumentTrackingDB', 1, (db) => {
                if (!db.objectStoreNames.contains('instruments')) {
                    const instrumentStore = db.createObjectStore('instruments', { keyPath: 'id' });
                    instrumentStore.createIndex('by_type', 'type', { unique: false });
                    instrumentStore.createIndex('by_status', 'status', { unique: false });
                }

                if (!db.objectStoreNames.contains('cases')) {
                    const caseStore = db.createObjectStore('cases', { keyPath: 'id' });
                    caseStore.createIndex('by_date', 'date', { unique: false });
                    caseStore.createIndex('by_patient', 'patientId', { unique: false });
                    caseStore.createIndex('by_status', 'status', { unique: false });
                }

                if (!db.objectStoreNames.contains('instrumentSets')) {
                    const setStore = db.createObjectStore('instrumentSets', { keyPath: 'id' });
                    setStore.createIndex('by_type', 'type', { unique: false });
                }

                if (!db.objectStoreNames.contains('audit')) {
                    const auditStore = db.createObjectStore('audit', { keyPath: 'id', autoIncrement: true });
                    auditStore.createIndex('by_user', 'userId', { unique: false });
                    auditStore.createIndex('by_action', 'action', { unique: false });
                    auditStore.createIndex('by_timestamp', 'timestamp', { unique: false });
                }
            });
            console.log('Database setup complete');
        } catch (error) {
            console.error('Error setting up database:', error);
        }
    }
    
    async loadPreferences() {
        try {
            // Try to load from server first
            if (this.syncStatus === 'online') {
                const response = await fetch('/api/v1/instrument-tracking/preferences', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                    },
                    credentials: 'same-origin'
                });
                
                if (response.ok) {
                    this.preferences = await response.json();
                    return;
                }
            }
            
            // Fallback to local storage
            const storedPrefs = localStorage.getItem('instrumentTrackingPreferences');
            if (storedPrefs) {
                this.preferences = JSON.parse(storedPrefs);
            } else {
                // Default preferences
                this.preferences = {
                    alertMissingInstruments: true,
                    trackSterilizationStatus: true,
                    autoGenerateReports: true,
                    scanThreshold: 3, // Seconds between duplicate scans
                    instrumentSetWarnings: true,
                    autoCheckIncompleteSets: true
                };
                
                // Save defaults
                localStorage.setItem('instrumentTrackingPreferences', JSON.stringify(this.preferences));
            }
        } catch (error) {
            console.error('Error loading preferences:', error);
            // Use defaults on error
            this.preferences = {
                alertMissingInstruments: true,
                trackSterilizationStatus: true,
                autoGenerateReports: true,
                scanThreshold: 3,
                instrumentSetWarnings: true,
                autoCheckIncompleteSets: true
            };
        }
    }
    
    async discoverScanners() {
        // In a real implementation, this would discover Bluetooth/USB scanners
        // For this implementation, we'll simulate with mock scanners
        
        this.scanners = [
            { id: 'scanner-1', type: 'bluetooth', name: 'OR Scanner 1', status: 'connected', location: 'OR 1' },
            { id: 'scanner-2', type: 'bluetooth', name: 'OR Scanner 2', status: 'connected', location: 'OR 2' },
            { id: 'scanner-3', type: 'usb', name: 'Sterilization Scanner', status: 'connected', location: 'Sterilization' }
        ];
        
        // Register scanner events (in a real app, these would be actual device connections)
        this.scanners.forEach(scanner => {
            console.log(`Scanner registered: ${scanner.name} at ${scanner.location}`);
        });
        
        // Notify UI of available scanners
        document.dispatchEvent(new CustomEvent('scannersUpdated', {
            detail: { scanners: this.scanners }
        }));
    }
    
    async loadInstrumentSets() {
        try {
            // Try to load from server first
            if (this.syncStatus === 'online') {
                const response = await fetch('/api/v1/instrument-tracking/sets', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                    },
                    credentials: 'same-origin'
                });
                
                if (response.ok) {
                    const sets = await response.json();
                    sets.forEach(set => {
                        this.instrumentSets.set(set.id, set);
                    });
                    await this.storeInstrumentSetsLocally(sets);
                    return;
                }
            }
            
            // Fallback to local database
            await this.loadInstrumentSetsFromLocal();
            
        } catch (error) {
            console.error('Error loading instrument sets:', error);
            // Load fallback data
            await this.loadFallbackInstrumentSets();
        }
    }
    
    async loadInstrumentSetsFromLocal() {
        return new Promise((resolve, reject) => {
            if (!this.dbInstance) {
                reject(new Error('Database not initialized'));
                return;
            }
            
            const transaction = this.dbInstance.transaction(['instrumentSets'], 'readonly');
            const store = transaction.objectStore('instrumentSets');
            const request = store.getAll();
            
            request.onsuccess = (event) => {
                const sets = event.target.result;
                sets.forEach(set => {
                    this.instrumentSets.set(set.id, set);
                });
                resolve();
            };
            
            request.onerror = (event) => {
                reject(event.target.error);
            };
        });
    }
    
    async storeInstrumentSetsLocally(sets) {
        return new Promise((resolve, reject) => {
            if (!this.dbInstance) {
                reject(new Error('Database not initialized'));
                return;
            }
            
            const transaction = this.dbInstance.transaction(['instrumentSets'], 'readwrite');
            const store = transaction.objectStore('instrumentSets');
            
            let completed = 0;
            let errors = 0;
            
            sets.forEach(set => {
                const request = store.put(set);
                
                request.onsuccess = () => {
                    completed++;
                    if (completed + errors === sets.length) {
                        resolve();
                    }
                };
                
                request.onerror = (event) => {
                    errors++;
                    console.error('Error storing instrument set:', event.target.error);
                    if (completed + errors === sets.length) {
                        resolve();
                    }
                };
            });
            
            if (sets.length === 0) {
                resolve();
            }
        });
    }
    
    async loadFallbackInstrumentSets() {
        // Mock instrument sets for offline mode
        const fallbackSets = [
            {
                id: 'set-gastric-1',
                name: 'Gastrectomy Set A',
                type: 'Gastrectomy',
                instruments: [
                    { id: 'instr-001', name: 'DeBakey Forceps', count: 2 },
                    { id: 'instr-002', name: 'Mayo Scissors', count: 1 },
                    { id: 'instr-003', name: 'Metzenbaum Scissors', count: 2 },
                    { id: 'instr-004', name: 'Adson Tissue Forceps', count: 2 },
                    { id: 'instr-005', name: 'Richardson Retractor', count: 2 },
                    { id: 'instr-006', name: 'Allis Clamp', count: 4 },
                    { id: 'instr-007', name: 'Kocher Clamp', count: 4 },
                    { id: 'instr-008', name: 'Babcock Clamp', count: 4 },
                    { id: 'instr-009', name: 'Kelly Clamp', count: 6 },
                    { id: 'instr-010', name: 'Needle Holder', count: 2 }
                ],
                lastUpdated: new Date().toISOString()
            },
            {
                id: 'set-gastric-2',
                name: 'Laparoscopic Gastrectomy Set',
                type: 'Laparoscopic',
                instruments: [
                    { id: 'instr-101', name: 'Trocar 5mm', count: 2 },
                    { id: 'instr-102', name: 'Trocar 10mm', count: 2 },
                    { id: 'instr-103', name: 'Laparoscopic Scissors', count: 1 },
                    { id: 'instr-104', name: 'Laparoscopic Grasper', count: 2 },
                    { id: 'instr-105', name: 'Laparoscopic Needle Driver', count: 2 },
                    { id: 'instr-106', name: 'Laparoscopic Clip Applier', count: 1 },
                    { id: 'instr-107', name: 'Harmonic Scalpel', count: 1 },
                    { id: 'instr-108', name: 'Laparoscopic Suction/Irrigator', count: 1 },
                    { id: 'instr-109', name: 'Specimen Retrieval Bag', count: 2 }
                ],
                lastUpdated: new Date().toISOString()
            }
        ];
        
        // Store in memory
        fallbackSets.forEach(set => {
            this.instrumentSets.set(set.id, set);
        });
        
        // Store in local DB
        await this.storeInstrumentSetsLocally(fallbackSets);
    }
    
    handleInstrumentScan(event) {
        const scanData = event.detail;
        
        if (!scanData || !scanData.instrumentId || !scanData.scannerId) {
            console.error('Invalid instrument scan data:', scanData);
            return;
        }
        
        // Check for duplicate scans within threshold
        const lastScan = this.getLastScanForInstrument(scanData.instrumentId);
        const now = new Date();
        
        if (lastScan && 
            (now - new Date(lastScan.timestamp) < this.preferences.scanThreshold * 1000)) {
            // Ignore duplicate scan
            return;
        }
        
        // Create scan record
        const scanRecord = {
            instrumentId: scanData.instrumentId,
            scannerId: scanData.scannerId,
            timestamp: now.toISOString(),
            location: this.getScannerLocation(scanData.scannerId),
            caseId: this.activeCase ? this.activeCase.id : null,
            action: scanData.action || 'check-in',
            user: window.currentUser ? window.currentUser.id : 'unknown',
            syncStatus: 'pending'
        };
        
        // Save scan record
        this.saveInstrumentScan(scanRecord);
        
        // Update instrument status
        this.updateInstrumentStatus(scanData.instrumentId, scanData.action, scanData.location);
        
        // If tracking a case, update case record
        if (this.activeCase) {
            this.updateCaseInstruments(scanData.instrumentId, scanData.action);
        }
        
        // Update sterilization status if applicable
        if (scanData.action === 'sterilization-start' || 
            scanData.action === 'sterilization-complete') {
            this.updateSterilizationStatus(scanData.instrumentId, scanData.action);
        }
        
        // Log for HIPAA audit
        this.logAudit('instrument_scan', {
            instrumentId: scanData.instrumentId,
            scannerId: scanData.scannerId,
            action: scanData.action,
            caseId: this.activeCase ? this.activeCase.id : null
        });
        
        // Update UI
        this.notifyUiOfScan(scanRecord);
    }
    
    getLastScanForInstrument(instrumentId) {
        // In a real implementation, this would query the database
        // For simplicity, we'll check the in-memory tracking history
        const scans = this.trackingHistory.filter(scan => scan.instrumentId === instrumentId);
        if (scans.length > 0) {
            return scans[scans.length - 1];
        }
        return null;
    }
    
    getScannerLocation(scannerId) {
        const scanner = this.scanners.find(s => s.id === scannerId);
        return scanner ? scanner.location : 'Unknown';
    }
    
    async saveInstrumentScan(scanRecord) {
        // Add to tracking history
        this.trackingHistory.push(scanRecord);
        
        // Trim history if it gets too long
        if (this.trackingHistory.length > 1000) {
            this.trackingHistory = this.trackingHistory.slice(-1000);
        }
        
        // Save to IndexedDB
        try {
            await this.storeScanInDatabase(scanRecord);
        } catch (error) {
            console.error('Error storing scan in database:', error);
        }
        
        // If online, sync with server
        if (this.syncStatus === 'online') {
            this.syncScanWithServer(scanRecord);
        }
    }
    
    async storeScanInDatabase(scanRecord) {
        return new Promise((resolve, reject) => {
            if (!this.dbInstance) {
                reject(new Error('Database not initialized'));
                return;
            }
            
            const transaction = this.dbInstance.transaction(['scans'], 'readwrite');
            const store = transaction.objectStore('scans');
            
            const request = store.add(scanRecord);
            
            request.onsuccess = () => resolve();
            request.onerror = (event) => reject(event.target.error);
        });
    }
    
    async syncScanWithServer(scanRecord) {
        try {
            const response = await fetch('/api/v1/instrument-tracking/scan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                },
                body: JSON.stringify(scanRecord),
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                // Update sync status in local DB
                this.updateScanSyncStatus(scanRecord.id, 'synced');
            } else {
                console.error('Failed to sync scan with server:', await response.text());
            }
        } catch (error) {
            console.error('Error syncing scan with server:', error);
        }
    }
    
    updateInstrumentStatus(instrumentId, action, location) {
        let status = 'in-use';
        
        switch (action) {
            case 'check-in':
                status = this.activeCase ? 'in-use' : 'available';
                break;
            case 'check-out':
                status = 'checked-out';
                break;
            case 'sterilization-start':
                status = 'sterilizing';
                break;
            case 'sterilization-complete':
                status = 'sterilized';
                break;
            case 'maintenance':
                status = 'maintenance';
                break;
            case 'damaged':
                status = 'damaged';
                break;
        }
        
        // Update local instrument status
        const instrument = this.instruments.get(instrumentId);
        
        if (instrument) {
            instrument.status = status;
            instrument.lastLocation = location;
            instrument.lastUpdated = new Date().toISOString();
            
            // Update in database
            this.updateInstrumentInDatabase(instrument);
        } else {
            // Instrument not in local cache, try to load from DB
            this.loadInstrumentFromDatabase(instrumentId).then(loadedInstrument => {
                if (loadedInstrument) {
                    loadedInstrument.status = status;
                    loadedInstrument.lastLocation = location;
                    loadedInstrument.lastUpdated = new Date().toISOString();
                    
                    // Update cache and DB
                    this.instruments.set(instrumentId, loadedInstrument);
                    this.updateInstrumentInDatabase(loadedInstrument);
                } else {
                    // Create new instrument record with limited info
                    const newInstrument = {
                        id: instrumentId,
                        status: status,
                        lastLocation: location,
                        lastUpdated: new Date().toISOString(),
                        // These would normally come from a database lookup
                        name: `Instrument ${instrumentId}`,
                        type: 'Unknown',
                        setId: null
                    };
                    
                    this.instruments.set(instrumentId, newInstrument);
                    this.updateInstrumentInDatabase(newInstrument);
                }
            });
        }
    }
    
    async loadInstrumentFromDatabase(instrumentId) {
        return new Promise((resolve, reject) => {
            if (!this.dbInstance) {
                reject(new Error('Database not initialized'));
                return;
            }
            
            const transaction = this.dbInstance.transaction(['instruments'], 'readonly');
            const store = transaction.objectStore('instruments');
            
            const request = store.get(instrumentId);
            
            request.onsuccess = (event) => resolve(event.target.result);
            request.onerror = (event) => reject(event.target.error);
        });
    }
    
    async updateInstrumentInDatabase(instrument) {
        return new Promise((resolve, reject) => {
            if (!this.dbInstance) {
                reject(new Error('Database not initialized'));
                return;
            }
            
            const transaction = this.dbInstance.transaction(['instruments'], 'readwrite');
            const store = transaction.objectStore('instruments');
            
            const request = store.put(instrument);
            
            request.onsuccess = () => resolve();
            request.onerror = (event) => reject(event.target.error);
        });
    }
    
    updateCaseInstruments(instrumentId, action) {
        if (!this.activeCase) return;
        
        // Add instrument to case instruments list if not already there
        if (!this.activeCase.instruments.includes(instrumentId)) {
            this.activeCase.instruments.push(instrumentId);
            
            // Update case in database
            this.updateCaseInDatabase(this.activeCase);
            
            // Check for instrument set completion
            this.checkInstrumentSetCompletion();
        }
    }
    
    async updateCaseInDatabase(caseRecord) {
        return new Promise((resolve, reject) => {
            if (!this.dbInstance) {
                reject(new Error('Database not initialized'));
                return;
            }
            
            const transaction = this.dbInstance.transaction(['cases'], 'readwrite');
            const store = transaction.objectStore('cases');
            
            const request = store.put(caseRecord);
            
            request.onsuccess = () => resolve();
            request.onerror = (event) => reject(event.target.error);
        });
    }
    
    updateSterilizationStatus(instrumentId, action) {
        const status = action === 'sterilization-complete' ? 'sterilized' : 'in-process';
        const timestamp = new Date().toISOString();
        
        this.sterilizationStatus.set(instrumentId, {
            status: status,
            timestamp: timestamp,
            processId: action === 'sterilization-start' ? `steri-${Date.now()}` : null
        });
        
        // Update instrument record
        const instrument = this.instruments.get(instrumentId);
        if (instrument) {
            instrument.sterilizationStatus = status;
            instrument.lastSterilized = status === 'sterilized' ? timestamp : instrument.lastSterilized;
            this.updateInstrumentInDatabase(instrument);
        }
    }
    
    async handleCaseStart(event) {
        const caseData = event.detail;
        
        if (!caseData || !caseData.patientId || !caseData.procedureType) {
            console.error('Invalid case data:', caseData);
            return;
        }
        
        // Create new case record
        const caseRecord = {
            id: `case-${Date.now()}`,
            patientId: caseData.patientId,
            procedureType: caseData.procedureType,
            startTime: new Date().toISOString(),
            endTime: null,
            status: 'in-progress',
            location: caseData.location || 'Unknown',
            surgeon: caseData.surgeon || 'Unknown',
            instruments: [],
            instrumentSets: caseData.instrumentSets || [],
            notes: caseData.notes || '',
            syncStatus: 'pending'
        };
        
        // Set as active case
        this.activeCase = caseRecord;
        
        // Save to database
        await this.storeCaseInDatabase(caseRecord);
        
        // If online, sync with server
        if (this.syncStatus === 'online') {
            this.syncCaseWithServer(caseRecord);
        }
        
        // Log for HIPAA audit
        this.logAudit('case_started', {
            caseId: caseRecord.id,
            patientId: caseRecord.patientId,
            procedureType: caseRecord.procedureType
        });
        
        // Update UI
        document.dispatchEvent(new CustomEvent('caseUpdated', {
            detail: { case: caseRecord, action: 'started' }
        }));
        
        console.log(`Case started: ${caseRecord.id} for patient ${caseRecord.patientId}`);
    }
    
    async storeCaseInDatabase(caseRecord) {
        return new Promise((resolve, reject) => {
            if (!this.dbInstance) {
                reject(new Error('Database not initialized'));
                return;
            }
            
            const transaction = this.dbInstance.transaction(['cases'], 'readwrite');
            const store = transaction.objectStore('cases');
            
            const request = store.add(caseRecord);
            
            request.onsuccess = () => resolve();
            request.onerror = (event) => reject(event.target.error);
        });
    }
    
    async syncCaseWithServer(caseRecord) {
        try {
            const response = await fetch('/api/v1/instrument-tracking/case', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                },
                body: JSON.stringify(caseRecord),
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                // Update sync status in local DB
                this.updateCaseSyncStatus(caseRecord.id, 'synced');
            } else {
                console.error('Failed to sync case with server:', await response.text());
            }
        } catch (error) {
            console.error('Error syncing case with server:', error);
        }
    }
    
    async handleCaseEnd(event) {
        if (!this.activeCase) {
            console.error('No active case to end');
            return;
        }
        
        // Update case record
        this.activeCase.endTime = new Date().toISOString();
        this.activeCase.status = 'completed';
        
        // Add any additional data from event
        if (event.detail) {
            if (event.detail.notes) {
                this.activeCase.notes += '\n' + event.detail.notes;
            }
            if (event.detail.outcome) {
                this.activeCase.outcome = event.detail.outcome;
            }
        }
        
        // Save to database
        await this.updateCaseInDatabase(this.activeCase);
        
        // If online, sync with server
        if (this.syncStatus === 'online') {
            this.syncCaseWithServer(this.activeCase);
        }
        
        // Log for HIPAA audit
        this.logAudit('case_ended', {
            caseId: this.activeCase.id,
            patientId: this.activeCase.patientId,
            duration: new Date(this.activeCase.endTime) - new Date(this.activeCase.startTime),
            instrumentCount: this.activeCase.instruments.length
        });
        
        // Generate case report if enabled
        if (this.preferences.autoGenerateReports) {
            this.generateCaseReport(this.activeCase);
        }
        
        // Check for missing instruments
        await this.checkForMissingInstruments();
        
        // Update UI
        document.dispatchEvent(new CustomEvent('caseUpdated', {
            detail: { case: this.activeCase, action: 'ended' }
        }));
        
        console.log(`Case ended: ${this.activeCase.id}`);
        
        // Clear active case
        const completedCase = this.activeCase;
        this.activeCase = null;
        
        return completedCase;
    }
    
    async checkForMissingInstruments() {
        if (!this.activeCase) return [];
        
        const missingInstruments = [];
        
        // Get expected instruments from sets used in the case
        const expectedInstruments = new Set();
        
        for (const setId of this.activeCase.instrumentSets) {
            const instrumentSet = this.instrumentSets.get(setId);
            if (instrumentSet) {
                instrumentSet.instruments.forEach(instrument => {
                    for (let i = 0; i < instrument.count; i++) {
                        expectedInstruments.add(`${instrument.id}-${i}`);
                    }
                });
            }
        }
        
        // Check which instruments were scanned
        for (const expectedId of expectedInstruments) {
            if (!this.activeCase.instruments.includes(expectedId)) {
                missingInstruments.push(expectedId);
            }
        }
        
        // Update missing instruments list
        this.missingInstruments = missingInstruments;
        
        // If there are missing instruments and alerts are enabled, notify
        if (missingInstruments.length > 0 && this.preferences.alertMissingInstruments) {
            document.dispatchEvent(new CustomEvent('missingInstruments', {
                detail: {
                    caseId: this.activeCase.id,
                    instruments: missingInstruments,
                    count: missingInstruments.length
                }
            }));
        }
        
        return missingInstruments;
    }
    
    generateCaseReport(caseRecord) {
        // Create report object
        const report = {
            id: `report-${caseRecord.id}`,
            caseId: caseRecord.id,
            patientId: caseRecord.patientId,
            procedureType: caseRecord.procedureType,
            date: new Date(caseRecord.startTime).toLocaleDateString(),
            duration: this.calculateDuration(caseRecord.startTime, caseRecord.endTime),
            instrumentCount: caseRecord.instruments.length,
            instrumentSets: caseRecord.instrumentSets.map(setId => {
                const set = this.instrumentSets.get(setId);
                return set ? set.name : setId;
            }),
            missingInstruments: this.missingInstruments.length,
            status: this.missingInstruments.length > 0 ? 'incomplete' : 'complete',
            generatedAt: new Date().toISOString(),
            generatedBy: window.currentUser ? window.currentUser.id : 'system'
        };
        
        // Dispatch event with report
        document.dispatchEvent(new CustomEvent('caseReportGenerated', {
            detail: { report: report }
        }));
        
        // If online, send to server
        if (this.syncStatus === 'online') {
            fetch('/api/v1/instrument-tracking/report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                },
                body: JSON.stringify(report),
                credentials: 'same-origin'
            }).catch(error => {
                console.error('Error sending report to server:', error);
            });
        }
        
        return report;
    }
    
    calculateDuration(startTime, endTime) {
        const start = new Date(startTime);
        const end = new Date(endTime);
        const durationMs = end - start;
        
        const hours = Math.floor(durationMs / (1000 * 60 * 60));
        const minutes = Math.floor((durationMs % (1000 * 60 * 60)) / (1000 * 60));
        
        return `${hours}h ${minutes}m`;
    }
    
    handleMissingInstrument(event) {
        const data = event.detail;
        
        if (!data || !data.instrumentId) {
            console.error('Invalid missing instrument report:', data);
            return;
        }
        
        // Add to missing instruments list if not already there
        if (!this.missingInstruments.includes(data.instrumentId)) {
            this.missingInstruments.push(data.instrumentId);
        }
        
        // Log the report
        this.logAudit('missing_instrument_reported', {
            instrumentId: data.instrumentId,
            caseId: data.caseId || (this.activeCase ? this.activeCase.id : null),
            reportedBy: window.currentUser ? window.currentUser.id : 'unknown',
            location: data.location || 'Unknown'
        });
        
        // Send report to server if online
        if (this.syncStatus === 'online') {
            fetch('/api/v1/instrument-tracking/missing', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                },
                body: JSON.stringify({
                    instrumentId: data.instrumentId,
                    caseId: data.caseId || (this.activeCase ? this.activeCase.id : null),
                    location: data.location || 'Unknown',
                    notes: data.notes || '',
                    timestamp: new Date().toISOString()
                }),
                credentials: 'same-origin'
            }).catch(error => {
                console.error('Error reporting missing instrument to server:', error);
            });
        }
        
        // Update UI
        document.dispatchEvent(new CustomEvent('missingInstrumentReported', {
            detail: {
                instrumentId: data.instrumentId,
                count: this.missingInstruments.length
            }
        }));
    }
    
    checkInstrumentSetCompletion() {
        if (!this.activeCase || !this.preferences.instrumentSetWarnings) return;
        
        // For each instrument set in the case
        for (const setId of this.activeCase.instrumentSets) {
            const set = this.instrumentSets.get(setId);
            if (!set) continue;
            
            let totalExpected = 0;
            let totalScanned = 0;
            
            // Count expected instruments
            set.instruments.forEach(instrument => {
                totalExpected += instrument.count;
                
                // Count how many of this instrument type were scanned
                const scanned = this.activeCase.instruments.filter(id => 
                    id.startsWith(instrument.id)).length;
                
                totalScanned += Math.min(scanned, instrument.count);
            });
            
            // Calculate completion percentage
            const completionPercentage = (totalScanned / totalExpected) * 100;
            
            // Update UI with completion status
            document.dispatchEvent(new CustomEvent('instrumentSetCompletion', {
                detail: {
                    setId: setId,
                    setName: set.name,
                    expected: totalExpected,
                    scanned: totalScanned,
                    percentage: completionPercentage,
                    complete: totalScanned === totalExpected
                }
            }));
        }
    }
    
    notifyUiOfScan(scanRecord) {
        // Get instrument details
        const instrument = this.instruments.get(scanRecord.instrumentId) || {
            id: scanRecord.instrumentId,
            name: `Instrument ${scanRecord.instrumentId}`,
            type: 'Unknown'
        };
        
        // Create event detail with combined information
        const detail = {
            scan: scanRecord,
            instrument: instrument,
            case: this.activeCase
        };
        
        // Dispatch event for UI to update
        document.dispatchEvent(new CustomEvent('instrumentScanned', {
            detail: detail
        }));
    }
    
    async syncOfflineData() {
        if (!this.dbInstance) return;
        
        try {
            // Sync pending scans
            const pendingScans = await this.getPendingScans();
            for (const scan of pendingScans) {
                await this.syncScanWithServer(scan);
            }
            
            // Sync pending cases
            const pendingCases = await this.getPendingCases();
            for (const caseRecord of pendingCases) {
                await this.syncCaseWithServer(caseRecord);
            }
            
            // Sync pending audit logs
            const pendingAuditLogs = await this.getPendingAuditLogs();
            for (const log of pendingAuditLogs) {
                await this.syncAuditLogWithServer(log);
            }
            
            console.log(`Synced ${pendingScans.length} scans, ${pendingCases.length} cases, and ${pendingAuditLogs.length} audit logs`);
        } catch (error) {
            console.error('Error syncing offline data:', error);
        }
    }
    
    async getPendingScans() {
        return new Promise((resolve, reject) => {
            if (!this.dbInstance) {
                reject(new Error('Database not initialized'));
                return;
            }
            
            const transaction = this.dbInstance.transaction(['scans'], 'readonly');
            const store = transaction.objectStore('scans');
            const index = store.index('by_sync_status');
            const request = index.getAll(IDBKeyRange.only('pending'));
            
            request.onsuccess = () => resolve(request.result);
            request.onerror = (event) => reject(event.target.error);
        });
    }
    
    async getPendingCases() {
        return new Promise((resolve, reject) => {
            if (!this.dbInstance) {
                reject(new Error('Database not initialized'));
                return;
            }
            
            const transaction = this.dbInstance.transaction(['cases'], 'readonly');
            const store = transaction.objectStore('cases');
            const index = store.index('by_sync_status');
            const request = index.getAll(IDBKeyRange.only('pending'));
            
            request.onsuccess = () => resolve(request.result);
            request.onerror = (event) => reject(event.target.error);
        });
    }
    
    async getPendingAuditLogs() {
        return new Promise((resolve, reject) => {
            if (!this.dbInstance) {
                reject(new Error('Database not initialized'));
                return;
            }
            
            const transaction = this.dbInstance.transaction(['audit'], 'readonly');
            const store = transaction.objectStore('audit');
            const index = store.index('by_sync_status');
            const request = index.getAll(IDBKeyRange.only('pending'));
            
            request.onsuccess = () => resolve(request.result);
            request.onerror = (event) => reject(event.target.error);
        });
    }
    
    async updateScanSyncStatus(scanId, status) {
        return new Promise((resolve, reject) => {
            if (!this.dbInstance) {
                reject(new Error('Database not initialized'));
                return;
            }
            
            const transaction = this.dbInstance.transaction(['scans'], 'readwrite');
            const store = transaction.objectStore('scans');
            
            const getRequest = store.get(scanId);
            
            getRequest.onsuccess = () => {
                const scan = getRequest.result;
                if (scan) {
                    scan.syncStatus = status;
                    const updateRequest = store.put(scan);
                    
                    updateRequest.onsuccess = () => resolve();
                    updateRequest.onerror = (event) => reject(event.target.error);
                } else {
                    reject(new Error('Scan not found'));
                }
            };
            
            getRequest.onerror = (event) => reject(event.target.error);
        });
    }
    
    async updateCaseSyncStatus(caseId, status) {
        return new Promise((resolve, reject) => {
            if (!this.dbInstance) {
                reject(new Error('Database not initialized'));
                return;
            }
            
            const transaction = this.dbInstance.transaction(['cases'], 'readwrite');
            const store = transaction.objectStore('cases');
            
            const getRequest = store.get(caseId);
            
            getRequest.onsuccess = () => {
                const caseRecord = getRequest.result;
                if (caseRecord) {
                    caseRecord.syncStatus = status;
                    const updateRequest = store.put(caseRecord);
                    
                    updateRequest.onsuccess = () => resolve();
                    updateRequest.onerror = (event) => reject(event.target.error);
                } else {
                    reject(new Error('Case not found'));
                }
            };
            
            getRequest.onerror = (event) => reject(event.target.error);
        });
    }
    
    logAudit(action, details) {
        const auditEntry = {
            action: action,
            details: details,
            timestamp: new Date().toISOString(),
            user: window.currentUser ? window.currentUser.id : 'unknown',
            ipAddress: window.clientIp || 'unknown',
            userAgent: navigator.userAgent,
            syncStatus: 'pending'
        };
        
        // Store in IndexedDB
        if (this.dbInstance) {
            const transaction = this.dbInstance.transaction(['audit'], 'readwrite');
            const store = transaction.objectStore('audit');
            store.add(auditEntry);
        }
        
        // If online, also send to server
        if (this.syncStatus === 'online') {
            this.syncAuditLogWithServer(auditEntry);
        }
    }
    
    async syncAuditLogWithServer(auditEntry) {
        try {
            const response = await fetch('/api/v1/audit/instrument-tracking', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                },
                body: JSON.stringify(auditEntry),
                credentials: 'same-origin'
            });
            
            if (response.ok && auditEntry.id) {
                // Update sync status in local DB
                this.updateAuditLogSyncStatus(auditEntry.id, 'synced');
            }
        } catch (error) {
            console.error('Error syncing audit log with server:', error);
        }
    }
    
    async updateAuditLogSyncStatus(logId, status) {
        return new Promise((resolve, reject) => {
            if (!this.dbInstance) {
                reject(new Error('Database not initialized'));
                return;
            }
            
            const transaction = this.dbInstance.transaction(['audit'], 'readwrite');
            const store = transaction.objectStore('audit');
            
            const getRequest = store.get(logId);
            
            getRequest.onsuccess = () => {
                const log = getRequest.result;
                if (log) {
                    log.syncStatus = status;
                    const updateRequest = store.put(log);
                    
                    updateRequest.onsuccess = () => resolve();
                    updateRequest.onerror = (event) => reject(event.target.error);
                } else {
                    reject(new Error('Audit log not found'));
                }
            };
            
            getRequest.onerror = (event) => reject(event.target.error);
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.instrumentTracking = new InstrumentTracking();
});

// Export for module use
export default InstrumentTracking;
