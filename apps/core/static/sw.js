// YAZ Healthcare Platform Service Worker
// Provides offline functionality and caching for PWA

const CACHE_NAME = 'yaz-healthcare-v1';
const OFFLINE_URL = '/dashboard';

const STATIC_CACHE_URLS = [
  '/dashboard',
  '/static/js/websocket-manager.js',
  '/static/js/data-manager.js',
  '/static/js/components.js',
  '/static/css/dashboard.css',
  '/static/manifest.json',
  'https://cdn.tailwindcss.com',
  'https://unpkg.com/htmx.org@1.9.6',
  'https://cdn.jsdelivr.net/npm/chart.js',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
];

const API_CACHE_URLS = [
  '/api/v1/dashboard/stats',
  '/api/v1/dashboard/activity',
  '/api/v1/dashboard/apps'
];

// Install event - cache static resources
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('📦 Caching static resources...');
        return cache.addAll(STATIC_CACHE_URLS);
      })
      .then(() => {
        console.log('✅ Static resources cached');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('❌ Failed to cache static resources:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('🚀 Service Worker activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME) {
              console.log('🗑️ Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('✅ Service Worker activated');
        return self.clients.claim();
      })
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Skip WebSocket requests
  if (request.url.includes('/ws')) {
    return;
  }
  
  // Handle different types of requests
  if (url.pathname.startsWith('/api/')) {
    // API requests - Cache First with Network Fallback
    event.respondWith(handleApiRequest(request));
  } else if (STATIC_CACHE_URLS.some(cachedUrl => url.pathname === cachedUrl || request.url.includes(cachedUrl))) {
    // Static resources - Cache First
    event.respondWith(handleStaticRequest(request));
  } else if (url.pathname === '/dashboard' || url.pathname === '/') {
    // Dashboard - Network First with Cache Fallback
    event.respondWith(handleDashboardRequest(request));
  } else {
    // Other requests - Network First
    event.respondWith(handleNetworkFirst(request));
  }
});

// Handle API requests with cache-first strategy
async function handleApiRequest(request) {
  try {
    const cache = await caches.open(CACHE_NAME);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      // Return cached response and update cache in background
      updateCacheInBackground(request, cache);
      return cachedResponse;
    }
    
    // No cache, fetch from network
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Cache successful responses
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
    
  } catch (error) {
    console.error('❌ API request failed:', error);
    
    // Return cached version if available
    const cache = await caches.open(CACHE_NAME);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline fallback for dashboard data
    if (request.url.includes('/dashboard/')) {
      return new Response(JSON.stringify(getOfflineFallbackData(request.url)), {
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    throw error;
  }
}

// Handle static resource requests
async function handleStaticRequest(request) {
  try {
    const cache = await caches.open(CACHE_NAME);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Not in cache, fetch from network
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
    
  } catch (error) {
    console.error('❌ Static request failed:', error);
    
    // Return cached version if available
    const cache = await caches.open(CACHE_NAME);
    return await cache.match(request);
  }
}

// Handle dashboard requests
async function handleDashboardRequest(request) {
  try {
    // Try network first
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }
    
    throw new Error('Network response not ok');
    
  } catch (error) {
    console.log('📱 Network failed, serving cached dashboard...');
    
    // Fallback to cache
    const cache = await caches.open(CACHE_NAME);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Ultimate fallback - offline page
    return await cache.match(OFFLINE_URL);
  }
}

// Handle other requests with network-first strategy
async function handleNetworkFirst(request) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
    
  } catch (error) {
    // Fallback to cache
    const cache = await caches.open(CACHE_NAME);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    throw error;
  }
}

// Update cache in background
async function updateCacheInBackground(request, cache) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      await cache.put(request, networkResponse.clone());
      console.log('🔄 Cache updated in background:', request.url);
    }
  } catch (error) {
    console.warn('⚠️ Background cache update failed:', error);
  }
}

// Provide offline fallback data
function getOfflineFallbackData(url) {
  if (url.includes('/stats')) {
    return {
      active_patients: 0,
      procedures_today: 0,
      success_rate: 0,
      avg_duration: 0,
      offline: true
    };
  } else if (url.includes('/activity')) {
    return [
      {
        id: 1,
        icon: 'fas fa-wifi',
        description: 'You are currently offline',
        timestamp: 'Just now',
        app: 'system'
      }
    ];
  } else if (url.includes('/apps')) {
    return {
      surge: { name: 'Surge', status: 'offline' },
      clinica: { name: 'Clinica', status: 'offline' },
      educa: { name: 'Educa', status: 'offline' },
      insura: { name: 'Insura', status: 'offline' },
      move: { name: 'Move', status: 'offline' }
    };
  }
  
  return { offline: true, message: 'Data unavailable offline' };
}

// Handle background sync
self.addEventListener('sync', (event) => {
  console.log('🔄 Background sync triggered:', event.tag);
  
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

// Perform background sync
async function doBackgroundSync() {
  try {
    console.log('🔄 Performing background sync...');
    
    // Sync critical data
    const criticalUrls = [
      '/api/v1/dashboard/stats',
      '/api/v1/dashboard/activity'
    ];
    
    const cache = await caches.open(CACHE_NAME);
    
    for (const url of criticalUrls) {
      try {
        const response = await fetch(url);
        if (response.ok) {
          await cache.put(url, response.clone());
        }
      } catch (error) {
        console.warn(`⚠️ Failed to sync ${url}:`, error);
      }
    }
    
    console.log('✅ Background sync completed');
    
  } catch (error) {
    console.error('❌ Background sync failed:', error);
  }
}

// Handle push notifications
self.addEventListener('push', (event) => {
  if (!event.data) {
    return;
  }
  
  const data = event.data.json();
  const options = {
    body: data.body || 'YAZ Healthcare notification',
    icon: '/static/assets/icon-192.png',
    badge: '/static/assets/badge.png',
    vibrate: [200, 100, 200],
    data: data.data || {},
    actions: data.actions || [],
    requireInteraction: data.requireInteraction || false
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title || 'YAZ Healthcare', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  console.log('🔔 Notification clicked:', event.notification.tag);
  
  event.notification.close();
  
  const data = event.notification.data;
  let url = '/dashboard';
  
  if (data && data.url) {
    url = data.url;
  }
  
  event.waitUntil(
    clients.openWindow(url)
  );
});

// Handle messages from main thread
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

console.log('🔧 YAZ Healthcare Service Worker loaded');
