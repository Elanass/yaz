// Service Worker for Decision Precision in Surgery PWA
// Provides offline functionality, caching, and background sync

const CACHE_NAME = 'surgify-v1.0';
const STATIC_CACHE = 'surgify-static-v1.0';
const DYNAMIC_CACHE = 'surgify-dynamic-v1.0';
const OFFLINE_FALLBACK = '/offline.html';

// Assets to cache immediately
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/static/manifest.json',
  '/static/css/main.css',
  '/static/js/app.js',
  '/static/icons/logo192.png',
  '/static/icons/logo512.png',
  // Add more static assets as needed
];

// API endpoints to cache
const API_CACHE_PATTERNS = [
  /^\/api\/v1\/journal/,
  /^\/api\/v1\/decisions/,
  /^\/api\/v1\/surgery/,
  /^\/api\/v1\/protocols/,
];

// Install Service Worker
self.addEventListener('install', event => {
  console.log('Service Worker installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {
        console.log('Caching static assets...');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate Service Worker
self.addEventListener('activate', event => {
  console.log('Service Worker activating...');
  
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log('Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => self.clients.claim())
  );
});

// Fetch Strategy
self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Handle API requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
    return;
  }

  // Handle static assets
  if (isStaticAsset(request)) {
    event.respondWith(handleStaticAsset(request));
    return;
  }

  // Handle navigation requests
  if (request.mode === 'navigate') {
    event.respondWith(handleNavigation(request));
    return;
  }

  // Default: Network first, then cache
  event.respondWith(
    fetch(request)
      .then(response => {
        // Cache successful responses
        if (response.status === 200) {
          const responseClone = response.clone();
          caches.open(DYNAMIC_CACHE)
            .then(cache => cache.put(request, responseClone));
        }
        return response;
      })
      .catch(() => {
        return caches.match(request);
      })
  );
});

// Handle API requests with cache-first for clinical data
async function handleApiRequest(request) {
  const url = new URL(request.url);
  
  // Check if this API endpoint should be cached
  const shouldCache = API_CACHE_PATTERNS.some(pattern => 
    pattern.test(url.pathname)
  );

  if (shouldCache) {
    // Cache first for clinical data
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      console.log('Serving from cache:', request.url);
      
      // Update cache in background
      fetch(request)
        .then(response => {
          if (response.status === 200) {
            caches.open(DYNAMIC_CACHE)
              .then(cache => cache.put(request, response.clone()));
          }
        })
        .catch(console.error);
      
      return cachedResponse;
    }
  }

  // Network first for other API requests
  try {
    const response = await fetch(request);
    
    if (response.status === 200 && shouldCache) {
      const responseClone = response.clone();
      const cache = await caches.open(DYNAMIC_CACHE);
      await cache.put(request, responseClone);
    }
    
    return response;
  } catch (error) {
    console.error('Network request failed:', error);
    
    // Try to serve from cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline page or error response
    return new Response(
      JSON.stringify({ 
        error: 'Offline', 
        message: 'You are currently offline. Some features may be limited.' 
      }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Handle static assets with cache first
async function handleStaticAsset(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    const response = await fetch(request);
    if (response.status === 200) {
      const cache = await caches.open(STATIC_CACHE);
      await cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.error('Failed to fetch static asset:', error);
    return cachedResponse || new Response('Asset not found', { status: 404 });
  }
}

// Handle navigation requests
async function handleNavigation(request) {
  try {
    const response = await fetch(request);
    return response;
  } catch (error) {
    console.error('Navigation request failed:', error);
    
    // Try to serve cached version
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Serve offline page
    return caches.match('/dashboard') || new Response('Offline', { status: 503 });
  }
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
         url.pathname.includes('.ico');
}

// Background Sync for clinical data
self.addEventListener('sync', event => {
  console.log('Background sync triggered:', event.tag);
  
  if (event.tag === 'clinical-data-sync') {
    event.waitUntil(syncClinicalData());
  }
});

// Sync clinical data when connection is restored
async function syncClinicalData() {
  try {
    console.log('Syncing clinical data...');
    
    // Get pending sync requests from IndexedDB or localStorage
    // This would typically involve syncing:
    // - Offline case modifications
    // - Decision analyses
    // - Journal entries
    // - Protocol updates
    
    const response = await fetch('/api/v1/sync/clinical-data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        timestamp: Date.now(),
        source: 'service-worker'
      })
    });
    
    if (response.ok) {
      console.log('Clinical data sync completed successfully');
      
      // Clear pending sync data
      // await clearPendingSyncData();
      
      // Notify client about successful sync
      const clients = await self.clients.matchAll();
      clients.forEach(client => {
        client.postMessage({
          type: 'SYNC_COMPLETED',
          status: 'success'
        });
      });
    } else {
      throw new Error('Sync failed with status: ' + response.status);
    }
    
  } catch (error) {
    console.error('Clinical data sync failed:', error);
    
    // Notify client about sync failure
    const clients = await self.clients.matchAll();
    clients.forEach(client => {
      client.postMessage({
        type: 'SYNC_COMPLETED',
        status: 'error',
        error: error.message
      });
    });
  }
}

// Push notification handler for clinical alerts
self.addEventListener('push', event => {
  console.log('Push notification received');
  
  const options = {
    body: 'You have new clinical updates',
    icon: '/static/icons/logo192.png',
    badge: '/static/icons/logo192.png',
    tag: 'clinical-alert',
    requireInteraction: true,
    actions: [
      {
        action: 'view',
        title: 'View Details'
      },
      {
        action: 'dismiss',
        title: 'Dismiss'
      }
    ]
  };

  if (event.data) {
    const data = event.data.json();
    options.body = data.message || options.body;
    options.tag = data.tag || options.tag;
  }

  event.waitUntil(
    self.registration.showNotification('Gastric ADCI Platform', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', event => {
  event.notification.close();

  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow('/dashboard')
    );
  }
});

// Periodic background sync (if supported)
self.addEventListener('periodicsync', event => {
  if (event.tag === 'clinical-data-check') {
    event.waitUntil(checkForClinicalUpdates());
  }
});

async function checkForClinicalUpdates() {
  try {
    const response = await fetch('/api/v1/updates/check');
    const updates = await response.json();
    
    if (updates.hasUpdates) {
      // Show notification about available updates
      await self.registration.showNotification('Clinical Updates Available', {
        body: `${updates.count} new clinical updates are available`,
        icon: '/static/icons/logo192.png',
        tag: 'clinical-updates'
      });
    }
  } catch (error) {
    console.error('Failed to check for updates:', error);
  }
}

console.log('Service Worker loaded successfully');
