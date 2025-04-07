[The entire file with the suggested changes, exactly as provided in the suggestion]

+----------------------------------------------------------------------+
|                      WEBPUSH API MANAGEMENT                          |
+-------------------------------+------------------------------------+
| NAVIGATION                    |  CONTENT (TEMPLATES)               |
+-------------------------------+------------------------------------+
===================== TEMPLATE LISTING PAGE =====================
| [Notifications]                   |  Push Templates                   |
| [Subscriptions]               |                                   |
| [Segments]                    |  + Create Template                 |
| [Templates] ►                   |                                   |
| [Campaigns]                   |  [Status: All ▼] [Search...] [🔍]  |
| [Automations]                  |                                   |
| [Analytics]                   |  Showing 18 push templates         |
| [Integrations]                |                                   |
| [Settings]                    |  +----+----------------+------+---+
|                               |  | ID | Title          |Status| 🛠 |
|                               |  +----+----------------+------+---+
|                               |  | 1  | Welcome Template|✅ Live|⋮|
|                               |  | 2  | Promo Template  |🔄 Draft|⋮|
|                               |  | 3  | Update Template |✅ Live|⋮|
|                               |  +----+----------------+------+---+
|                               |                                   |
|                               |  [← Previous] [1] [Next →]        |
+-------------------------------+------------------------------------+
===================== CREATE TEMPLATE FORM =====================
|                               |  Create Push Template             |
|                               |                                   |
|                               |  Template Title:                  |
|                               |  [______________________________] |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Template Builder            |  |
|                               |  | Title: [__________________] |  |
|                               |  | Body: [___________________] |  |
|                               |  | Icon: [📁 Upload]           |  |
|                               |  | Image: [📁 Upload]          |  |
|                               |  | Action URL: [_____________] |  |
|                               |  +-----------------------------+  |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Personalization Vars        |  |
|                               |  | {user.name}                 |  |
|                               |  | {company.name}              |  |
|                               |  | {product.title}             |  |
|                               |  +-----------------------------+  |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Advanced Options            |  |
|                               |  | Category: [Select ▼]        |  |
|                               |  | Tags: [Marketing, Promo]    |  |
|                               |  | Version: 1.0                |  |
|                               |  +-----------------------------+  |
|                               |                                   |
|                               |  [Preview]                       |
|                               |                                   |
|                               |  [Cancel]    [Save Template]     |
+-------------------------------+------------------------------------+
===================== TEMPLATE DETAILS PAGE =====================
|                               |  Welcome Template (#15)           |
|                               |                                   |
|                               |  [✏ Edit] [🗑 Delete] [↻ Clone]   |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Overview                   |  |
|                               |  | Status: ✅ Active          |  |
|                               |  | Created: May 1, 2023       |  |
|                               |  | Last Modified: Jun 10, 2023|  |
|                               |  +-----------------------------+  |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Template Preview           |  |
|                               |  | [Mobile notification mockup]|  |
|                               |  | Title: Welcome!            |  |
|                               |  | Body: Thanks for joining   |  |
|                               |  +-----------------------------+  |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Usage Statistics           |  |
|                               |  | Used in 12 campaigns       |  |
|                               |  | Total sends: 5,342         |  |
|                               |  +-----------------------------+  |
+-------------------------------+------------------------------------+
===================== EDIT TEMPLATE FORM =====================
|                               |  Edit Welcome Template (#15)      |
|                               |                                   |
|                               |  Template Title:                  |
|                               |  [Welcome Template______________] |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Template Builder            |  |
|                               |  | Title: [Welcome!_________]  |  |
|                               |  | Body: [Thanks for...______] |  |
|                               |  | Icon: [✅ uploaded.png]     |  |
|                               |  | Action URL: [https://...__] |  |
|                               |  +-----------------------------+  |
|                               |                                   |
|                               |  +-----------------------------+  |
|                               |  | Personalization Vars        |  |
|                               |  | ✅ {user.name}              |  |
|                               |  | ✅ {company.name}           |  |
|                               |  +-----------------------------+  |
|                               |                                   |
|                               |  [Preview]                       |
|                               |                                   |
|                               |  [Cancel]    [Save Changes]      |
+-------------------------------+------------------------------------+
===================== DELETE CONFIRMATION =====================
|                               |  Delete Push Template?            |
|                               |                                   |
|                               |  Are you sure you want to delete: |
|                               |  "Welcome Template" ?             |
|                               |                                   |
|                               |  ❗ This will affect:              |
|                               |  • 12 active campaigns            |
|                               |  • Future notification sends      |
|                               |                                   |
|                               |  [Cancel]    [Delete Template]    |
+-------------------------------+------------------------------------+
