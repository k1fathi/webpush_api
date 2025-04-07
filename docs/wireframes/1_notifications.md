+----------------------------------------------------------------------+
|                      WEBPUSH API MANAGEMENT                          |
+-------------------------------+------------------------------------+
| NAVIGATION                    |  NOTIFICATIONS                     |
+-------------------------------+------------------------------------+
===================== NOTIFICATION LISTING PAGE =====================
| [Notifications] ►             |  Notifications                     |
| [Subscriptions]               |                                    |
| [Segments]                    |  + Create Notification             |
| [Templates]                   |                                    |
| [Campaigns]                   |  [Status: All ▼] [Search...] [🔍]  |
| [Triggers]                    |                                    |
| [Analytics]                   |  Showing 28 notifications          |
| [Integrations]                |                                    |
| [Settings]                    |  +----+----------------+------+--------+
|                               |  | ID | Title          |Status|Actions |
|                               |  +----+----------------+------+--------+
|                               |  | 1  | System Update  |✅ Sent |👁️ ✏️ 🗑️ |
|                               |  | 2  | New Feature    |⏳ Scheduled|👁️ ✏️ 🗑️|
|                               |  | 3  | Alert          |❌ Failed |👁️ ✏️ 🗑️ |
|                               |  +----+----------------+------+--------+
|                               |                                    |
|                               |  [← Previous] [1] [2] [Next →]     |
+-------------------------------+------------------------------------+
===================== CREATE NOTIFICATION FORM =====================
|                               |  Create Notification               |
|                               |                                    |
|                               |  Notification Title:               |
|                               |  [_______________________________] |
|                               |                                    |
|                               |  Content Source:                   |
|                               |  (●) Use Template                  |
|                               |      [Select Template ▼]           |
|                               |  ( ) Custom Message                |
|                               |                                    |
|                               |  Message Content:                  |
|                               |  [_______________________________] |
|                               |  [✎ Formatting toolbar]            |
|                               |  (Disabled when using template)    |
|                               |                                    |
|                               |  +-----------------------------+   |
|                               |  | Template Variables          |   |
|                               |  | {user.name} {user.email}    |   |
|                               |  +-----------------------------+   |
|                               |                                    |
|                               |  +---------------+ +-------------+ |
|                               |  | Target Segment| | Priority    | |
|                               |  | [Select ▼]    | | [Normal ▼]  | |
|                               |  +---------------+ +-------------+ |
|                               |                                    |
|                               |  Delivery Options:                 |
|                               |  [ ] Immediate    [ ] Schedule     |
|                               |  If scheduled: [📅 Date] [🕒 Time]  |
|                               |                                    |
|                               |  [Preview]                         |
|                               |                                    |
|                               |  [Cancel]    [Send Notification]   |
+-------------------------------+------------------------------------+
===================== NOTIFICATION DETAILS PAGE =====================
|                               |  System Update (#105)              |
|                               |                                    |
|                               |  [✏ Edit] [🗑 Delete] [↻ Resend]   |
|                               |                                    |
|                               |  +-------------------------------+ |
|                               |  | Overview                     | |
|                               |  | Status: ✅ Delivered         | |
|                               |  | Sent: Jun 15, 2023 10:30 AM  | |
|                               |  | Sender: admin@company.com    | |
|                               |  | Template: System Template    | |
|                               |  +-------------------------------+ |
|                               |                                    |
|                               |  +-------------------------------+ |
|                               |  | Content                      | |
|                               |  | Title: System Maintenance    | |
|                               |  | Message: We'll be performing.| |
|                               |  +-------------------------------+ |
|                               |                                    |
|                               |  +-------------------------------+ |
|                               |  | Delivery Stats               | |
|                               |  | Target: All Users (1,245)    | |
|                               |  | Delivered: 1,200 (96%)       | |
|                               |  | Opened: 840 (70%)            | |
|                               |  | Clicked: 420 (35%)           | |
|                               |  +-------------------------------+ |
+-------------------------------+------------------------------------+
===================== EDIT NOTIFICATION FORM =====================
|                               |  Edit System Update (#105)        |
|                               |                                    |
|                               |  +-----------------------------+   |
|                               |  | Template: System Template   |   |
|                               |  | [Change Template]           |   |
|                               |  +-----------------------------+   |
|                               |                                    |
|                               |  Notification Title:               |
|                               |  [System Maintenance___________]   |
|                               |                                    |
|                               |  Message Content:                  |
|                               |  [We'll be performing...________]  |
|                               |  [✎ Formatting toolbar]            |
|                               |                                    |
|                               |  Target Audience:                  |
|                               |  [All Users (selected) ▼]          |
|                               |                                    |
|                               |  Delivery Options:                 |
|                               |  [✓ Immediate] [ ] Schedule       |
|                               |                                    |
|                               |  [Preview]                         |
|                               |                                    |
|                               |  [Cancel]    [Save Changes]        |
+-------------------------------+------------------------------------+
===================== DELETE CONFIRMATION =====================
|                               |  Delete Notification?              |
|                               |                                    |
|                               |  Are you sure you want to delete:  |
|                               |  "System Maintenance" notification?|
|                               |                                    |
|                               |  ❗ This will:                     |
|                               |  • Remove the notification record  |
|                               |  • Delete delivery statistics      |
|                               |  • Remove it from reports         |
|                               |                                    |
|                               |  [Cancel]    [Delete Notification] |
+-------------------------------+------------------------------------+
|                               |  Edit System Update (#105)        |
===================== NOTIFICATION DETAILS PAGE =====================
|                               |  System Update (#105)              |
|                               |                                    |
|                               |  Notification Title:              |
|                               |  [System Maintenance___________]  |
|                               |                                    |
|                               |  Message Content:                 |
|                               |  [We'll be performing...________] |
|                               |  [✎ Formatting toolbar]           |
|                               |                                    |
|                               |  Target Audience:                 |
|                               |  [All Users (selected) ▼]         |
|                               |  [✏ Edit] [🗑 Delete] [↻ Resend]   |
|                               |                                    |
|                               |  +-------------------------------+ |
|                               |  | Overview                     | |
|                               |  | Status: ✅ Delivered         | |
|                               |  | Sent: Jun 15, 2023 10:30 AM  | |
|                               |  | Sender: admin@company.com    | |
|                               |  | Template: System Template    | |
|                               |  +-------------------------------+ |
|                               |                                    |
|                               |  Delivery Options:                |
|                               |  [✓ Immediate] [ ] Schedule      |
|                               |                                    |
|                               |  [Preview]                        |
|                               |                                    |
|                               |  [Cancel]    [Save Changes]       |
+-------------------------------+------------------------------------+
===================== DELETE CONFIRMATION =====================
|                               |  Delete Notification?             |
|                               |                                    |
|                               |  Are you sure you want to delete: |
|                               |  "System Maintenance" notification?|
|                               |                                    |
|                               |  ❗ This will:                     |
|                               |  • Remove the notification record |
|                               |  • Delete delivery statistics     |
|                               |                                    |
|                               |  [Cancel]    [Delete Notification]|
|                               |  +-------------------------------+ |
|                               |  | Content                      | |
|                               |  | Title: System Maintenance    | |
|                               |  | Message: We'll be performing.| |
|                               |  +-------------------------------+ |
|                               |                                    |
|                               |  +-------------------------------+ |
|                               |  | Delivery Stats               | |
|                               |  | Target: All Users (1,245)    | |
|                               |  | Delivered: 1,200 (96%)       | |
|                               |  | Opened: 840 (70%)            | |
|                               |  | Clicked: 420 (35%)           | |
|                               |  +-------------------------------+ |
+-------------------------------+------------------------------------+
|                               |  [Cancel]    [Save Changes]       |
|                               |  +-----------------------------+   |
|                               |  | Template: System Template   |   |
|                               |  | [Change Template]           |   |
|                               |  +-----------------------------+   |
|                               |                                    |
|                               |  Notification Title:               |
|                               |  [System Maintenance___________]   |
|                               |                                    |
|                               |  Message Content:                  |
|                               |  [We'll be performing...________]  |
|                               |  [✎ Formatting toolbar]            |
|                               |                                    |
|                               |  Target Audience:                  |
|                               |  [All Users (selected) ▼]          |
|                               |                                    |
|                               |  Delivery Options:                 |
|                               |  [✓ Immediate] [ ] Schedule       |
|                               |                                    |
|                               |  [Preview]                         |
|                               |                                    |
|                               |  [Cancel]    [Save Changes]        |
+-------------------------------+------------------------------------+

===================== DELETE CONFIRMATION =====================
|                               |  Delete Notification?             |
|                               |  Delete Notification?              |
|                               |                                    |
|                               |  Are you sure you want to delete: |
|                               |  Are you sure you want to delete:  |
|                               |  "System Maintenance" notification?|
|                               |                                    |
|                               |  ❗ This will:                     |
|                               |  • Remove the notification record |
|                               |  • Delete delivery statistics     |
|                               |                                    |
|                               |  [Cancel]    [Delete Notification]|
|                               |  +-------------------------------+ |
|                               |  | Content                      | |
|                               |  | Title: System Maintenance    | |
|                               |  | Message: We'll be performing.| |
|                               |  +-------------------------------+ |
|                               |                                    |
|                               |  +-------------------------------+ |
|                               |  | Delivery Stats               | |
|                               |  | Target: All Users (1,245)    | |
|                               |  | Delivered: 1,200 (96%)       | |
|                               |  | Opened: 840 (70%)            | |
|                               |  | Clicked: 420 (35%)           | |
|                               |  +-------------------------------+ |
|                               |  • Remove the notification record  |
|                               |  • Delete delivery statistics      |
|                               |  • Remove it from reports         |
|                               |                                    |
|                               |  [Cancel]    [Delete Notification] |
+-------------------------------+------------------------------------+

|                               |  Edit System Update (#105)        |
===================== NOTIFICATION DETAILS PAGE =====================
|                               |  System Update (#105)              |
|                               |                                    |
|                               |  Notification Title:              |
|                               |  [System Maintenance___________]  |
|                               |                                    |
|                               |  Message Content:                 |
|                               |  [We'll be performing...________] |
|                               |  [✎ Formatting toolbar]           |
|                               |                                    |
|                               |  Target Audience:                 |
|                               |  [All Users (selected) ▼]         |
|                               |  [✏ Edit] [🗑 Delete] [↻ Resend]   |
|                               |                                    |
|                               |  +-------------------------------+ |
|                               |  | Overview                     | |
|                               |  | Status: ✅ Delivered         | |
|                               |  | Sent: Jun 15, 2023 10:30 AM  | |
|                               |  | Sender: admin@company.com    | |
|                               |  | Template: System Template    | |
|                               |  +-------------------------------+ |
|                               |                                    |
|                               |  Delivery Options:                |
|                               |  [✓ Immediate] [ ] Schedule      |
|                               |                                    |
|                               |  [Preview]                        |
|                               |                                    |
|                               |  [Cancel]    [Save Changes]       |
+-------------------------------+------------------------------------+
===================== DELETE CONFIRMATION =====================
|                               |  Delete Notification?             |
|                               |                                    |
|                               |  Are you sure you want to delete: |
|                               |  "System Maintenance" notification?|
|                               |                                    |
|                               |  ❗ This will:                     |
|                               |  • Remove the notification record |
|                               |  • Delete delivery statistics     |
|                               |                                    |
|                               |  [Cancel]    [Delete Notification]|
|                               |  +-------------------------------+ |
|                               |  | Content                      | |
|                               |  | Title: System Maintenance    | |
|                               |  | Message: We'll be performing.| |
|                               |  +-------------------------------+ |
|                               |                                    |
|                               |  +-------------------------------+ |
|                               |  | Delivery Stats               | |
|                               |  | Target: All Users (1,245)    | |
|                               |  | Delivered: 1,200 (96%)       | |
|                               |  | Opened: 840 (70%)            | |
|                               |  | Clicked: 420 (35%)           | |
|                               |  +-------------------------------+ |
+-------------------------------+------------------------------------+
