// Web Push Service Worker
// This service worker handles web push notifications

const VERSION = '1.0.0';

// Cache name for the service worker cache
const CACHE_NAME = 'webpush-cache-v1';

// Files to precache
const filesToCache = [
  '/static/images/icon.png',
  '/static/images/badge.png'
];

// Install event
self.addEventListener('install', event => {
  console.log('[ServiceWorker] Install version:', VERSION);
  
  // Precache static resources
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[ServiceWorker] Caching files');
        return cache.addAll(filesToCache);
      })
      .then(() => {
        console.log('[ServiceWorker] Skip waiting on install');
        return self.skipWaiting();
      })
  );
});

// Activate event
self.addEventListener('activate', event => {
  console.log('[ServiceWorker] Activate');
  
  // Delete old caches
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(oldCache => {
          if (oldCache !== CACHE_NAME) {
            console.log('[ServiceWorker] Removing old cache', oldCache);
            return caches.delete(oldCache);
          }
        })
      );
    }).then(() => {
      console.log('[ServiceWorker] Claiming clients');
      return self.clients.claim();
    })
  );
});

// Fetch event - for network requests
self.addEventListener('fetch', event => {
  // Only handle GET requests
  if (event.request.method !== 'GET') return;
  
  // Skip non-HTTP(S) requests
  if (!event.request.url.startsWith('http')) return;
  
  // Respond with cache then network strategy
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // If cached, return the cached version
        if (response) {
          console.log('[ServiceWorker] Serving cached:', event.request.url);
          return response;
        }
        
        // Otherwise, fetch from network
        console.log('[ServiceWorker] Fetching:', event.request.url);
        return fetch(event.request)
          .then(response => {
            // Don't cache if not a valid response
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }
            
            // Clone the response since it can only be consumed once
            const responseToCache = response.clone();
            
            // Cache the fetched response
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });
            
            return response;
          });
      })
      .catch(error => {
        console.error('[ServiceWorker] Fetch failed:', error);
      })
  );
});

// Push event - Handle incoming push messages
self.addEventListener('push', event => {
  console.log('[ServiceWorker] Push received:', event);
  
  let notificationData = {};
  
  // Parse the push data
  if (event.data) {
    try {
      notificationData = event.data.json();
      console.log('[ServiceWorker] Push data:', notificationData);
    } catch (e) {
      console.error('[ServiceWorker] Error parsing push data:', e);
      notificationData = {
        notification: {
          title: 'New Notification',
          body: event.data ? event.data.text() : 'No details available'
        }
      };
    }
  } else {
    notificationData = {
      notification: {
        title: 'New Notification',
        body: 'No details available'
      }
    };
  }
  
  // Default notification options
  const defaultOptions = {
    icon: '/static/images/icon.png',
    badge: '/static/images/badge.png',
    vibrate: [100, 50, 100],
    data: {
      timestamp: new Date().getTime()
    },
    requireInteraction: false
  };
  
  // Get notification content and options
  const title = notificationData.notification?.title || 'New Notification';
  const options = {
    ...defaultOptions,
    ...notificationData.notification,
    data: {
      ...defaultOptions.data,
      ...notificationData.data
    }
  };
  
  // Track when the notification was received
  trackPushEvent('received', options.data);
  
  // Show the notification
  event.waitUntil(
    self.registration.showNotification(title, options)
      .then(() => {
        // Track when notification was shown
        return trackPushEvent('shown', options.data);
      })
  );
});

// Notification click event
self.addEventListener('notificationclick', event => {
  console.log('[ServiceWorker] Notification click:', event);
  
  // Close the notification
  event.notification.close();
  
  // Get notification data
  const data = event.notification.data || {};
  
  // Handle notification click
  let action = 'clicked';
  let actionId = null;
  
  // Check if a specific action was clicked
  if (event.action) {
    action = 'action_button';
    actionId = event.action;
  }
  
  // Track the click event
  trackPushEvent(action, { ...data, actionId });
  
  // Open a window if URL is provided
  if (data.url) {
    event.waitUntil(
      clients.matchAll({ type: 'window' })
        .then(windowClients => {
          // Check if there is already a window/tab open with the target URL
          for (let i = 0; i < windowClients.length; i++) {
            const client = windowClients[i];
            // If so, focus it
            if (client.url === data.url && 'focus' in client) {
              return client.focus();
            }
          }
          // If not, open a new window
          if (clients.openWindow) {
            return clients.openWindow(data.url);
          }
        })
        .catch(err => console.error('[ServiceWorker] Error opening window:', err))
    );
  }
});

// Notification close event
self.addEventListener('notificationclose', event => {
  console.log('[ServiceWorker] Notification close:', event);
  
  // Get notification data
  const data = event.notification.data || {};
  
  // Track the close event
  trackPushEvent('closed', data);
});

// Helper function to track push events
function trackPushEvent(eventType, data = {}) {
  // Add event type to data
  data.eventType = eventType;
  data.timestamp = data.timestamp || new Date().getTime();
  
  // Calculate time since original event if applicable
  if (data.timestamp && eventType !== 'received') {
    data.timeSinceDelivery = (new Date().getTime() - data.timestamp) / 1000;
  }
  
  // Add browser information
  data.userAgent = self.navigator.userAgent;
  
  // Track the event by sending to our backend API
  return fetch('/api/webpush/events', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      eventType: eventType,
      notificationId: data.notificationId,
      subscriptionId: data.subscriptionId,
      userId: data.userId,
      campaignId: data.campaignId,
      actionId: data.actionId,
      timeSinceDelivery: data.timeSinceDelivery,
      userAgent: data.userAgent,
      timestamp: data.timestamp,
      url: data.url,
      customData: data.customData || {}
    })
  }).catch(err => {
    console.error('[ServiceWorker] Error tracking event:', err);
  });
}