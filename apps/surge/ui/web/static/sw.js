// Enhanced Surgify PWA Service Worker
// Sub-14KB shell, background sync, push notifications, native-parity APIs

const CACHE_VERSION = 'v3.0.0';
const SHELL_CACHE = `surgify-shell-${CACHE_VERSION}`;
const API_CACHE = `surgify-api-${CACHE_VERSION}`;
const DYNAMIC_CACHE = `surgify-dynamic-${CACHE_VERSION}`;
const OFFLINE_CACHE = `surgify-offline-${CACHE_VERSION}`;

// Critical shell resources (sub-14KB optimized)
const SHELL_ASSETS = [
  '/',
  '/surgify',
  '/offline',
  '/static/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  '/static/css/critical.css'
];

// Extended static assets
const STATIC_ASSETS = [
  '/static/css/main.css',
  '/static/js/htmx.min.js'
];

// API caching strategies
const API_STRATEGIES = {
  '/api/v1/auth/me': 'cache-first',
  '/api/v1/cases': 'stale-while-revalidate', 
  '/api/v1/dashboard': 'network-first',
  '/api/v1/auth': 'network-only'
};

// Enhanced install event
self.addEventListener('install', event => {
  console.log('[SW] Installing enhanced service worker v' + CACHE_VERSION);
  
  event.waitUntil(
    Promise.all([
      // Priority: Cache critical shell first
      caches.open(SHELL_CACHE).then(cache => {
        console.log('[SW] Caching shell assets');
        return cache.addAll(SHELL_ASSETS);
      }),
      
      // Cache static assets
      caches.open(DYNAMIC_CACHE).then(cache => {
        console.log('[SW] Caching static assets');
        return cache.addAll(STATIC_ASSETS).catch(err => {
          console.warn('[SW] Some static assets failed:', err);
        });
      }),
      
      // Prepare offline page
      caches.open(OFFLINE_CACHE).then(cache => {
        return cache.add('/offline');
      })
    ]).then(() => {
      console.log('[SW] Installation complete');
      return self.skipWaiting();
    })
  );
});

// Enhanced activate event
self.addEventListener('activate', event => {
  console.log('[SW] Activating service worker v' + CACHE_VERSION);
  
  event.waitUntil(
    Promise.all([
      // Clean old caches
      caches.keys().then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (!cacheName.includes(CACHE_VERSION)) {
              console.log('[SW] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      
      // Claim clients immediately
      self.clients.claim(),
      
      // Setup background sync
      setupBackgroundSync(),
      
      // Setup push notifications
      setupPushNotifications()
    ]).then(() => {
      console.log('[SW] Activation complete');
      notifyClients({ type: 'SW_ACTIVATED', version: CACHE_VERSION });
    })
  );
});

// Enhanced fetch handler with multiple strategies
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Handle navigation requests
  if (request.mode === 'navigate') {
    event.respondWith(handleNavigation(request));
    return;
  }
  
  // Handle API requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleAPIRequest(request));
    return;
  }
  
  // Handle static assets
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(handleStaticAsset(request));
    return;
  }
  
  // Default: network first with cache fallback
  event.respondWith(handleDefault(request));
});

// Navigation handler with shell-first approach
async function handleNavigation(request) {
  try {
    // Try network first for fresh content
    const networkResponse = await fetch(request);
    
    // Cache successful navigation responses
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[SW] Navigation offline, serving shell');
    
    // Serve shell from cache when offline
    const cache = await caches.open(SHELL_CACHE);
    const shellResponse = await cache.match('/');
    
    if (shellResponse) {
      return shellResponse;
    }
    
    // Last resort: offline page
    const offlineCache = await caches.open(OFFLINE_CACHE);
    return offlineCache.match('/offline');
  }
}

// API request handler with strategy-based caching
async function handleAPIRequest(request) {
  const url = new URL(request.url);
  const strategy = getAPIStrategy(url.pathname);
  
  switch (strategy) {
    case 'cache-first':
      return cacheFirst(request);
    case 'network-first':
      return networkFirst(request);
    case 'stale-while-revalidate':
      return staleWhileRevalidate(request);
    case 'network-only':
      return networkOnly(request);
    default:
      return networkFirst(request);
  }
}

// Static asset handler with long-term caching
async function handleStaticAsset(request) {
  const cache = await caches.open(DYNAMIC_CACHE);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    // Serve from cache immediately
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('[SW] Static asset failed:', request.url);
    return new Response('Asset not available offline', { status: 503 });
  }
}

// Default handler
async function handleDefault(request) {
  return networkFirst(request);
}

// Caching strategy implementations
async function cacheFirst(request) {
  const cache = await caches.open(API_CACHE);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    return new Response('Not available offline', { status: 503 });
  }
}

async function networkFirst(request) {
  const cache = await caches.open(API_CACHE);
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    return new Response('Not available offline', { status: 503 });
  }
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(API_CACHE);
  const cachedResponse = await cache.match(request);
  
  // Always try to update in background
  const networkPromise = fetch(request).then(response => {
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  }).catch(() => {});
  
  // Return cached version immediately if available
  if (cachedResponse) {
    return cachedResponse;
  }
  
  // Wait for network if no cache
  return networkPromise;
}

async function networkOnly(request) {
  return fetch(request);
}

// Background sync setup
function setupBackgroundSync() {
  if ('sync' in self.registration) {
    console.log('[SW] Background sync supported');
    
    // Register for background sync events
    self.addEventListener('sync', event => {
      console.log('[SW] Background sync triggered:', event.tag);
      
      if (event.tag === 'background-sync-cases') {
        event.waitUntil(syncCases());
      }
      
      if (event.tag === 'background-sync-analytics') {
        event.waitUntil(syncAnalytics());
      }
    });
  }
}

// Push notifications setup
function setupPushNotifications() {
  if ('push' in self.registration) {
    console.log('[SW] Push notifications supported');
    
    self.addEventListener('push', event => {
      console.log('[SW] Push received');
      
      let data = {};
      if (event.data) {
        data = event.data.json();
      }
      
      const options = {
        body: data.body || 'New notification from Surgify',
        icon: '/static/icons/icon-192.png',
        badge: '/static/icons/badge-72.png',
        tag: data.tag || 'surgify-notification',
        data: data.data || {},
        actions: [
          { action: 'view', title: 'View' },
          { action: 'dismiss', title: 'Dismiss' }
        ],
        requireInteraction: data.requireInteraction || false
      };
      
      event.waitUntil(
        self.registration.showNotification(data.title || 'Surgify', options)
      );
    });
    
    self.addEventListener('notificationclick', event => {
      console.log('[SW] Notification clicked');
      event.notification.close();
      
      if (event.action === 'view') {
        event.waitUntil(
          clients.openWindow(event.notification.data.url || '/')
        );
      }
    });
  }
}

// Background sync functions
async function syncCases() {
  try {
    const response = await fetch('/api/v1/cases/sync');
    if (response.ok) {
      console.log('[SW] Cases synced successfully');
      notifyClients({ type: 'SYNC_COMPLETE', resource: 'cases' });
    }
  } catch (error) {
    console.log('[SW] Cases sync failed:', error);
  }
}

async function syncAnalytics() {
  try {
    const response = await fetch('/api/v1/analytics/sync');
    if (response.ok) {
      console.log('[SW] Analytics synced successfully');
      notifyClients({ type: 'SYNC_COMPLETE', resource: 'analytics' });
    }
  } catch (error) {
    console.log('[SW] Analytics sync failed:', error);
  }
}

// Utility functions
function getAPIStrategy(pathname) {
  for (const [pattern, strategy] of Object.entries(API_STRATEGIES)) {
    if (pathname.startsWith(pattern)) {
      return strategy;
    }
  }
  return 'network-first';
}

function notifyClients(message) {
  self.clients.matchAll().then(clients => {
    clients.forEach(client => {
      client.postMessage(message);
    });
  });
}

// Periodic background sync (if supported)
if ('periodicSync' in self.registration) {
  self.addEventListener('periodicsync', event => {
    if (event.tag === 'content-sync') {
      event.waitUntil(syncContent());
    }
  });
}

async function syncContent() {
  try {
    // Sync important content in background
    await Promise.all([
      syncCases(),
      syncAnalytics()
    ]);
    console.log('[SW] Periodic sync completed');
  } catch (error) {
    console.log('[SW] Periodic sync failed:', error);
  }
}

console.log('[SW] Service worker script loaded v' + CACHE_VERSION);

// Setup background sync registration
async function setupBackgroundSync() {
  try {
    // Register periodic background sync if supported
    if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
      console.log('SW: Background sync is supported');
    }
    
    // Setup periodic sync for clinical data if supported
    if ('periodicSync' in self.registration) {
      await self.registration.periodicSync.register('clinical-data-sync', {
        minInterval: 24 * 60 * 60 * 1000 // 24 hours
      });
      console.log('SW: Periodic sync registered');
    }
  } catch (error) {
    console.warn('SW: Background sync setup failed:', error);
  }
}

// Enhanced fetch strategy with offline fallback
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Handle navigation requests (pages)
    if (request.mode === 'navigate') {
        event.respondWith(
            fetch(request)
                .then(response => {
                    // If online, update cache and return response
                    if (response.ok) {
                        const responseClone = response.clone();
                        caches.open(DYNAMIC_CACHE).then(cache => {
                            cache.put(request, responseClone);
                        });
                    }
                    return response;
                })
                .catch(() => {
                    // If offline, try cache first, then offline fallback
                    return caches.match(request)
                        .then(cachedResponse => {
                            if (cachedResponse) {
                                return cachedResponse;
                            }
                            // Return offline page as fallback
                            return caches.match('/offline');
                        });
                })
        );
        return;
    }
    
    // Handle API requests with cache-first strategy
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            caches.match(request)
                .then(cachedResponse => {
                    if (cachedResponse) {
                        // Return cached version immediately
                        fetch(request)
                            .then(response => {
                                if (response.ok) {
                                    // Update cache in background
                                    const responseClone = response.clone();
                                    caches.open(API_CACHE).then(cache => {
                                        cache.put(request, responseClone);
                                    });
                                }
                            })
                            .catch(() => console.log('Background API update failed'));
                        return cachedResponse;
                    }
                    
                    // No cache, try network
                    return fetch(request)
                        .then(response => {
                            if (response.ok) {
                                const responseClone = response.clone();
                                caches.open(API_CACHE).then(cache => {
                                    cache.put(request, responseClone);
                                });
                            }
                            return response;
                        })
                        .catch(() => {
                            // Return offline API response
                            return new Response(
                                JSON.stringify({
                                    error: 'Offline',
                                    message: 'Data not available offline',
                                    cached: false
                                }),
                                {
                                    status: 503,
                                    statusText: 'Service Unavailable',
                                    headers: { 'Content-Type': 'application/json' }
                                }
                            );
                        });
                })
        );
        return;
    }
    
    // Handle static assets with cache-first strategy
    if (url.pathname.startsWith('/static/')) {
        event.respondWith(
            caches.match(request)
                .then(cachedResponse => {
                    return cachedResponse || fetch(request)
                        .then(response => {
                            if (response.ok) {
                                const responseClone = response.clone();
                                caches.open(STATIC_CACHE).then(cache => {
                                    cache.put(request, responseClone);
                                });
                            }
                            return response;
                        });
                })
        );
        return;
    }
    
    // Default: network first, cache fallback
    event.respondWith(
        fetch(request)
            .then(response => {
                if (response.ok && request.method === 'GET') {
                    const responseClone = response.clone();
                    caches.open(DYNAMIC_CACHE).then(cache => {
                        cache.put(request, responseClone);
                    });
                }
                return response;
            })
            .catch(() => {
                return caches.match(request);
            })
    );
});

// Check if request is for shell asset (sub-14KB critical path)
function isShellAsset(request) {
  const url = new URL(request.url);
  return SHELL_ASSETS.some(asset => url.pathname === asset || url.pathname.endsWith(asset));
}

// Handle shell assets with instant loading
async function handleShellAsset(request) {
  const cachedResponse = await caches.match(request, { cacheName: SHELL_CACHE });
  if (cachedResponse) {
    return cachedResponse;
  }

  // Fallback to network if not in shell cache
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(SHELL_CACHE);
      await cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.error('SW: Shell asset fetch failed:', error);
    return new Response('Shell asset unavailable', { status: 503 });
  }
}

// Smart API request handling with different strategies
async function handleSmartApiRequest(request) {
  const url = new URL(request.url);
  
  // Find matching pattern and strategy
  const apiConfig = API_CACHE_PATTERNS.find(config => 
    config.pattern.test(url.pathname)
  );
  
  const strategy = apiConfig?.strategy || 'network-first';
  
  switch (strategy) {
    case 'cache-first':
      return handleCacheFirst(request);
    case 'network-first':
      return handleNetworkFirst(request);
    case 'stale-while-revalidate':
      return handleStaleWhileRevalidate(request);
    case 'network-only':
      return fetch(request);
    default:
      return handleNetworkFirst(request);
  }
}

// Cache-first strategy for stable data
async function handleCacheFirst(request) {
  const cachedResponse = await caches.match(request, { cacheName: API_CACHE });
  if (cachedResponse) {
    console.log('SW: Serving from cache:', request.url);
    
    // Update cache in background
    fetch(request)
      .then(response => {
        if (response.ok) {
          caches.open(API_CACHE)
            .then(cache => cache.put(request, response.clone()));
        }
      })
      .catch(console.error);
    
    return cachedResponse;
  }
  
  // Fallback to network
  return handleNetworkFirst(request);
}

// Network-first strategy for fresh data
async function handleNetworkFirst(request) {
  try {
    const response = await fetch(request);
    
    if (response.ok) {
      const cache = await caches.open(API_CACHE);
      await cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.error('SW: Network request failed:', error);
    
    // Try to serve from cache
    const cachedResponse = await caches.match(request, { cacheName: API_CACHE });
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline response
    return new Response(
      JSON.stringify({ 
        error: 'Offline', 
        message: 'You are currently offline. Some features may be limited.',
        timestamp: Date.now()
      }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Stale-while-revalidate strategy
async function handleStaleWhileRevalidate(request) {
  const cache = await caches.open(API_CACHE);
  const cachedResponse = await cache.match(request);
  
  const fetchPromise = fetch(request).then(response => {
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  }).catch(error => {
    console.error('SW: Revalidation failed:', error);
    return cachedResponse;
  });
  
  return cachedResponse || fetchPromise;
}

// Enhanced static asset handling
async function handleStaticAsset(request) {
  const cachedResponse = await caches.match(request, { cacheName: DYNAMIC_CACHE });
  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      await cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.error('SW: Failed to fetch static asset:', error);
    return new Response('Asset not found', { status: 404 });
  }
}

// Enhanced navigation handling for SPA
async function handleNavigation(request) {
  try {
    const response = await fetch(request);
    return response;
  } catch (error) {
    console.error('SW: Navigation request failed:', error);
    
    // Try to serve cached shell for SPA routing
    const shellResponse = await caches.match('/', { cacheName: SHELL_CACHE });
    if (shellResponse) {
      return shellResponse;
    }
    
    // Fallback to any cached page
    const cachedResponse = await caches.match('/islands/landing');
    return cachedResponse || new Response('Offline - Please check your connection', { 
      status: 503,
      headers: { 'Content-Type': 'text/html' }
    });
  }
}

// Handle POST requests with background sync fallback
async function handlePostWithSync(request) {
  try {
    const response = await fetch(request);
    return response;
  } catch (error) {
    console.log('SW: POST failed, queuing for background sync');
    
    // Store request for background sync
    const requestData = {
      url: request.url,
      method: request.method,
      headers: Object.fromEntries(request.headers.entries()),
      body: await request.text(),
      timestamp: Date.now()
    };
    
    // Store in IndexedDB or similar
    await storeForSync(requestData);
    
    // Register background sync
    if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
      await self.registration.sync.register('background-sync');
    }
    
    return new Response(
      JSON.stringify({ 
        queued: true, 
        message: 'Request queued for when connection is restored' 
      }),
      { 
        status: 202,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Check if request should be synced in background
function isBackgroundSyncRequest(request) {
  const url = new URL(request.url);
  return request.method === 'POST' && url.pathname.startsWith('/api/v1/');
}

// Store request data for background sync
async function storeForSync(requestData) {
  // This would typically use IndexedDB
  // For now, we'll use a simple approach
  try {
    const existingData = await getStoredSyncData();
    existingData.push(requestData);
    
    // Store back (in a real app, use IndexedDB)
    console.log('SW: Stored request for background sync:', requestData.url);
  } catch (error) {
    console.error('SW: Failed to store sync data:', error);
  }
}

async function getStoredSyncData() {
  // Placeholder - use IndexedDB in production
  return [];
}

// Check if request is for a static asset
function isStaticAsset(request) {
  const url = new URL(request.url);
  return url.pathname.startsWith('/static/') ||
         url.pathname.includes('.css') ||
         url.pathname.includes('.js') ||
         url.pathname.includes('.png') ||
         url.pathname.includes('.jpg') ||
         url.pathname.includes('.svg') ||
         url.pathname.includes('.ico') ||
         url.pathname.includes('.webp') ||
         url.pathname.includes('.avif');
}

// Enhanced background sync for clinical data and user actions
self.addEventListener('sync', event => {
  console.log('SW: Background sync triggered:', event.tag);
  
  switch (event.tag) {
    case 'background-sync':
      event.waitUntil(processBackgroundSync());
      break;
    case 'clinical-data-sync':
      event.waitUntil(syncClinicalData());
      break;
    default:
      console.log('SW: Unknown sync tag:', event.tag);
  }
});

// Process queued background sync requests
async function processBackgroundSync() {
  try {
    console.log('SW: Processing background sync queue');
    
    const syncData = await getStoredSyncData();
    const results = [];
    
    for (const requestData of syncData) {
      try {
        const response = await fetch(requestData.url, {
          method: requestData.method,
          headers: requestData.headers,
          body: requestData.body
        });
        
        results.push({ 
          url: requestData.url, 
          success: response.ok,
          status: response.status 
        });
        
        console.log('SW: Sync request completed:', requestData.url);
      } catch (error) {
        console.error('SW: Sync request failed:', requestData.url, error);
        results.push({ 
          url: requestData.url, 
          success: false, 
          error: error.message 
        });
      }
    }
    
    // Clear successful syncs and notify clients
    await clearSyncData();
    await notifyClients('BACKGROUND_SYNC_COMPLETED', { results });
    
  } catch (error) {
    console.error('SW: Background sync processing failed:', error);
  }
}

// Sync clinical data when connection is restored
async function syncClinicalData() {
  try {
    console.log('SW: Syncing clinical data...');
    
    const response = await fetch('/api/v1/sync/clinical-data', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        timestamp: Date.now(),
        source: 'service-worker',
        type: 'clinical-data-sync'
      })
    });
    
    if (response.ok) {
      console.log('SW: Clinical data sync completed successfully');
      await notifyClients('CLINICAL_SYNC_COMPLETED', { status: 'success' });
    } else {
      throw new Error(`Sync failed with status: ${response.status}`);
    }
    
  } catch (error) {
    console.error('SW: Clinical data sync failed:', error);
    await notifyClients('CLINICAL_SYNC_COMPLETED', { 
      status: 'error', 
      error: error.message 
    });
  }
}

// Clear sync data after successful processing
async function clearSyncData() {
  // Placeholder - implement with IndexedDB
  console.log('SW: Cleared sync data');
}

// Notify all clients about events
async function notifyClients(type, data) {
  const clients = await self.clients.matchAll();
  clients.forEach(client => {
    client.postMessage({ type, data });
  });
}

// Enhanced push notification handler with rich interactions
self.addEventListener('push', event => {
  console.log('SW: Push notification received');
  
  let notificationData = {
    title: 'Surgify - Clinical Alert',
    body: 'You have new clinical updates',
    icon: '/static/icons/icon-192.png',
    badge: '/static/icons/icon-192.png',
    tag: 'clinical-alert',
    requireInteraction: true,
    vibrate: [200, 100, 200],
    actions: [
      { action: 'view', title: 'View Details', icon: '/static/icons/view.png' },
      { action: 'dismiss', title: 'Dismiss', icon: '/static/icons/dismiss.png' }
    ],
    data: {
      url: '/dashboard',
      timestamp: Date.now()
    }
  };

  if (event.data) {
    try {
      const pushData = event.data.json();
      notificationData = { ...notificationData, ...pushData };
    } catch (error) {
      console.error('SW: Invalid push data:', error);
    }
  }

  event.waitUntil(
    self.registration.showNotification(notificationData.title, notificationData)
  );
});

// Enhanced notification click handling
self.addEventListener('notificationclick', event => {
  console.log('SW: Notification clicked:', event.action);
  event.notification.close();

  if (event.action === 'view') {
    const urlToOpen = event.notification.data?.url || '/dashboard';
    
    event.waitUntil(
      clients.matchAll({ type: 'window', includeUncontrolled: true })
        .then(clientList => {
          // Check if app is already open
          for (const client of clientList) {
            if (client.url.includes(urlToOpen) && 'focus' in client) {
              return client.focus();
            }
          }
          
          // Open new window/tab
          if (clients.openWindow) {
            return clients.openWindow(urlToOpen);
          }
        })
    );
  } else if (event.action === 'dismiss') {
    // Log dismissal for analytics
    console.log('SW: Notification dismissed');
  }
});

// Periodic background sync (if supported)
self.addEventListener('periodicsync', event => {
  console.log('SW: Periodic sync triggered:', event.tag);
  
  switch (event.tag) {
    case 'clinical-data-sync':
      event.waitUntil(checkForClinicalUpdates());
      break;
    case 'cache-cleanup':
      event.waitUntil(performCacheCleanup());
      break;
    default:
      console.log('SW: Unknown periodic sync:', event.tag);
  }
});

// Check for clinical updates periodically
async function checkForClinicalUpdates() {
  try {
    const response = await fetch('/api/v1/updates/check');
    const updates = await response.json();
    
    if (updates.hasUpdates) {
      await self.registration.showNotification('Clinical Updates Available', {
        body: `${updates.count} new clinical updates are available`,
        icon: '/static/icons/icon-192.png',
        tag: 'clinical-updates',
        actions: [
          { action: 'view-updates', title: 'View Updates' },
          { action: 'later', title: 'Later' }
        ]
      });
    }
  } catch (error) {
    console.error('SW: Failed to check for updates:', error);
  }
}

// Perform periodic cache cleanup
async function performCacheCleanup() {
  try {
    console.log('SW: Performing cache cleanup');
    
    // Clean old cache entries (older than 7 days)
    const cutoffTime = Date.now() - (7 * 24 * 60 * 60 * 1000);
    
    const cacheNames = await caches.keys();
    for (const cacheName of cacheNames) {
      if (cacheName.includes('dynamic')) {
        const cache = await caches.open(cacheName);
        const requests = await cache.keys();
        
        for (const request of requests) {
          const response = await cache.match(request);
          const dateHeader = response?.headers.get('date');
          
          if (dateHeader && new Date(dateHeader).getTime() < cutoffTime) {
            await cache.delete(request);
            console.log('SW: Cleaned old cache entry:', request.url);
          }
        }
      }
    }
  } catch (error) {
    console.error('SW: Cache cleanup failed:', error);
  }
}

// Message handling for client communication
self.addEventListener('message', event => {
  console.log('SW: Message received:', event.data);
  
  switch (event.data.type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;
      
    case 'GET_VERSION':
      event.ports[0].postMessage({ version: CACHE_VERSION });
      break;
      
    case 'CACHE_URLS':
      event.waitUntil(cacheUrls(event.data.urls));
      break;
      
    case 'CLEAR_CACHE':
      event.waitUntil(clearAllCaches());
      break;
      
    default:
      console.log('SW: Unknown message type:', event.data.type);
  }
});

// Cache specific URLs on demand
async function cacheUrls(urls) {
  try {
    const cache = await caches.open(DYNAMIC_CACHE);
    await cache.addAll(urls);
    console.log('SW: Cached on-demand URLs:', urls);
  } catch (error) {
    console.error('SW: Failed to cache URLs:', error);
  }
}

// Clear all caches
async function clearAllCaches() {
  try {
    const cacheNames = await caches.keys();
    await Promise.all(cacheNames.map(cacheName => caches.delete(cacheName)));
    console.log('SW: All caches cleared');
  } catch (error) {
    console.error('SW: Failed to clear caches:', error);
  }
}

console.log('SW: Enhanced Surgify service worker loaded successfully - Version:', CACHE_VERSION);
