"""
PWA Service - Progressive Web App superpowers for offline-first clinical workflows.
Implements Background Sync, Push Notifications, and Service Worker management.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

import aiofiles
from cryptography.fernet import Fernet
from fastapi import HTTPException
from pywebpush import WebPusher, webpush
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..db.models import User, PWASubscription, BackgroundSyncJob
from ..schemas.pwa import (
    PushSubscription,
    BackgroundSyncJobCreate,
    BackgroundSyncJobResponse,
    NotificationPayload,
    PWAManifest,
)

logger = logging.getLogger(__name__)


class PWAService:
    """PWA Service for offline-first clinical workflows."""

    def __init__(self):
        self.encryption_key = settings.encryption_key.encode()
        self.cipher = Fernet(self.encryption_key)
        self.vapid_private_key = settings.vapid_private_key
        self.vapid_public_key = settings.vapid_public_key
        self.vapid_email = settings.vapid_email

    async def register_push_subscription(
        self, db: AsyncSession, user_id: UUID, subscription_data: PushSubscription
    ) -> PWASubscription:
        """Register a new push subscription for a user."""
        try:
            # Encrypt the subscription data
            encrypted_endpoint = self.cipher.encrypt(subscription_data.endpoint.encode())
            encrypted_keys = self.cipher.encrypt(
                json.dumps(subscription_data.keys.dict()).encode()
            )

            # Check if subscription already exists
            existing = await db.execute(
                select(PWASubscription).where(
                    PWASubscription.user_id == user_id,
                    PWASubscription.endpoint_hash == self._hash_endpoint(
                        subscription_data.endpoint
                    ),
                )
            )
            existing_sub = existing.scalar_one_or_none()

            if existing_sub:
                # Update existing subscription
                existing_sub.encrypted_endpoint = encrypted_endpoint
                existing_sub.encrypted_keys = encrypted_keys
                existing_sub.updated_at = datetime.utcnow()
                await db.commit()
                await db.refresh(existing_sub)
                return existing_sub

            # Create new subscription
            subscription = PWASubscription(
                id=uuid4(),
                user_id=user_id,
                encrypted_endpoint=encrypted_endpoint,
                encrypted_keys=encrypted_keys,
                endpoint_hash=self._hash_endpoint(subscription_data.endpoint),
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            db.add(subscription)
            await db.commit()
            await db.refresh(subscription)

            logger.info(f"Push subscription registered for user {user_id}")
            return subscription

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to register push subscription: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to register push subscription"
            )

    async def send_push_notification(
        self,
        db: AsyncSession,
        user_id: UUID,
        notification: NotificationPayload,
        urgent: bool = False,
    ) -> List[bool]:
        """Send push notification to all user's subscriptions."""
        try:
            # Get user's active subscriptions
            result = await db.execute(
                select(PWASubscription).where(
                    PWASubscription.user_id == user_id,
                    PWASubscription.is_active == True,
                )
            )
            subscriptions = result.scalars().all()

            if not subscriptions:
                logger.warning(f"No active subscriptions found for user {user_id}")
                return []

            # Prepare notification payload
            payload = {
                "title": notification.title,
                "body": notification.body,
                "icon": notification.icon or "/icons/icon-192x192.png",
                "badge": notification.badge or "/icons/badge-72x72.png",
                "tag": notification.tag or f"adci-{uuid4()}",
                "data": notification.data or {},
                "requireInteraction": urgent or notification.require_interaction,
                "timestamp": datetime.utcnow().isoformat(),
                "vibrate": [200, 100, 200] if urgent else [100],
                "actions": notification.actions or [],
            }

            # Add clinical urgency indicators
            if urgent:
                payload["urgency"] = "high"
                payload["data"]["clinical_urgency"] = True
                payload["vibrate"] = [300, 100, 300, 100, 300]

            results = []
            for subscription in subscriptions:
                try:
                    # Decrypt subscription data
                    endpoint = self.cipher.decrypt(subscription.encrypted_endpoint).decode()
                    keys_data = json.loads(
                        self.cipher.decrypt(subscription.encrypted_keys).decode()
                    )

                    # Send notification
                    webpush(
                        subscription_info={
                            "endpoint": endpoint,
                            "keys": keys_data,
                        },
                        data=json.dumps(payload),
                        vapid_private_key=self.vapid_private_key,
                        vapid_claims={
                            "sub": f"mailto:{self.vapid_email}",
                            "exp": int(
                                (datetime.utcnow() + timedelta(hours=12)).timestamp()
                            ),
                        },
                        timeout=15,
                    )
                    results.append(True)
                    logger.info(f"Notification sent to subscription {subscription.id}")

                except Exception as e:
                    logger.error(
                        f"Failed to send notification to subscription {subscription.id}: {str(e)}"
                    )
                    # Deactivate subscription if it's invalid
                    if "InvalidSubscription" in str(e) or "Gone" in str(e):
                        subscription.is_active = False
                        await db.commit()
                    results.append(False)

            return results

        except Exception as e:
            logger.error(f"Failed to send push notifications: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to send push notifications"
            )

    async def create_background_sync_job(
        self, db: AsyncSession, user_id: UUID, job_data: BackgroundSyncJobCreate
    ) -> BackgroundSyncJob:
        """Create a background sync job for offline data synchronization."""
        try:
            # Encrypt sensitive data
            encrypted_data = None
            if job_data.data:
                encrypted_data = self.cipher.encrypt(json.dumps(job_data.data).encode())

            job = BackgroundSyncJob(
                id=uuid4(),
                user_id=user_id,
                job_type=job_data.job_type,
                encrypted_data=encrypted_data,
                priority=job_data.priority,
                max_retries=job_data.max_retries or 3,
                retry_count=0,
                status="pending",
                created_at=datetime.utcnow(),
                scheduled_at=job_data.scheduled_at or datetime.utcnow(),
            )

            db.add(job)
            await db.commit()
            await db.refresh(job)

            logger.info(f"Background sync job created: {job.id}")
            return job

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create background sync job: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to create background sync job"
            )

    async def process_background_sync_jobs(self, db: AsyncSession) -> List[UUID]:
        """Process pending background sync jobs."""
        try:
            # Get pending jobs ordered by priority and scheduled time
            result = await db.execute(
                select(BackgroundSyncJob)
                .where(
                    BackgroundSyncJob.status == "pending",
                    BackgroundSyncJob.scheduled_at <= datetime.utcnow(),
                )
                .order_by(
                    BackgroundSyncJob.priority.desc(),
                    BackgroundSyncJob.scheduled_at.asc(),
                )
                .limit(50)  # Process up to 50 jobs at a time
            )
            jobs = result.scalars().all()

            processed_jobs = []
            for job in jobs:
                try:
                    # Mark job as processing
                    job.status = "processing"
                    job.started_at = datetime.utcnow()
                    await db.commit()

                    # Process job based on type
                    success = await self._process_sync_job(db, job)

                    if success:
                        job.status = "completed"
                        job.completed_at = datetime.utcnow()
                        processed_jobs.append(job.id)
                        logger.info(f"Background sync job completed: {job.id}")
                    else:
                        await self._handle_job_failure(db, job)

                    await db.commit()

                except Exception as e:
                    logger.error(f"Error processing job {job.id}: {str(e)}")
                    await self._handle_job_failure(db, job)
                    await db.commit()

            return processed_jobs

        except Exception as e:
            logger.error(f"Failed to process background sync jobs: {str(e)}")
            return []

    async def _process_sync_job(self, db: AsyncSession, job: BackgroundSyncJob) -> bool:
        """Process a specific background sync job."""
        try:
            # Decrypt job data if present
            job_data = {}
            if job.encrypted_data:
                decrypted_data = self.cipher.decrypt(job.encrypted_data).decode()
                job_data = json.loads(decrypted_data)

            # Process based on job type
            if job.job_type == "patient_data_sync":
                return await self._sync_patient_data(db, job.user_id, job_data)
            elif job.job_type == "decision_cache_update":
                return await self._update_decision_cache(db, job.user_id, job_data)
            elif job.job_type == "audit_log_sync":
                return await self._sync_audit_logs(db, job.user_id, job_data)
            elif job.job_type == "clinical_protocol_update":
                return await self._update_clinical_protocols(db, job.user_id, job_data)
            else:
                logger.warning(f"Unknown job type: {job.job_type}")
                return False

        except Exception as e:
            logger.error(f"Error processing sync job: {str(e)}")
            return False

    async def _handle_job_failure(self, db: AsyncSession, job: BackgroundSyncJob):
        """Handle failed background sync job."""
        job.retry_count += 1
        job.last_error = datetime.utcnow()

        if job.retry_count >= job.max_retries:
            job.status = "failed"
            job.failed_at = datetime.utcnow()
            
            # Send notification about critical sync failure
            if job.priority >= 8:  # High priority jobs
                await self.send_push_notification(
                    db,
                    job.user_id,
                    NotificationPayload(
                        title="Critical Sync Failure",
                        body=f"Background sync job {job.job_type} failed after {job.max_retries} retries",
                        tag="sync-failure",
                        require_interaction=True,
                        data={"job_id": str(job.id), "job_type": job.job_type},
                    ),
                    urgent=True,
                )
        else:
            # Exponential backoff for retry
            delay_minutes = min(2 ** job.retry_count, 60)
            job.scheduled_at = datetime.utcnow() + timedelta(minutes=delay_minutes)
            job.status = "pending"

    async def _sync_patient_data(
        self, db: AsyncSession, user_id: UUID, job_data: Dict[str, Any]
    ) -> bool:
        """Sync patient data in background."""
        # Implementation would depend on specific patient data sync requirements
        logger.info(f"Syncing patient data for user {user_id}")
        await asyncio.sleep(1)  # Simulate processing
        return True

    async def _update_decision_cache(
        self, db: AsyncSession, user_id: UUID, job_data: Dict[str, Any]
    ) -> bool:
        """Update decision engine cache in background."""
        logger.info(f"Updating decision cache for user {user_id}")
        await asyncio.sleep(1)  # Simulate processing
        return True

    async def _sync_audit_logs(
        self, db: AsyncSession, user_id: UUID, job_data: Dict[str, Any]
    ) -> bool:
        """Sync audit logs in background."""
        logger.info(f"Syncing audit logs for user {user_id}")
        await asyncio.sleep(1)  # Simulate processing
        return True

    async def _update_clinical_protocols(
        self, db: AsyncSession, user_id: UUID, job_data: Dict[str, Any]
    ) -> bool:
        """Update clinical protocols in background."""
        logger.info(f"Updating clinical protocols for user {user_id}")
        await asyncio.sleep(1)  # Simulate processing
        return True

    def _hash_endpoint(self, endpoint: str) -> str:
        """Create a hash of the endpoint for duplicate detection."""
        import hashlib
        return hashlib.sha256(endpoint.encode()).hexdigest()

    async def get_pwa_manifest(self) -> PWAManifest:
        """Generate PWA manifest for installable app."""
        return PWAManifest(
            name="Gastric ADCI Platform",
            short_name="ADCI",
            description="Precision oncology decision support for gastric surgery",
            start_url="/",
            display="standalone",
            background_color="#ffffff",
            theme_color="#1976d2",
            orientation="portrait-primary",
            scope="/",
            lang="en",
            categories=["medical", "healthcare", "productivity"],
            icons=[
                {
                    "src": "/icons/icon-72x72.png",
                    "sizes": "72x72",
                    "type": "image/png",
                    "purpose": "any maskable",
                },
                {
                    "src": "/icons/icon-96x96.png",
                    "sizes": "96x96",
                    "type": "image/png",
                    "purpose": "any maskable",
                },
                {
                    "src": "/icons/icon-128x128.png",
                    "sizes": "128x128",
                    "type": "image/png",
                    "purpose": "any maskable",
                },
                {
                    "src": "/icons/icon-144x144.png",
                    "sizes": "144x144",
                    "type": "image/png",
                    "purpose": "any maskable",
                },
                {
                    "src": "/icons/icon-152x152.png",
                    "sizes": "152x152",
                    "type": "image/png",
                    "purpose": "any maskable",
                },
                {
                    "src": "/icons/icon-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png",
                    "purpose": "any maskable",
                },
                {
                    "src": "/icons/icon-384x384.png",
                    "sizes": "384x384",
                    "type": "image/png",
                    "purpose": "any maskable",
                },
                {
                    "src": "/icons/icon-512x512.png",
                    "sizes": "512x512",
                    "type": "image/png",
                    "purpose": "any maskable",
                },
            ],
            shortcuts=[
                {
                    "name": "New Case",
                    "short_name": "New Case",
                    "description": "Start a new patient case",
                    "url": "/cases/new",
                    "icons": [{"src": "/icons/shortcut-new-case.png", "sizes": "96x96"}],
                },
                {
                    "name": "Dashboard",
                    "short_name": "Dashboard",
                    "description": "View clinical dashboard",
                    "url": "/dashboard",
                    "icons": [{"src": "/icons/shortcut-dashboard.png", "sizes": "96x96"}],
                },
                {
                    "name": "Guidelines",
                    "short_name": "Guidelines",
                    "description": "Access clinical guidelines",
                    "url": "/guidelines",
                    "icons": [{"src": "/icons/shortcut-guidelines.png", "sizes": "96x96"}],
                },
            ],
            related_applications=[],
            prefer_related_applications=False,
        )

    async def generate_service_worker(self) -> str:
        """Generate service worker JavaScript for PWA functionality."""
        sw_content = """
// Gastric ADCI Platform Service Worker
// Handles offline caching, background sync, and push notifications

const CACHE_NAME = 'adci-v1.0.0';
const STATIC_CACHE = 'adci-static-v1.0.0';
const DYNAMIC_CACHE = 'adci-dynamic-v1.0.0';

// Files to cache for offline functionality
const STATIC_FILES = [
    '/',
    '/static/css/main.css',
    '/static/js/main.js',
    '/static/js/offline.js',
    '/icons/icon-192x192.png',
    '/icons/icon-512x512.png',
    '/offline.html',
    '/manifest.json'
];

// Critical API endpoints to cache
const API_CACHE_PATTERNS = [
    '/api/guidelines/',
    '/api/protocols/',
    '/api/users/me',
    '/api/cases/recent'
];

// Install event - cache static files
self.addEventListener('install', event => {
    console.log('Service Worker: Installing...');
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('Service Worker: Caching static files');
                return cache.addAll(STATIC_FILES);
            })
            .then(() => {
                console.log('Service Worker: Skip waiting');
                return self.skipWaiting();
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('Service Worker: Activating...');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cache => {
                    if (cache !== STATIC_CACHE && cache !== DYNAMIC_CACHE) {
                        console.log('Service Worker: Deleting old cache', cache);
                        return caches.delete(cache);
                    }
                })
            );
        }).then(() => {
            console.log('Service Worker: Claiming clients');
            return self.clients.claim();
        })
    );
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', event => {
    const request = event.request;
    const url = new URL(request.url);
    
    // Handle API requests
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            handleApiRequest(request)
        );
        return;
    }
    
    // Handle static files
    event.respondWith(
        caches.match(request)
            .then(response => {
                if (response) {
                    return response;
                }
                
                return fetch(request)
                    .then(fetchResponse => {
                        // Don't cache non-successful responses
                        if (!fetchResponse || fetchResponse.status !== 200) {
                            return fetchResponse;
                        }
                        
                        // Cache dynamic content
                        const responseToCache = fetchResponse.clone();
                        caches.open(DYNAMIC_CACHE)
                            .then(cache => {
                                cache.put(request, responseToCache);
                            });
                        
                        return fetchResponse;
                    })
                    .catch(() => {
                        // Return offline page for navigation requests
                        if (request.destination === 'document') {
                            return caches.match('/offline.html');
                        }
                    });
            })
    );
});

// Handle API requests with offline support
async function handleApiRequest(request) {
    try {
        // Try network first for API requests
        const response = await fetch(request);
        
        // Cache successful responses for critical endpoints
        if (response.status === 200) {
            const url = new URL(request.url);
            const shouldCache = API_CACHE_PATTERNS.some(pattern => 
                url.pathname.includes(pattern)
            );
            
            if (shouldCache) {
                const cache = await caches.open(DYNAMIC_CACHE);
                cache.put(request, response.clone());
            }
        }
        
        return response;
    } catch (error) {
        // Network failed, try cache
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            // Add offline indicator header
            const headers = new Headers(cachedResponse.headers);
            headers.set('X-Served-By', 'service-worker-cache');
            
            return new Response(cachedResponse.body, {
                status: cachedResponse.status,
                statusText: cachedResponse.statusText,
                headers: headers
            });
        }
        
        // Return offline response for critical endpoints
        if (request.url.includes('/api/users/me')) {
            return new Response(
                JSON.stringify({
                    error: 'offline',
                    message: 'User data unavailable offline'
                }),
                {
                    status: 503,
                    headers: { 'Content-Type': 'application/json' }
                }
            );
        }
        
        throw error;
    }
}

// Background sync event
self.addEventListener('sync', event => {
    console.log('Service Worker: Background sync triggered', event.tag);
    
    if (event.tag === 'patient-data-sync') {
        event.waitUntil(syncPatientData());
    } else if (event.tag === 'audit-log-sync') {
        event.waitUntil(syncAuditLogs());
    } else if (event.tag === 'decision-cache-update') {
        event.waitUntil(updateDecisionCache());
    }
});

// Push notification event
self.addEventListener('push', event => {
    console.log('Service Worker: Push received');
    
    if (!event.data) {
        return;
    }
    
    const data = event.data.json();
    const options = {
        body: data.body,
        icon: data.icon || '/icons/icon-192x192.png',
        badge: data.badge || '/icons/badge-72x72.png',
        tag: data.tag,
        requireInteraction: data.requireInteraction || false,
        vibrate: data.vibrate || [100, 50, 100],
        data: data.data || {},
        actions: data.actions || [],
        timestamp: data.timestamp ? new Date(data.timestamp).getTime() : Date.now()
    };
    
    // Add clinical urgency styling
    if (data.data && data.data.clinical_urgency) {
        options.requireInteraction = true;
        options.vibrate = [300, 100, 300, 100, 300];
    }
    
    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

// Notification click event
self.addEventListener('notificationclick', event => {
    console.log('Service Worker: Notification clicked');
    
    event.notification.close();
    
    const data = event.notification.data || {};
    let url = '/dashboard';
    
    // Navigate based on notification data
    if (data.case_id) {
        url = `/cases/${data.case_id}`;
    } else if (data.patient_id) {
        url = `/patients/${data.patient_id}`;
    } else if (data.url) {
        url = data.url;
    }
    
    event.waitUntil(
        clients.matchAll({ type: 'window' })
            .then(clientList => {
                // Focus existing window if available
                for (const client of clientList) {
                    if (client.url.includes(url) && 'focus' in client) {
                        return client.focus();
                    }
                }
                
                // Open new window
                if (clients.openWindow) {
                    return clients.openWindow(url);
                }
            })
    );
});

// Background sync functions
async function syncPatientData() {
    try {
        console.log('Service Worker: Syncing patient data');
        
        // Get pending sync jobs from IndexedDB
        const pendingJobs = await getPendingSyncJobs('patient-data-sync');
        
        for (const job of pendingJobs) {
            try {
                const response = await fetch('/api/background-sync/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(job)
                });
                
                if (response.ok) {
                    await removeSyncJob(job.id);
                    console.log('Service Worker: Patient data synced successfully');
                }
            } catch (error) {
                console.error('Service Worker: Failed to sync patient data', error);
            }
        }
    } catch (error) {
        console.error('Service Worker: Background sync failed', error);
    }
}

async function syncAuditLogs() {
    try {
        console.log('Service Worker: Syncing audit logs');
        // Implementation for audit log sync
    } catch (error) {
        console.error('Service Worker: Audit log sync failed', error);
    }
}

async function updateDecisionCache() {
    try {
        console.log('Service Worker: Updating decision cache');
        // Implementation for decision cache update
    } catch (error) {
        console.error('Service Worker: Decision cache update failed', error);
    }
}

// IndexedDB helpers for background sync
async function getPendingSyncJobs(type) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('adci-sync', 1);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction(['sync-jobs'], 'readonly');
            const store = transaction.objectStore('sync-jobs');
            const index = store.index('type');
            const getRequest = index.getAll(type);
            
            getRequest.onsuccess = () => resolve(getRequest.result);
            getRequest.onerror = () => reject(getRequest.error);
        };
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            const store = db.createObjectStore('sync-jobs', { keyPath: 'id' });
            store.createIndex('type', 'type', { unique: false });
        };
    });
}

async function removeSyncJob(jobId) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('adci-sync', 1);
        
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction(['sync-jobs'], 'readwrite');
            const store = transaction.objectStore('sync-jobs');
            const deleteRequest = store.delete(jobId);
            
            deleteRequest.onsuccess = () => resolve();
            deleteRequest.onerror = () => reject(deleteRequest.error);
        };
    });
}

console.log('Service Worker: Loaded');
"""
        return sw_content
