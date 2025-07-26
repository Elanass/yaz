// Utility functions for IndexedDB operations

/**
 * Open an IndexedDB database
 * @param {string} dbName - Name of the database
 * @param {number} version - Version of the database
 * @param {function} upgradeCallback - Callback for database upgrade
 * @returns {Promise<IDBDatabase>} - Promise resolving to the database instance
 */
export function openDatabase(dbName, version, upgradeCallback) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(dbName, version);

        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (upgradeCallback) {
                upgradeCallback(db);
            }
        };

        request.onsuccess = (event) => {
            resolve(event.target.result);
        };

        request.onerror = (event) => {
            reject(event.target.error);
        };
    });
}

/**
 * Perform a database transaction
 * @param {IDBDatabase} db - Database instance
 * @param {string} storeName - Name of the object store
 * @param {string} mode - Transaction mode ('readonly' or 'readwrite')
 * @param {function} transactionCallback - Callback for transaction logic
 * @returns {Promise<any>} - Promise resolving to the transaction result
 */
export function performTransaction(db, storeName, mode, transactionCallback) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction([storeName], mode);
        const store = transaction.objectStore(storeName);

        try {
            const result = transactionCallback(store);
            transaction.oncomplete = () => resolve(result);
            transaction.onerror = (event) => reject(event.target.error);
        } catch (error) {
            reject(error);
        }
    });
}

/**
 * Get all records from an object store
 * @param {IDBObjectStore} store - Object store instance
 * @returns {Promise<any[]>} - Promise resolving to an array of records
 */
export function getAllRecords(store) {
    return new Promise((resolve, reject) => {
        const request = store.getAll();

        request.onsuccess = () => resolve(request.result);
        request.onerror = (event) => reject(event.target.error);
    });
}

/**
 * Get a record by key from an object store
 * @param {IDBObjectStore} store - Object store instance
 * @param {any} key - Key of the record to retrieve
 * @returns {Promise<any>} - Promise resolving to the record
 */
export function getRecordByKey(store, key) {
    return new Promise((resolve, reject) => {
        const request = store.get(key);

        request.onsuccess = () => resolve(request.result);
        request.onerror = (event) => reject(event.target.error);
    });
}

/**
 * Add or update a record in an object store
 * @param {IDBObjectStore} store - Object store instance
 * @param {any} record - Record to add or update
 * @returns {Promise<void>} - Promise resolving when the operation is complete
 */
export function putRecord(store, record) {
    return new Promise((resolve, reject) => {
        const request = store.put(record);

        request.onsuccess = () => resolve();
        request.onerror = (event) => reject(event.target.error);
    });
}

/**
 * Delete a record by key from an object store
 * @param {IDBObjectStore} store - Object store instance
 * @param {any} key - Key of the record to delete
 * @returns {Promise<void>} - Promise resolving when the operation is complete
 */
export function deleteRecord(store, key) {
    return new Promise((resolve, reject) => {
        const request = store.delete(key);

        request.onsuccess = () => resolve();
        request.onerror = (event) => reject(event.target.error);
    });
}
