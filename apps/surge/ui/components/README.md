# Surgify UI Component Library

A reusable component library for the Surgify platform, built with HTML, Tailwind CSS, vanilla JavaScript, and HTMX integration.

## Overview

This component library provides a set of standalone, reusable UI components that can be used throughout the Surgify platform. Each component is designed to be:

- **Standalone**: Can be used independently without dependencies on other components
- **Responsive**: Works across different screen sizes and devices
- **Accessible**: Built with accessibility best practices
- **Customizable**: Highly configurable through options
- **HTMX-ready**: Integrated hooks for HTMX interactions
- **Event-driven**: Emits custom events for component interactions

## Components

### 1. DomainSelector
A dropdown component for selecting medical domains.

**Features:**
- Searchable dropdown interface
- Custom domain lists
- HTMX endpoint integration
- Keyboard navigation support
- Custom event dispatching

**Usage:**
```javascript
const selector = new DomainSelector('container-id', {
    domains: ['Gastric Surgery', 'Oncology', 'Pathology', 'Radiology'],
    selectedDomain: 'Oncology',
    placeholder: 'Select a domain...',
    onSelect: (domain) => console.log('Selected:', domain),
    htmxEndpoint: '/api/domains/select'
});
selector.render();
```

### 2. CaseList
A comprehensive list component for displaying and managing cases.

**Features:**
- Search functionality
- Status filtering
- Pagination
- Responsive grid layout
- Case selection handling
- HTMX integration for dynamic loading

**Usage:**
```javascript
const caseList = new CaseList('container-id', {
    cases: casesArray,
    showSearch: true,
    showFilters: true,
    pageSize: 10,
    onCaseSelect: (caseData) => console.log('Case selected:', caseData),
    htmxEndpoint: '/api/cases'
});
caseList.render();
```

### 3. CaseDetail
A detailed view component for individual cases with tabs and editing capabilities.

**Features:**
- Tabbed interface (overview, clinical, imaging, notes)
- Inline editing mode
- Note management
- Image gallery
- Action buttons
- Form validation

**Usage:**
```javascript
const caseDetail = new CaseDetail('container-id', {
    case: caseObject,
    showTabs: true,
    showActions: true,
    editable: true,
    htmxEndpoint: '/api/cases'
});
caseDetail.render();
```

### 4. NotificationBadge
A flexible notification badge that can be attached to any element.

**Features:**
- Multiple color themes
- Different sizes
- Position options
- Animation support
- Auto-update functionality
- WebSocket integration ready

**Usage:**
```javascript
const badge = new NotificationBadge('container-id', {
    count: 5,
    type: 'danger',
    size: 'medium',
    position: 'top-right',
    autoUpdate: true,
    htmxEndpoint: '/api/notifications/count'
});
badge.render();
```

### 5. ThemeToggle
A theme switching component with multiple styles and automatic system detection.

**Features:**
- Multiple UI styles (switch, button, icon)
- Light/dark/auto modes
- System theme detection
- Persistent storage
- Smooth transitions

**Usage:**
```javascript
const themeToggle = new ThemeToggle('container-id', {
    style: 'switch',
    showLabel: true,
    autoDetect: true,
    onChange: (theme) => console.log('Theme changed:', theme)
});
themeToggle.render();
```

## Installation & Setup

### 1. Include Component Files

Add the component scripts to your HTML template:

```html
<!-- Component Library -->
<script src="/static/js/components/DomainSelector.js"></script>
<script src="/static/js/components/CaseList.js"></script>
<script src="/static/js/components/CaseDetail.js"></script>
<script src="/static/js/components/NotificationBadge.js"></script>
<script src="/static/js/components/ThemeToggle.js"></script>
<script src="/static/js/components/index.js"></script>
```

### 2. Auto-initialization with Data Attributes

Components can be automatically initialized using data attributes:

```html
<div id="my-domain-selector" 
     data-component="domain-selector" 
     data-auto-init="true"
     data-domains='["Surgery", "Oncology"]'
     data-placeholder="Choose domain...">
</div>
```

### 3. Manual Initialization

```javascript
// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    const components = window.SurgifyComponents.createBatch([
        {
            type: 'DomainSelector',
            containerId: 'domain-selector',
            options: { domains: ['Surgery', 'Oncology'] }
        },
        {
            type: 'CaseList',
            containerId: 'case-list',
            options: { cases: [], pageSize: 10 }
        }
    ]);
});
```

## HTMX Integration

All components support HTMX integration through the `htmxEndpoint` option:

```javascript
const component = new ComponentName('container-id', {
    htmxEndpoint: '/api/endpoint',
    // ... other options
});
```

Components will automatically:
- Add appropriate HTMX attributes to interactive elements
- Handle HTMX response events
- Maintain state during HTMX updates

## Event System

Components emit custom events that can be listened to:

```javascript
// Listen for component events
document.addEventListener('domainSelected', (e) => {
    console.log('Domain selected:', e.detail.domain);
});

document.addEventListener('caseSelected', (e) => {
    console.log('Case selected:', e.detail.case);
});

document.addEventListener('themeChanged', (e) => {
    console.log('Theme changed:', e.detail);
});
```

## Styling

Components use Tailwind CSS classes and include built-in dark mode support. Custom styling can be applied through:

1. **CSS Classes**: Add custom classes via the `className` option
2. **CSS Variables**: Override component-specific CSS variables
3. **Theme Customization**: Modify color schemes through Tailwind configuration

## Demo Page

View all components in action at `/demo-components`:

- Live examples of each component
- Interactive demos with sample data
- Code snippets for implementation
- Integration examples

## File Structure

```
src/surgify/ui/components/
├── DomainSelector.js          # Domain selection dropdown
├── CaseList.js               # Case list with filtering
├── CaseDetail.js             # Detailed case view
├── NotificationBadge.js      # Notification badges
├── ThemeToggle.js           # Theme switching
├── index.js                 # Component registry and utilities
└── README.md               # This documentation

src/surgify/ui/web/static/js/components/
├── [Component files copied here for serving]

src/surgify/ui/web/templates/
├── base.html               # Updated with component imports
└── demo_components.html    # Component demonstration page
```

## Best Practices

### 1. Component Initialization
- Always wait for DOM ready before initializing components
- Use the component registry for consistent initialization
- Handle missing containers gracefully

### 2. Data Management
- Keep component data separate from DOM manipulation
- Use the public API methods to update component state
- Listen to component events for data synchronization

### 3. Performance
- Initialize components only when needed
- Use pagination for large datasets
- Leverage HTMX for efficient DOM updates

### 4. Accessibility
- Components include ARIA attributes by default
- Test with keyboard navigation
- Ensure sufficient color contrast

### 5. Error Handling
- Components log errors to console for debugging
- Gracefully handle missing data or configuration
- Provide fallback UI states

## Browser Support

- Modern browsers (Chrome 80+, Firefox 75+, Safari 13+, Edge 80+)
- ES6+ features used
- Responsive design for mobile devices
- Progressive enhancement approach

## Contributing

When adding new components:

1. Follow the existing naming conventions
2. Include comprehensive JSDoc comments
3. Add event dispatching for user interactions
4. Support HTMX integration
5. Include accessibility features
6. Add to the component registry
7. Update demo page with examples
8. Document usage patterns

## Troubleshooting

### Components Not Rendering
- Check browser console for JavaScript errors
- Verify container elements exist in DOM
- Ensure component scripts are loaded

### HTMX Integration Issues
- Verify HTMX is loaded before components
- Check endpoint URLs are correct
- Monitor network requests in browser DevTools

### Styling Problems
- Ensure Tailwind CSS is loaded
- Check for CSS conflicts with existing styles
- Verify dark mode classes are applied correctly

## License

This component library is part of the Surgify platform and follows the same licensing terms.
