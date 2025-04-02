# WebPush System Actors and Roles

## System Actors

Based on the business flow and ERD, the following key actors have been identified:

1. **System Administrator** - Technical administrators of the WebPush platform
2. **Marketing Manager** - Oversees all marketing campaigns and strategies
3. **Campaign Manager** - Creates and manages WebPush campaigns
4. **Content Editor** - Creates and edits notification templates and content
5. **Analytics Specialist** - Analyzes performance data and generates reports
6. **Segment Manager** - Creates and manages user segments
7. **Integration Specialist** - Manages webhooks and third-party integrations
8. **End User** - Recipient of WebPush notifications (not a system user)

## Role Definitions and Permissions

### 1. System Administrator
**Description:** Has complete unrestricted access to all system features and configurations.

**Permissions:**
- Full access to all system features, settings, and data without any restrictions
- User management (create, read, update, delete all user accounts)
- Role management (assign, modify, revoke roles)
- System configuration (modify all system settings)
- Database access (direct access to all data)
- Security settings (manage API keys, authentication settings)
- Access to logs and monitoring tools
- Server and infrastructure management

### 2. Marketing Manager
**Description:** Responsible for overseeing the marketing strategy and campaign performance.

**Permissions:**
- View all campaigns, segments, templates, and analytics
- Approve/reject campaigns before publishing
- Access comprehensive analytics dashboards
- Create and manage team members' access (limited to marketing roles)
- Set notification frequency policies
- View CDP integration data and insights
- Access CEP decision metrics and channel performance

### 3. Campaign Manager
**Description:** Creates, schedules, and manages WebPush campaigns.

**Permissions:**
- Create/edit/delete campaigns
- Schedule and publish campaigns
- Select segments for targeting
- Choose templates for campaigns
- Create and manage A/B tests
- View campaign analytics
- Set up automated triggers
- Access limited CDP data relevant to campaigns

### 4. Content Editor
**Description:** Creates and manages notification templates and content.

**Permissions:**
- Create/edit/delete notification templates
- Manage dynamic variables
- Design notification appearance
- Upload and manage media assets
- Preview notifications
- Limited access to campaign creation (draft only)
- No access to user data or segments

### 5. Analytics Specialist
**Description:** Analyzes campaign performance and creates reports.

**Permissions:**
- View comprehensive analytics data
- Create custom reports and dashboards
- Export analytics data
- View campaign, segment, and template information (read-only)
- Access CDP integration data for reporting
- View A/B test results
- No ability to create or modify campaigns

### 6. Segment Manager
**Description:** Creates and manages user segments for targeting.

**Permissions:**
- Create/edit/delete user segments
- Define segment criteria and rules
- View anonymized user data
- Import/export segment data
- Access CDP data for segmentation purposes
- View campaign performance by segment
- No direct access to individual user identifiable information

### 7. Integration Specialist
**Description:** Manages external system integrations and webhooks.

**Permissions:**
- Create/edit/delete webhooks
- Configure CDP/CEP integrations
- Manage API access and keys
- Monitor integration performance
- Access integration logs
- Limited access to notification data related to integrations
- No access to create campaigns or segments

## Permission Matrix

| Feature | Admin | Marketing Manager | Campaign Manager | Content Editor | Analytics Specialist | Segment Manager | Integration Specialist |
|---------|-------|-------------------|------------------|----------------|----------------------|-----------------|------------------------|
| User Management | ✓ | ✓ (limited) | ✗ | ✗ | ✗ | ✗ | ✗ |
| Campaign Creation | ✓ | ✓ | ✓ | ✓ (draft) | ✗ | ✗ | ✗ |
| Campaign Publishing | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Template Management | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| Segment Creation | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Analytics Access | ✓ | ✓ | ✓ (limited) | ✗ | ✓ | ✓ (limited) | ✓ (integration only) |
| A/B Testing | ✓ | ✓ | ✓ | ✗ | ✓ (view) | ✗ | ✗ |
| Trigger Management | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ (integration) |
| Webhook Config | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| CDP/CEP Config | ✓ | ✓ (view) | ✗ | ✗ | ✓ (view) | ✓ (view) | ✓ |
| System Settings | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

## Admin Role Implementation Note

The System Administrator role is configured with unrestricted access to all features and data without any additional authorization checks. This provides maximum flexibility for system management but should be granted very selectively for security reasons. This role bypasses all permission checks in the application code.

## Role-Based Access Control Implementation

The permissions system should be implemented using a role-based access control (RBAC) model where:

1. Each user is assigned one or more roles
2. Each role has a defined set of permissions
3. Permissions are checked before allowing access to features
4. The admin role bypasses all permission checks

For granular access control, consider implementing custom permission groups that can be assigned to specific campaigns, segments, or templates.
