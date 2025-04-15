/**
 * WebPush Client SDK
 * Provides a simple API for subscribing to web push notifications
 */
class WebPushClient {
  /**
   * Initialize the WebPush client
   * @param {Object} options - Configuration options
   * @param {string} options.serviceWorkerPath - Path to the service worker file (default: '/service-worker.js')
   * @param {string} options.serviceWorkerScope - Scope for the service worker (default: '/')
   * @param {string} options.apiEndpoint - API endpoint for subscription management (default: '/api/webpush')
   * @param {string} options.vapidPublicKey - VAPID public key for push subscription
   * @param {Function} options.onSubscriptionSuccess - Callback for successful subscription
   * @param {Function} options.onSubscriptionError - Callback for subscription errors
   * @param {Function} options.onPermissionChange - Callback for permission changes
   */
  constructor(options = {}) {
    this.options = {
      serviceWorkerPath: '/service-worker.js',
      serviceWorkerScope: '/',
      apiEndpoint: '/api/webpush',
      ...options
    };

    this.initialized = false;
    this.subscription = null;
    this.permissionStatus = null;
    this.serviceWorkerRegistration = null;
  }

  /**
   * Initialize the WebPush client
   * @returns {Promise<boolean>} - Whether initialization was successful
   */
  async init() {
    try {
      // Check if service workers are supported
      if (!('serviceWorker' in navigator)) {
        console.error('Service workers are not supported by this browser');
        return false;
      }

      // Check if Push API is supported
      if (!('PushManager' in window)) {
        console.error('Push notifications are not supported by this browser');
        return false;
      }

      // Register the service worker
      this.serviceWorkerRegistration = await navigator.serviceWorker.register(
        this.options.serviceWorkerPath,
        { scope: this.options.serviceWorkerScope }
      );

      console.log('Service Worker registered:', this.serviceWorkerRegistration);

      // Get current permission status
      this.permissionStatus = this._getPermissionStatus();

      // Get existing subscription if any
      this.subscription = await this._getExistingSubscription();

      // Setup permission change listener
      if (navigator.permissions && navigator.permissions.query) {
        const permissionStatus = await navigator.permissions.query({ name: 'notifications' });
        permissionStatus.addEventListener('change', () => {
          const newStatus = this._getPermissionStatus();
          this.permissionStatus = newStatus;
          
          if (typeof this.options.onPermissionChange === 'function') {
            this.options.onPermissionChange(newStatus);
          }
          
          // If permission was revoked, update server
          if (newStatus === 'denied' && this.subscription) {
            this._updateSubscriptionPermission('denied');
          }
        });
      }

      this.initialized = true;
      return true;
    } catch (error) {
      console.error('Failed to initialize WebPush client:', error);
      return false;
    }
  }

  /**
   * Subscribe for push notifications
   * @param {Object} options - Subscription options
   * @param {boolean} options.userVisibleOnly - Whether notifications must be visible to the user
   * @param {Object} options.applicationServerKey - VAPID public key (or use the one provided in constructor)
   * @param {Object} options.context - Additional context information for the subscription
   * @returns {Promise<Object>} - The subscription object
   */
  async subscribe(options = {}) {
    if (!this.initialized) {
      await this.init();
    }

    try {
      // Request permission if not already granted
      if (this.permissionStatus !== 'granted') {
        const permission = await Notification.requestPermission();
        
        if (permission !== 'granted') {
          console.error('Permission not granted for notifications');
          
          // Track permission denied event
          this._trackEvent('permission_denied', { permissionStatus: permission });
          
          if (typeof this.options.onSubscriptionError === 'function') {
            this.options.onSubscriptionError({ error: 'permission_denied' });
          }
          
          return null;
        }
        
        // Track permission granted event
        this._trackEvent('permission_granted');
        
        // Update permission status
        this.permissionStatus = 'granted';
      }

      // Get subscription options
      const subscriptionOptions = {
        userVisibleOnly: true,
        applicationServerKey: this._urlBase64ToUint8Array(
          options.applicationServerKey || this.options.vapidPublicKey
        )
      };

      // Subscribe to push
      const pushSubscription = await this.serviceWorkerRegistration.pushManager.subscribe(subscriptionOptions);
      console.log('Push subscription:', pushSubscription);

      // Save the subscription
      this.subscription = pushSubscription;

      // Send subscription to server
      const response = await this._saveSubscription(pushSubscription, options.context);
      
      if (response && response.success) {
        if (typeof this.options.onSubscriptionSuccess === 'function') {
          this.options.onSubscriptionSuccess(response.subscription);
        }
      }

      return pushSubscription;
    } catch (error) {
      console.error('Failed to subscribe for push notifications:', error);
      
      if (typeof this.options.onSubscriptionError === 'function') {
        this.options.onSubscriptionError({ error: error.message });
      }
      
      return null;
    }
  }

  /**
   * Unsubscribe from push notifications
   * @returns {Promise<boolean>} - Whether unsubscription was successful
   */
  async unsubscribe() {
    if (!this.initialized) {
      await this.init();
    }

    try {
      const subscription = this.subscription || await this._getExistingSubscription();
      
      if (!subscription) {
        console.warn('No subscription to unsubscribe from');
        return true;
      }

      // Unsubscribe from push manager
      const success = await subscription.unsubscribe();
      
      if (success) {
        // Notify server
        await this._deleteSubscription(subscription);
        this.subscription = null;
        
        // Track unsubscribe event
        this._trackEvent('unsubscribed');
        
        return true;
      } else {
        console.error('Failed to unsubscribe');
        return false;
      }
    } catch (error) {
      console.error('Error unsubscribing:', error);
      return false;
    }
  }

  /**
   * Check if the user is subscribed
   * @returns {Promise<boolean>} - Whether the user is subscribed
   */
  async isSubscribed() {
    if (!this.initialized) {
      await this.init();
    }

    if (this.subscription) {
      return true;
    }

    const subscription = await this._getExistingSubscription();
    this.subscription = subscription;
    
    return !!subscription;
  }

  /**
   * Get the current permission status
   * @returns {string} - The permission status: 'granted', 'denied', or 'default'
   */
  getPermissionStatus() {
    return this._getPermissionStatus();
  }

  /**
   * Update subscription preferences
   * @param {Object} preferences - User preferences for notifications
   * @returns {Promise<boolean>} - Whether the update was successful
   */
  async updatePreferences(preferences = {}) {
    if (!this.initialized) {
      await this.init();
    }

    if (!this.subscription) {
      console.warn('No active subscription to update preferences for');
      return false;
    }

    try {
      const response = await fetch(`${this.options.apiEndpoint}/subscription/preferences`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          subscription: this._serializeSubscription(this.subscription),
          preferences
        })
      });

      if (!response.ok) {
        throw new Error('Failed to update preferences');
      }

      return true;
    } catch (error) {
      console.error('Error updating preferences:', error);
      return false;
    }
  }

  // Private methods

  /**
   * Get the current permission status
   * @private
   * @returns {string} - The permission status
   */
  _getPermissionStatus() {
    return Notification.permission;
  }

  /**
   * Get existing push subscription if any
   * @private
   * @returns {Promise<PushSubscription|null>} - The existing push subscription
   */
  async _getExistingSubscription() {
    try {
      if (!this.serviceWorkerRegistration) {
        return null;
      }
      
      return await this.serviceWorkerRegistration.pushManager.getSubscription();
    } catch (error) {
      console.error('Error getting existing subscription:', error);
      return null;
    }
  }

  /**
   * Save subscription to server
   * @private
   * @param {PushSubscription} subscription - The push subscription
   * @param {Object} context - Additional context information
   * @returns {Promise<Object>} - Server response
   */
  async _saveSubscription(subscription, context = {}) {
    try {
      // Get device and browser information
      const deviceInfo = this._getDeviceInfo();

      const response = await fetch(`${this.options.apiEndpoint}/subscription`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...this._serializeSubscription(subscription),
          userAgent: navigator.userAgent,
          referrer: document.referrer,
          screenResolution: `${window.screen.width}x${window.screen.height}`,
          context,
          ...deviceInfo
        })
      });

      if (!response.ok) {
        throw new Error('Failed to save subscription');
      }

      return await response.json();
    } catch (error) {
      console.error('Error saving subscription:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Delete subscription from server
   * @private
   * @param {PushSubscription} subscription - The push subscription
   * @returns {Promise<boolean>} - Whether deletion was successful
   */
  async _deleteSubscription(subscription) {
    try {
      const response = await fetch(`${this.options.apiEndpoint}/subscription`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(this._serializeSubscription(subscription))
      });

      return response.ok;
    } catch (error) {
      console.error('Error deleting subscription:', error);
      return false;
    }
  }

  /**
   * Update subscription permission status on server
   * @private
   * @param {string} permissionStatus - The new permission status
   * @returns {Promise<boolean>} - Whether the update was successful
   */
  async _updateSubscriptionPermission(permissionStatus) {
    if (!this.subscription) {
      return false;
    }

    try {
      const response = await fetch(`${this.options.apiEndpoint}/subscription/permission`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          subscription: this._serializeSubscription(this.subscription),
          permission: permissionStatus
        })
      });

      return response.ok;
    } catch (error) {
      console.error('Error updating permission status:', error);
      return false;
    }
  }

  /**
   * Track events on the server
   * @private
   * @param {string} eventType - The type of event
   * @param {Object} data - Additional event data
   * @returns {Promise<boolean>} - Whether tracking was successful
   */
  async _trackEvent(eventType, data = {}) {
    try {
      const deviceInfo = this._getDeviceInfo();
      
      const response = await fetch(`${this.options.apiEndpoint}/events`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          eventType,
          subscription: this.subscription ? this._serializeSubscription(this.subscription) : null,
          userAgent: navigator.userAgent,
          referrer: document.referrer,
          url: window.location.href,
          timestamp: new Date().toISOString(),
          ...deviceInfo,
          ...data
        })
      });

      return response.ok;
    } catch (error) {
      console.error('Error tracking event:', error);
      return false;
    }
  }

  /**
   * Serialize PushSubscription object
   * @private
   * @param {PushSubscription} subscription - The push subscription
   * @returns {Object} - Serialized subscription
   */
  _serializeSubscription(subscription) {
    if (!subscription) return null;

    const subscriptionJSON = subscription.toJSON();
    
    return {
      endpoint: subscription.endpoint,
      keys: subscriptionJSON.keys
    };
  }

  /**
   * Get device and browser information
   * @private
   * @returns {Object} - Device and browser information
   */
  _getDeviceInfo() {
    const info = {
      userAgent: navigator.userAgent,
      language: navigator.language,
      platform: navigator.platform,
      deviceMemory: navigator.deviceMemory,
      hardwareConcurrency: navigator.hardwareConcurrency,
      screenWidth: window.screen.width,
      screenHeight: window.screen.height,
      pixelRatio: window.devicePixelRatio
    };

    // Detect mobile device
    info.isMobile = /Mobi|Android/i.test(navigator.userAgent);

    return info;
  }

  /**
   * Convert URL Base64 to Uint8Array
   * @private
   * @param {string} base64String - Base64 string
   * @returns {Uint8Array} - Uint8Array
   */
  _urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    
    return outputArray;
  }
}

// Export as global or module
if (typeof module !== 'undefined' && module.exports) {
  module.exports = WebPushClient;
} else {
  window.WebPushClient = WebPushClient;
}