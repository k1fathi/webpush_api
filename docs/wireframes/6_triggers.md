+----------------------------------------------------------------------+
|                      WEBPUSH API MANAGEMENT                          |
+-------------------------------+------------------------------------+
| NAVIGATION                    |  CONTENT (TRIGGERS)                |
+-------------------------------+------------------------------------+
===================== TRIGGER LISTING PAGE =====================
| [Notifications]                   |  Triggers                        |
| [Subscriptions]               |                                   |
| [Segments]                    |  + Create Trigger                  |
| [Templates]                   |                                   |
| [Campaigns]                   |  [Status: All ▼] [Search...] [🔍]  |
| [Triggers] ►               |                                   |
| [Analytics]                   |  Showing 15 triggers               |
| [Integrations]                |                                   |
| [Settings]                    |  +----+----------------+------+---+
|                               |  | ID | Name           |Status| 🛠 |
|                               |  +----+----------------+------+---+
|                               |  | 1  | User Signup    |✅ Active|⋮|
|                               |  | 2  | Cart Abandon   |🔄 Draft |⋮|
|                               |  | 3  | Purchase       |✅ Active|⋮|
|                               |  +----+----------------+------+---+
|                               |                                   |
|                               |  [← Previous] [1] [Next →]        |
+-------------------------------+------------------------------------+
===================== CREATE TRIGGER FORM =====================
|                               |  Create New Trigger               |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Trigger Information         |  |
|                               |  | Name: [________________]    |  |
|                               |  | Description: [____________] |  |
|                               |  +-----------------------------+  |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Event Configuration         |  |
|                               |  | Type: [Select Event ▼]      |  |
|                               |  | - User Signup               |  |
|                               |  | - Purchase                  |  |
|                               |  | - Cart Abandonment         |  |
|                               |  +-----------------------------+  |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Conditions                 |  |
|                               |  | If: [User Age] [>=] [18]   |  |
|                               |  | And: [Purchase Value] [>] [50]|
|                               |  | +➕ Add Condition            |  |
|                               |  +-----------------------------+  |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Action                     |  |
|                               |  | Send: [Select Template ▼]  |  |
|                               |  | To: [Select Segment ▼]     |  |
|                               |  | Delay: [30] [Minutes ▼]    |  |
|                               |  +-----------------------------+  |
|                               |                                   |
|                               |  [Cancel]    [Create Trigger]     |
+-------------------------------+------------------------------------+
===================== TRIGGER DETAILS PAGE =====================
|                               |  User Signup Trigger (#12)        |
|                               |                                   |
|                               |  [✏ Edit] [🗑 Delete] [↻ Clone]   |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Overview                   |  |
|                               |  | Status: ✅ Active          |  |
|                               |  | Created: May 1, 2023       |  |
|                               |  | Last Triggered: Jun 10, 2023|  |
|                               |  +-----------------------------+  |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Trigger Details            |  |
|                               |  | Event: User Signup         |  |
|                               |  | Conditions:                |  |
|                               |  | - User Age >= 18           |  |
|                               |  | - Purchase Value > $50     |  |
|                               |  +-----------------------------+  |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Performance               |  |
|                               |  | Triggered: 342 times       |  |
|                               |  | Conversion Rate: 15%       |  |
|                               |  +-----------------------------+  |
+-------------------------------+------------------------------------+
===================== EDIT TRIGGER FORM =====================
|                               |  Edit User Signup Trigger (#12)   |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Trigger Information         |  |
|                               |  | Name: [User Signup Trigger]|  |
|                               |  | Description: [New user...]  |  |
|                               |  +-----------------------------+  |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Event Configuration         |  |
|                               |  | Type: [User Signup ▼]       |  |
|                               |  +-----------------------------+  |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Conditions                 |  |
|                               |  | If: [User Age] [>=] [18]   |  |
|                               |  | And: [Purchase Value] [>] [50]|
|                               |  | +➕ Add Condition            |  |
|                               |  +-----------------------------+  |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Action                     |  |
|                               |  | Send: [Welcome Template ▼] |  |
|                               |  | To: [New Users Segment ▼]  |  |
|                               |  | Delay: [30] [Minutes ▼]    |  |
|                               |  +-----------------------------+  |
|                               |                                   |
|                               |  [Cancel]    [Save Changes]       |
+-------------------------------+------------------------------------+
===================== DELETE CONFIRMATION =====================
|                               |  Delete Trigger?                  |
|                               |                                   |
|                               |  Are you sure you want to delete: |
|                               |  "User Signup Trigger" ?          |
|                               |                                   |
|                               |  ❗ This will affect:              |
|                               |  • 1 active campaign              |
|                               |  • Future user signup actions     |
|                               |                                   |
|                               |  [Cancel]    [Delete Trigger]     |
+-------------------------------+------------------------------------+
