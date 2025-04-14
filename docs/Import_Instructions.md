# Importing the WebPush API Postman Collection

Follow these steps to import the WebPush API Postman collection and environment:

1. Open Postman
2. Click on "Import" button in the top left corner
3. Select "Files" and browse to the following files:
   - `WebPush_API_Postman_Collection.json`
   - `WebPush_API_Environment.json`
4. Click "Import"
5. Select the "WebPush API Environment" from the environment dropdown in the top right corner

## Available Endpoints

The collection includes the following endpoint groups:

- **Authentication**: Login and registration endpoints
- **Push Notifications**: Send individual and broadcast notifications
- **Subscriptions**: Manage user push notification subscriptions
- **Users**: User profile and preference management
- **Health Check**: API health check endpoint

## Usage

1. First, use the "Login" request to authenticate and get a JWT token
2. The token will be automatically stored in the environment variables
3. All other authenticated requests will use this token automatically
4. You can modify the environment variables as needed for your testing

## Variables

- `base_url`: The base URL of your API (default: http://localhost:8000)
- `username`: Your username for authentication
- `password`: Your password for authentication
- `auth_token`: JWT authentication token (automatically set after login)
- `user_id`: ID of the user for user-specific requests
- `subscription_id`: ID of subscription for subscription-specific requests
