# NotificationBadge Component

## Description
The `NotificationBadge` component displays a badge with the number of notifications. It is designed to be lightweight and easily integrated into navigation bars or headers.

## Features
- Notification count display.
- HTMX hooks for dynamic updates.
- Tailwind CSS for styling.

## Usage
```html
<div hx-get="/notifications" hx-trigger="load" class="notification-badge">
  <span>3</span>
</div>
```

## Code Snippet
```javascript
// NotificationBadge.js
export function NotificationBadge() {
  // Initialization code
}
```

## Notes
- Ensure the backend endpoint `/notifications` is configured to return notification data.
- Customize styles using Tailwind CSS classes.
