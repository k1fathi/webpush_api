+----------------------------------------------------------------------+
|                      WEBPUSH API MANAGEMENT                          |
+-------------------------------+------------------------------------+
| NAVIGATION                    |  SEGMENTS                          |
+-------------------------------+------------------------------------+

===================== SEGMENT LISTING PAGE =====================
| [Notifications]                   |  Segments                         |
| [Subscriptions]               |                                   |
| [Segments] ►                  |  + Create Segment                 |
| [Templates]                     |                                   |
| [Campaigns]                   |  [Type: All ▼] [Search...] [🔍]   |
| [Triggers]                    |                                   |
| [Analytics]                   |  Showing 15 segments              |
| [Integrations]                |                                   |
| [Settings]                    |  +----+----------------+------+---+
|                               |  | ID | Name           | Type | 🛠 |
|                               |  +----+----------------+------+---+
|                               |  | 1  | Active Users  | Dynamic|⋮|
|                               |  | 2  | Premium       | Static |⋮|
|                               |  | 3  | Inactive      | Dynamic|⋮|
|                               |  +----+----------------+------+---+
|                               |                                   |
|                               |  [← Previous] [1] [Next →]        |
+-------------------------------+------------------------------------+

===================== CREATE SEGMENT FORM =====================
|                               |  Create Segment                   |
|                               |                                   |
|                               |  Segment Name:                    |
|                               |  [______________________________] |
|                               |                                   |
|                               |  Description:                     |
|                               |  [______________________________] |
|                               |                                   |
|                               |  Segment Type:                    |
|                               |  [Dynamic ▼]                      |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Filter Criteria Builder     |  |
|                               |  | [Attribute ▼] [Operator ▼]  |  |
|                               |  | [Value input] [+ Add Rule]  |  |
|                               |  |                             |  |
|                               |  | last_login > 7 days ago     |  |
|                               |  | is_active = true            |  |
|                               |  +-----------------------------+  |
|                               |                                   |
|                               |  [Preview Segment] (1,245 users)  |
|                               |                                   |
|                               |  [Cancel]    [Create Segment]     |
+-------------------------------+------------------------------------+

===================== SEGMENT DETAILS PAGE =====================
|                               |  Active Users (#42)              |
|                               |                                   |
|                               |  [✏ Edit] [🗑 Delete] [📊 Stats]  |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Overview                   |  |
|                               |  | Type: Dynamic              |  |
|                               |  | Created: Jun 1, 2023       |  |
|                               |  | Last Updated: Jun 15, 2023 |  |
|                               |  | Members: 1,245             |  |
|                               |  +-----------------------------+  |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Filter Criteria            |  |
|                               |  | last_login > 7 days ago     |  |
|                               |  | is_active = true            |  |
|                               |  +-----------------------------+  |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Usage                      |  |
|                               |  | Used in 5 campaigns        |  |
|                               |  | Last used: Jun 10, 2023    |  |
|                               |  +-----------------------------+  |
+-------------------------------+------------------------------------+

===================== EDIT SEGMENT FORM =====================
|                               |  Edit Active Users (#42)          |
|                               |                                   |
|                               |  Segment Name:                    |
|                               |  [Active Users________________]  |
|                               |                                   |
|                               |  Description:                     |
|                               |  [Users who logged in..._______]  |
|                               |                                   |
|                               |  Segment Type:                    |
|                               |  [Dynamic (disabled)]             |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Filter Criteria Builder     |  |
|                               |  | last_login > [7 ▼] days ago |  |
|                               |  | is_active = [true ▼]        |  |
|                               |  | [+ Add New Condition]       |  |
|                               |  +-----------------------------+  |
|                               |                                   |
|                               |  [Preview Segment] (1,245 users)  |
|                               |                                   |
|                               |  [Cancel]    [Save Changes]       |
+-------------------------------+------------------------------------+

===================== DELETE CONFIRMATION =====================
|                               |  Delete Segment?                  |
|                               |                                   |
|                               |  Are you sure you want to delete: |
|                               |  "Active Users" segment?          |
|                               |                                   |
|                               |  ❗ This will affect:              |
|                               |  • 5 active campaigns             |
|                               |  • 1,245 user assignments         |
|                               |                                   |
|                               |  [Cancel]    [Delete Segment]     |
+-------------------------------+------------------------------------+