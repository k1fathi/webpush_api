+----------------------------------------------------------------------+
|                      WEBPUSH API MANAGEMENT                          |
+-------------------------------+------------------------------------+
| NAVIGATION                    |  SUBSCRIPTIONS                     |
+-------------------------------+------------------------------------+

===================== SUBSCRIPTION LISTING PAGE =====================
| [Notifications]                   |  Subscriptions                     |
| [Subscriptions] ►             |                                    |
| [Segments]                    |  + Add Subscription                |
| [Templates]                     |                                    |
| [Campaigns]                   |  [Status: All ▼] [Search...] [🔍]  |
| [Triggers]                  |                                    |
| [Analytics]                   |  Showing 1,245 subscriptions       |
| [Integrations]                |                                    |
| [Settings]                    |  +------+-------------------+------+
|                               |  | ID   | Endpoint          |Status|
|                               |  +------+-------------------+------+
|                               |  | #1234| https://.../abc123|✅ Active|
|                               |  | #2345| https://.../def456|✅ Active|
|                               |  | #3456| https://.../ghi789|❌ Inactive|
|                               |  +------+-------------------+------+
|                               |                                    |
|                               |  [← Previous] [1] [2] [3] [Next →] |
+-------------------------------+------------------------------------+

===================== ADD SUBSCRIPTION FORM =====================
|                               |  Add Subscription                  |
|                               |                                    |
|                               |  User Identifier:                  |
|                               |  [user_12345] (from dropdown)      |
|                               |                                    |
|                               |  +-----------------------------+   |
|                               |  | Push Subscription Details   |   |
|                               |  | Endpoint: [https://...]     |   |
|                               |  | Keys: [p256dh:...]          |   |
|                               |  |        [auth:...]           |   |
|                               |  +-----------------------------+   |
|                               |                                    |
|                               |  +-----------------------------+   |
|                               |  | Device Information          |   |
|                               |  | Browser: [Chrome ▼]         |   |
|                               |  | OS: [Android ▼]             |   |
|                               |  +-----------------------------+   |
|                               |                                    |
|                               |  [Cancel]    [Save Subscription]   |
+-------------------------------+------------------------------------+

===================== SUBSCRIPTION DETAILS PAGE =====================
|                               |  Subscription #1234                |
|                               |                                    |
|                               |  [✏ Edit] [🗑 Delete] [↻ Refresh]   |
|                               |                                    |
|                               |  +-----------------------------+   |
|                               |  | Basic Information          |   |
|                               |  | Status: ✅ Active          |   |
|                               |  | Created: Jun 1, 2023       |   |
|                               |  | Last Active: Jun 15, 2023  |   |
|                               |  +-----------------------------+   |
|                               |                                    |
|                               |  +-----------------------------+   |
|                               |  | Subscription Data          |   |
|                               |  | Endpoint: https://.../abc123|
|                               |  | p256dh: (shown when expanded)|
|                               |  | auth: (shown when expanded)  |
|                               |  +-----------------------------+   |
|                               |                                    |
|                               |  +-----------------------------+   |
|                               |  | Device Information          |   |
|                               |  | Browser: Chrome 114         |   |
|                               |  | OS: Android 13              |   |
|                               |  | IP: 192.168.1.1            |   |
|                               |  +-----------------------------+   |
+-------------------------------+------------------------------------+

===================== EDIT SUBSCRIPTION FORM =====================
|                               |  Edit Subscription #1234           |
|                               |                                    |
|                               |  Status:                          |
|                               |  [✅ Active ▼]                     |
|                               |                                    |
|                               |  +-----------------------------+   |
|                               |  | Subscription Data          |   |
|                               |  | Endpoint: [https://.../abc123]|
|                               |  | Keys: [p256dh:...]          |   |
|                               |  |        [auth:...]           |   |
|                               |  +-----------------------------+   |
|                               |                                    |
|                               |  [Test Subscription]              |
|                               |                                    |
|                               |  [Cancel]    [Save Changes]       |
+-------------------------------+------------------------------------+

===================== DELETE CONFIRMATION =====================
|                               |  Remove Subscription?              |
|                               |                                    |
|                               |  Are you sure you want to remove:  |
|                               |  Subscription #1234?               |
|                               |                                    |
|                               |  ❗ This will:                      |
|                               |  • Stop all push notifications     |
|                               |  • Delete subscription data        |
|                               |                                    |
|                               |  [Cancel]    [Remove Subscription] |
+-------------------------------+------------------------------------+