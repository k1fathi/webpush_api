# Segment Management Wireframes

## 1. Segment Listing Page

```
| [Content]                     |  |                         |       |
| [Campaigns]                   |  |  Are you sure you want  |       |
| [Automation]                  |  |  to delete this         |       |
| [Analytics]                   |  |  segment?               |       |
| [Integrations]                |  |                         |       |
| [Settings]                    |  |  This action cannot be  |       |
|                               |  |  undone.                |       |
+-------------------------------+  |                         |       |
                                   |  Segment ID: #1234       |       |
                                   |  Name: Active Users      |       |
                                   |                         |       |
                                   +-------------------------+       |
                                   
                                   [Cancel]    [Delete Segment]
```

## 2. Create/Edit Segment Form
// ...wireframe for creating or editing segments...

## API Endpoints Usage

### 1. Create a New Segment
- **Endpoint**: `POST /api/v1/segments`
- **Permission**: `segments:write`
- **Request Body**:
  ```json
  {
    "name": "Active Users",
    "description": "Users who have logged in within the last 7 days",
    "segment_type": "dynamic",
    "filter_criteria": {
      "last_login": {
        "type": "date",
        "operator": "gt",
        "value": "7d"
      },
      "is_active": true
    }
  }
  ```

### 2. List Segments
- **Endpoint**: `GET /api/v1/segments`
- **Permission**: `segments:read`
- **Query Parameters**:
  - `skip=0`
  - `limit=100`
  - `active_only=true`

### 3. Get Segment Details
- **Endpoint**: `GET /api/v1/segments/{id}`
- **Permission**: `segments:read`
- **Path Parameter**: Segment ID

### 4. Update Segment
- **Endpoint**: `PUT /api/v1/segments/{id}`
- **Permission**: `segments:write`
- **Path Parameter**: Segment ID
- **Request Body**:
  ```json
  {
    "name": "Very Active Users",
    "description": "Users who have logged in within the last 3 days",
    "filter_criteria": {
      "last_login": {
        "type": "date",
        "operator": "gt",
        "value": "3d"
      },
      "is_active": true
    }
  }
  ```

### 5. Delete Segment
- **Endpoint**: `DELETE /api/v1/segments/{id}`
- **Permission**: `segments:write`
- **Path Parameter**: Segment ID

## Visual Form Formats

### Create Segment Form
+----------------------------------------------+
|           Create New Segment                 |
+----------------------------------------------+
| Segment Name:    [_______________________]     |
| Description:     [_______________________]     |
| Segment Type:    [ dropdown ]                 |
| Filter Criteria: [_______________________]     |
|                                              |
|       [Cancel]           [Create Segment]      |
+----------------------------------------------+

### Edit Segment Form
+----------------------------------------------+
|              Edit Segment                    |
+----------------------------------------------+
| Segment Name:    [ prefilled text ]           |
| Description:     [ prefilled text ]           |
| Filter Criteria: [ prefilled text ]           |
|                                              |
|       [Cancel]           [Save Changes]        |
+----------------------------------------------+

### Delete Segment Confirmation
+----------------------------------------------+
|         Delete Segment Confirmation          |
+----------------------------------------------+
| Are you sure you want to delete this segment?|
| This action cannot be undone.                |
|                                              |
|       [Cancel]           [Delete Segment]      |
+----------------------------------------------+

