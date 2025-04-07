# Subscription Management Wireframes

## 1. Subscription Listing Page

```
+----------------------------------------------------------------------+
|                      WEBPUSH API MANAGEMENT                          |
+-------------------------------+------------------------------------+
| [Dashboard]                   |  Subscriptions                     |
| [Subscriptions] ►             |                                    |
| [Segments]                    |  + Create New Subscription         |
| [Content]                     |                                    |
| [Campaigns]                   |  [Filters] [Search.......] [Apply] |
| [Automation]                  |                                    |
| [Analytics]                   |  Total: 1,245 subscriptions        |
| [Integrations]                |                                    |
| [Settings]                    |  +------+-------------------+------+
|                               |  | ID   | Email             | Status|
+-------------------------------+  +------+-------------------+------+
                                   | #1234| user@example.com  | Active|
                                   | #2345| test@example.com  | Active|
                                   | #3456| john@example.com  | Inactv|
                                   | ...  | ...               | ...   |
                                   +------+-------------------+------+
                                   
                                   [< 1 2 3 ... 50 >]
```

## 2. Subscription Details Page

```
+----------------------------------------------------------------------+
|                      WEBPUSH API MANAGEMENT                          |
+-------------------------------+------------------------------------+
| [Dashboard]                   |  Subscription Details              |
| [Subscriptions] ►             |                                    |
| [Segments]                    |  ID: #1234                         |
| [Content]                     |                                    |
| [Campaigns]                   |  [Edit] [Delete]                   |
| [Automation]                  |                                    |
| [Analytics]                   |  +-------------------------+       |
| [Integrations]                |  | Basic Information       |       |
| [Settings]                    |  +-------------------------+       |
|                               |  | Email: user@example.com |       |
+-------------------------------+  | Username: testuser      |       |
                                   | Status: Active          |       |
                                   | Created: 2023-05-15     |       |
                                   | Last Updated: 2023-06-10|       |
                                   +-------------------------+       |
                                   
                                   +-------------------------+
                                   | Device Information      |
                                   +-------------------------+
                                   | User Agent: Chrome 98.0 |
                                   | Device Type: Desktop    |
                                   | Last Seen: 2023-06-08   |
                                   +-------------------------+
                                   
                                   +-------------------------+
                                   | Subscription Details    |
                                   +-------------------------+
                                   | Endpoint: https://...   |
                                   | Keys: p256dh, auth      |
                                   | Enabled: Yes            |
                                   +-------------------------+
```

## 3. Create Subscription Form

```
+----------------------------------------------------------------------+
|                      WEBPUSH API MANAGEMENT                          |
+-------------------------------+------------------------------------+
| [Dashboard]                   |  Create New Subscription           |
| [Subscriptions] ►             |                                    |
| [Segments]                    |  +-------------------------+       |
| [Content]                     |  | User Information        |       |
| [Campaigns]                   |  +-------------------------+       |
| [Automation]                  |  | User ID:                |       |
| [Analytics]                   |  | [dropdown or search]    |       |
| [Integrations]                |  +-------------------------+       |
| [Settings]                    |                                    |
|                               |  +-------------------------+       |
+-------------------------------+  | Subscription Data       |       |
                                   +-------------------------+       |
                                   | Endpoint:               |       |
                                   | [text field]            |       |
                                   |                         |       |
                                   | Key (p256dh):           |       |
                                   | [text field]            |       |
                                   |                         |       |
                                   | Key (auth):             |       |
                                   | [text field]            |       |
                                   |                         |       |
                                   | Device Type:            |       |
                                   | [dropdown]              |       |
                                   |                         |       |
                                   | User Agent:             |       |
                                   | [text field]            |       |
                                   +-------------------------+       |
                                   
                                   [Cancel]    [Create Subscription]  
```

## 4. Edit Subscription Form

```
+----------------------------------------------------------------------+
|                      WEBPUSH API MANAGEMENT                          |
+-------------------------------+------------------------------------+
| [Dashboard]                   |  Edit Subscription                 |
| [Subscriptions] ►             |                                    |
| [Segments]                    |  ID: #1234                         |
| [Content]                     |  User: user@example.com            |
| [Campaigns]                   |                                    |
| [Automation]                  |  +-------------------------+       |
| [Analytics]                   |  | Subscription Status     |       |
| [Integrations]                |  +-------------------------+       |
| [Settings]                    |  | [ ] Enabled             |       |
|                               |  | Status: [dropdown]      |       |
+-------------------------------+  +-------------------------+       |
                                   
                                   +-------------------------+
                                   | Subscription Data       |
                                   +-------------------------+
                                   | Endpoint:               |
                                   | [text field - prefilled]|
                                   |                         |
                                   | Key (p256dh):           |
                                   | [text field - prefilled]|
                                   |                         |
                                   | Key (auth):             |
                                   | [text field - prefilled]|
                                   |                         |
                                   | Device Type:            |
                                   | [dropdown - selected]   |
                                   +-------------------------+
                                   
                                   [Cancel]    [Save Changes]
```

## 5. Delete Subscription Confirmation

```
+----------------------------------------------------------------------+
|                      WEBPUSH API MANAGEMENT                          |
+-------------------------------+------------------------------------+
| [Dashboard]                   |  Delete Subscription               |
| [Subscriptions] ►             |                                    |
| [Segments]                    |  +-------------------------+       |
| [Content]                     |  |                         |       |
| [Campaigns]                   |  |  Are you sure you want  |       |
| [Automation]                  |  |  to delete this         |       |
| [Analytics]                   |  |  subscription?          |       |
| [Integrations]                |  |                         |       |
| [Settings]                    |  |  This action cannot be  |       |
|                               |  |  undone.                |       |
+-------------------------------+  |                         |       |
                                   |  Subscription ID: #1234 |       |
                                   |  User: user@example.com |       |
                                   |                         |       |
                                   +-------------------------+       |
                                   
                                   [Cancel]    [Delete Subscription]
```

## API Endpoints Usage

### 1. Create a New Subscription
- **Endpoint**: `POST /api/v1/subscriptions`
- **Permission**: `subscriptions:write`
- **Request Body**:
  ```json
  {
    "subscription_info": {
      "endpoint": "https://fcm.googleapis.com/fcm/send/...",
      "keys": {
        "p256dh": "BNJUg_UO_...",
        "auth": "xp0m9PDj..."
      }
    },
    "user_agent": "Mozilla/5.0...",
    "device_type": "desktop"
  }
  ```
- **Query Parameter**: `user_id=123e4567-e89b-12d3-a456-426614174000`

### 2. List Subscriptions
- **Endpoint**: `GET /api/v1/subscriptions`
- **Permission**: `subscriptions:read`
- **Query Parameters**:
  - `skip=0`
  - `limit=100`
  - `active_only=true`

### 3. Get Subscription Details
- **Endpoint**: `GET /api/v1/subscriptions/{id}`
- **Permission**: `subscriptions:read`
- **Path Parameter**: Subscription ID (User ID)

### 4. Update Subscription
- **Endpoint**: `PUT /api/v1/subscriptions/{id}`
- **Permission**: `subscriptions:write`
- **Path Parameter**: Subscription ID (User ID)
- **Request Body**:
  ```json
  {
    "subscription_info": {
      "endpoint": "https://fcm.googleapis.com/fcm/send/...",
      "keys": {
        "p256dh": "BNJUg_UO_...",
        "auth": "xp0m9PDj..."
      }
    },
    "webpush_enabled": true,
    "status": "active"
  }
  ```

### 5. Delete Subscription
- **Endpoint**: `DELETE /api/v1/subscriptions/{id}`
- **Permission**: `subscriptions:write`
- **Path Parameter**: Subscription ID (User ID)

## Note
Use this wireframe format as a template for other management entities.

## Visual Form Formats

### Create Subscription Form
+------------------------------------------------+
|           Create New Subscription              |
+------------------------------------------------+
| User ID:          [ dropdown/search field ]    |
| Endpoint:         [_________________________]    |
| Key (p256dh):     [_________________________]    |
| Key (auth):       [_________________________]    |
| Device Type:      [ dropdown ]                   |
| User Agent:       [_________________________]    |
|                                                |
|       [Cancel]           [Create Subscription]   |
+------------------------------------------------+

### Edit Subscription Form
+------------------------------------------------+
|             Edit Subscription                  |
+------------------------------------------------+
| Subscription ID:   [ prefilled text ]          |
| Endpoint:          [ prefilled text ]          |
| Key (p256dh):      [ prefilled text ]          |
| Key (auth):        [ prefilled text ]          |
| Device Type:       [ selected dropdown ]       |
| Status:            [ dropdown ]                |
|                                                |
|       [Cancel]           [Save Changes]         |
+------------------------------------------------+

### Delete Subscription Confirmation
+------------------------------------------------+
|         Delete Subscription Confirmation       |
+------------------------------------------------+
| Are you sure you want to delete subscription?  |
| Subscription ID: #XXXX                           |
| This action cannot be undone.                  |
|                                                |
|       [Cancel]           [Delete Subscription]   |
+------------------------------------------------+
