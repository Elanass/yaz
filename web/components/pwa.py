"""
PWA (Progressive Web App) configuration and service worker
"""

import json

from fasthtml.common import *


def create_pwa_manifest():
    """Create PWA manifest file"""
    
    manifest = {
        "name": "Gastric ADCI Platform",
        "short_name": "ADCI",
        "description": "Gastric Oncology-Surgery Decision Support Platform",
        "start_url": "/",
        "display": "standalone",
        "theme_color": "#2563eb",
        "background_color": "#ffffff",
        "orientation": "portrait-primary",
        "scope": "/",
        "icons": [
            {
                "src": "/static/icons/icon-72x72.png",
                "sizes": "72x72",
                "type": "image/png",
                "purpose": "maskable any"
            },
            {
                "src": "/static/icons/icon-96x96.png", 
                "sizes": "96x96",
                "type": "image/png",
                "purpose": "maskable any"
            },
            {
                "src": "/static/icons/icon-128x128.png",
                "sizes": "128x128", 
                "type": "image/png",
                "purpose": "maskable any"
            },
            {
                "src": "/static/icons/icon-144x144.png",
                "sizes": "144x144",
                "type": "image/png",
                "purpose": "maskable any"
            },
            {
                "src": "/static/icons/icon-152x152.png",
                "sizes": "152x152",
                "type": "image/png",
                "purpose": "maskable any"
            },
            {
                "src": "/static/icons/icon-192x192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "maskable any"
            },
            {
                "src": "/static/icons/icon-384x384.png",
                "sizes": "384x384",
                "type": "image/png",
                "purpose": "maskable any"
            },
            {
                "src": "/static/icons/icon-512x512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "maskable any"
            }
        ],
        "categories": ["medical", "health", "productivity"],
        "screenshots": [
            {
                "src": "/static/screenshots/mobile-1.png",
                "sizes": "640x1136",
                "type": "image/png",
                "form_factor": "narrow"
            },
            {
                "src": "/static/screenshots/desktop-1.png", 
                "sizes": "1280x720",
                "type": "image/png",
                "form_factor": "wide"
            }
        ],
        "shortcuts": [
            {
                "name": "Decision Support",
                "short_name": "Decision",
                "description": "Access clinical decision support tools",
                "url": "/decision-support",
                "icons": [
                    {
                        "src": "/static/icons/decision-icon.png",
                        "sizes": "96x96"
                    }
                ]
            },
            {
                "name": "Protocols",
                "short_name": "Protocols",
                "description": "Browse clinical protocols",
                "url": "/protocols",
                "icons": [
                    {
                        "src": "/static/icons/protocols-icon.png",
                        "sizes": "96x96"
                    }
                ]
            }
        ],
        "prefer_related_applications": False,
        "protocol_handlers": [
            {
                "protocol": "web+gastric-adci",
                "url": "/protocol-handler?type=%s"
            }
        ]
    }
    
    return Response(
        content=json.dumps(manifest, indent=2),
        media_type="application/json",
        headers={"Cache-Control": "public, max-age=31536000"}
    )


def create_service_worker():
    """Create service worker for PWA functionality"""
    
    sw_content = """
// Gastric ADCI Platform Service Worker
// Provides offline functionality, caching, and background sync

const CACHE_NAME = 'gastric-adci-v1.0.0';
const OFFLINE_URL = '/offline';

// Files to cache for offline functionality
const CACHE_URLS = [
    '/',
    '/offline',
    '/static/css/app.css',
    '/static/js/app.js',
    '/static/js/gun-integration.js',
    '/static/js/pwa.js',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-512x512.png',
    // External dependencies
    'https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css',
    'https://unpkg.com/htmx.org@1.9.6/dist/htmx.min.js',
    'https://cdn.jsdelivr.net/npm/gun/gun.js',
    'https://cdn.jsdelivr.net/npm/chart.js'
];

// Install event - cache essential files
self.addEventListener('install', event => {
    console.log('[SW] Install event');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('[SW] Caching app shell');
                return cache.addAll(CACHE_URLS);
            })
            .then(() => {
                console.log('[SW] Skip waiting');
                return self.skipWaiting();
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('[SW] Activate event');
    
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== CACHE_NAME) {
                            console.log('[SW] Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('[SW] Claiming clients');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', event => {
    // Skip non-GET requests
    if (event.request.method !== 'GET') return;
    
    // Skip Chrome extensions
    if (event.request.url.startsWith('chrome-extension://')) return;
    
    // Handle API requests with network-first strategy
    if (event.request.url.includes('/api/')) {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    // Cache successful API responses for offline access
                    if (response.status === 200) {
                        const responseClone = response.clone();
                        caches.open(CACHE_NAME)
                            .then(cache => {
                                cache.put(event.request, responseClone);
                            });
                    }
                    return response;
                })
                .catch(() => {
                    // Return cached API response if available
                    return caches.match(event.request)
                        .then(response => {
                            if (response) {
                                return response;
                            }
                            // Return offline message for failed API calls
                            return new Response(
                                JSON.stringify({
                                    error: 'Offline',
                                    message: 'This feature requires an internet connection'
                                }),
                                {
                                    status: 503,
                                    headers: {
                                        'Content-Type': 'application/json'
                                    }
                                }
                            );
                        });
                })
        );
        return;
    }
    
    // Handle page requests with cache-first strategy
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                if (response) {
                    return response;
                }
                
                return fetch(event.request)
                    .then(response => {
                        // Don't cache non-successful responses
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }
                        
                        // Cache the response
                        const responseToCache = response.clone();
                        caches.open(CACHE_NAME)
                            .then(cache => {
                                cache.put(event.request, responseToCache);
                            });
                        
                        return response;
                    })
                    .catch(() => {
                        // Return offline page for navigation requests
                        if (event.request.mode === 'navigate') {
                            return caches.match(OFFLINE_URL);
                        }
                        
                        // Return a fallback response for other requests
                        return new Response(
                            'Content not available offline',
                            {
                                status: 503,
                                statusText: 'Service Unavailable'
                            }
                        );
                    });
            })
    );
});

// Background sync for form submissions
self.addEventListener('sync', event => {
    console.log('[SW] Background sync event:', event.tag);
    
    if (event.tag === 'background-sync-decision') {
        event.waitUntil(syncDecisionRequests());
    }
    
    if (event.tag === 'background-sync-patient-data') {
        event.waitUntil(syncPatientData());
    }
});

// Push notification handling
self.addEventListener('push', event => {
    console.log('[SW] Push event');
    
    if (!event.data) return;
    
    const data = event.data.json();
    const title = data.title || 'Gastric ADCI Platform';
    const options = {
        body: data.body || 'You have a new notification',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/badge-72x72.png',
        data: data,
        actions: [
            {
                action: 'view',
                title: 'View',
                icon: '/static/icons/view-icon.png'
            },
            {
                action: 'dismiss',
                title: 'Dismiss',
                icon: '/static/icons/dismiss-icon.png'
            }
        ],
        requireInteraction: data.critical || false,
        silent: false,
        vibrate: [200, 100, 200]
    };
    
    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
    console.log('[SW] Notification click event');
    
    const notification = event.notification;
    const action = event.action;
    
    if (action === 'dismiss') {
        notification.close();
        return;
    }
    
    // Default action or 'view' action
    event.waitUntil(
        clients.matchAll({ type: 'window' })
            .then(clientsArr => {
                // Check if there's already a window/tab open
                const hadWindowToFocus = clientsArr.some(windowClient => {
                    if (windowClient.url === notification.data.url) {
                        windowClient.focus();
                        return true;
                    }
                    return false;
                });
                
                // If not, open a new window/tab
                if (!hadWindowToFocus) {
                    clients.openWindow(notification.data.url || '/');
                }
                
                notification.close();
            })
    );
});

// Background sync functions
async function syncDecisionRequests() {
    try {
        console.log('[SW] Syncing decision requests');
        
        // Get pending requests from IndexedDB
        const pendingRequests = await getPendingDecisionRequests();
        
        for (const request of pendingRequests) {
            try {
                const response = await fetch('/api/v1/decision-engine/process', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${request.token}`
                    },
                    body: JSON.stringify(request.data)
                });
                
                if (response.ok) {
                    await removePendingDecisionRequest(request.id);
                    console.log('[SW] Synced decision request:', request.id);
                }
            } catch (error) {
                console.error('[SW] Failed to sync decision request:', error);
            }
        }
    } catch (error) {
        console.error('[SW] Background sync failed:', error);
    }
}

async function syncPatientData() {
    try {
        console.log('[SW] Syncing patient data');
        
        // ElectricsQL will handle most of the sync
        // This is for additional custom sync logic
        
        const pendingUpdates = await getPendingPatientUpdates();
        
        for (const update of pendingUpdates) {
            try {
                const response = await fetch(`/api/v1/patients/${update.patientId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${update.token}`
                    },
                    body: JSON.stringify(update.data)
                });
                
                if (response.ok) {
                    await removePendingPatientUpdate(update.id);
                    console.log('[SW] Synced patient data:', update.id);
                }
            } catch (error) {
                console.error('[SW] Failed to sync patient data:', error);
            }
        }
    } catch (error) {
        console.error('[SW] Patient data sync failed:', error);
    }
}

// IndexedDB helper functions (simplified)
async function getPendingDecisionRequests() {
    // Implementation would use IndexedDB to store/retrieve pending requests
    return [];
}

async function removePendingDecisionRequest(id) {
    // Implementation would remove from IndexedDB
}

async function getPendingPatientUpdates() {
    // Implementation would use IndexedDB to store/retrieve pending updates
    return [];
}

async function removePendingPatientUpdate(id) {
    // Implementation would remove from IndexedDB
}

// Log service worker registration
console.log('[SW] Service Worker registered successfully');
    """
    
    return Response(
        content=sw_content,
        media_type="application/javascript",
        headers={
            "Cache-Control": "public, max-age=0",  # Don't cache service worker
            "Service-Worker-Allowed": "/"
        }
    )
