# Component Library Documentation

> **Surgify UI Components** - Modular, reusable interface components

## 📚 Component Overview

The Surgify Component Library provides a comprehensive set of UI components designed for medical applications. Each component is:

- **🔧 Modular** - Standalone functionality with no dependencies
- **🎨 Customizable** - Extensive configuration options
- **♿ Accessible** - ARIA compliant and keyboard navigable
- **📱 Responsive** - Mobile-first design approach
- **⚡ Performant** - Optimized for fast rendering and interaction

## 🎯 Component Catalog

### Core Components

| Component | Purpose | Size | Status | Documentation |
|-----------|---------|------|--------|---------------|
| **DomainSelector** | Medical domain selection dropdown | 6.5KB | ✅ Stable | [View Docs](./domain-selector.md) |
| **CaseList** | Case management with filtering/search | 12KB | ✅ Stable | [View Docs](./case-list.md) |
| **CaseDetail** | Detailed case view with tabs | 15KB | ✅ Stable | [View Docs](./case-detail.md) |
| **NotificationBadge** | Notification badges with animations | 8KB | ✅ Stable | [View Docs](./notification-badge.md) |
| **ThemeToggle** | Theme switching with system detection | 10KB | ✅ Stable | [View Docs](./theme-toggle.md) |

### Component Hierarchy

```
UI Components
├── Input Components
│   └── DomainSelector          # Domain selection
├── Display Components
│   ├── CaseList               # Data listing
│   ├── CaseDetail             # Detailed views
│   └── NotificationBadge      # Status indicators
└── Control Components
    └── ThemeToggle             # Theme management
```

## 🚀 Quick Start

### 1. Include Component Library

```html
<!-- In your HTML head -->
<link rel="stylesheet" href="/static/css/components.css">

<!-- Before closing body tag -->
<script src="/static/js/components/index.js"></script>
```

### 2. Initialize Components

```javascript
// Automatic initialization
document.addEventListener('DOMContentLoaded', function() {
    SurgifyComponents.initialize();
});

// Manual initialization
const selector = new DomainSelector('container-id', {
    domains: ['Surgery', 'Oncology', 'Pathology'],
    onSelect: (domain) => console.log('Selected:', domain)
});
selector.render();
```

### 3. HTML Structure

```html
<!-- Auto-init with data attributes -->
<div id="domain-selector" 
     data-component="domain-selector"
     data-auto-init="true"
     data-domains='["Surgery", "Oncology"]'>
</div>

<!-- Or use empty container for manual init -->
<div id="manual-selector"></div>
```

## 🏗️ Architecture Patterns

### Component Structure

All components follow a consistent architecture:

```javascript
class ComponentName {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = { /* default options */ ...options };
    }
    
    render() {
        // Generate and inject HTML
    }
    
    attachEventListeners() {
        // Set up interactivity
    }
    
    // Public API methods
    setValue(value) { /* ... */ }
    getValue() { /* ... */ }
    
    // Event handling
    handleEvent() { /* ... */ }
}
```

### Configuration Options

Each component accepts a configuration object with:

- **Required Options**: Essential configuration
- **Optional Options**: Customization settings with defaults
- **Callback Functions**: Event handlers and custom logic
- **HTMX Integration**: Server communication settings

### Event System

Components use a custom event system for communication:

```javascript
// Component dispatches events
component.dispatchEvent(new CustomEvent('componentAction', {
    detail: { data: 'value' },
    bubbles: true
}));

// Listen for component events
document.addEventListener('componentAction', (e) => {
    console.log('Event data:', e.detail);
});
```

## 🎨 Styling & Theming

### CSS Architecture

```
components.css
├── Base Styles              # Common component styles
├── Component Specific       # Individual component styles
├── Theme Variables          # CSS custom properties
├── Responsive Breakpoints   # Mobile adaptations
├── Animation Definitions    # Transitions and effects
└── Accessibility Overrides # High contrast, reduced motion
```

### Theme System

Components support light/dark themes with CSS custom properties:

```css
:root {
    --component-bg: #ffffff;
    --component-text: #1f2937;
    --component-border: #e5e7eb;
}

.dark {
    --component-bg: #374151;
    --component-text: #f9fafb;
    --component-border: #6b7280;
}
```

### Customization

Override default styles with CSS classes:

```css
/* Custom component styling */
.my-custom-selector .domain-selector-trigger {
    background: linear-gradient(45deg, #3b82f6, #8b5cf6);
    border-radius: 12px;
}
```

## 🔌 Integration Patterns

### HTMX Integration

Components are designed to work seamlessly with HTMX:

```html
<!-- Component with HTMX endpoint -->
<div data-component="case-list"
     data-htmx-endpoint="/api/cases"
     data-auto-init="true">
</div>
```

```javascript
// Component automatically includes HTMX attributes
const caseList = new CaseList('container', {
    htmxEndpoint: '/api/cases',
    onCaseSelect: (caseData) => {
        // Handle selection
    }
});
```

### Event-Driven Communication

Components communicate through events rather than direct coupling:

```javascript
// Component A emits event
domainSelector.addEventListener('domainSelected', (e) => {
    // Filter case list based on domain
    caseList.filterByDomain(e.detail.domain);
});

// Component B responds to event
caseList.addEventListener('caseSelected', (e) => {
    // Show case details
    caseDetail.setCase(e.detail.case);
});
```

## 📊 Performance Considerations

### Bundle Sizes
- **Individual Components**: 6-15KB each
- **Complete Library**: ~52KB unminified
- **CSS Styles**: ~8KB additional
- **Runtime Memory**: Minimal footprint

### Optimization Strategies
- **Lazy Loading**: Load components on demand
- **Tree Shaking**: Include only used components
- **CSS Purging**: Remove unused styles
- **Event Delegation**: Efficient event handling

### Performance Benchmarks
- **Initialization**: < 50ms per component
- **Rendering**: < 100ms for complex components
- **Memory Usage**: < 1MB for full library
- **Bundle Parse**: < 10ms on modern browsers

## 🧪 Testing Strategy

### Component Testing
Each component includes:
- **Unit Tests**: Individual method testing
- **Integration Tests**: Component interaction testing
- **Visual Tests**: UI consistency testing
- **Accessibility Tests**: ARIA and keyboard testing

### Test Structure
```
tests/
├── unit/
│   ├── domain-selector.test.js
│   ├── case-list.test.js
│   └── ...
├── integration/
│   ├── component-communication.test.js
│   └── htmx-integration.test.js
└── accessibility/
    ├── keyboard-navigation.test.js
    └── screen-reader.test.js
```

## 🔧 Development Guidelines

### Creating New Components

1. **Follow Naming Convention**: PascalCase for classes
2. **Use Consistent Structure**: Constructor, render, attach listeners
3. **Include Documentation**: JSDoc comments and README
4. **Add Tests**: Unit and integration tests
5. **Update Index**: Add to component registry

### Code Quality Standards

- **ESLint Configuration**: Consistent code style
- **JSDoc Comments**: Comprehensive documentation
- **Error Handling**: Graceful failure modes
- **Browser Support**: Modern browser compatibility

### Contribution Process

1. **Create Feature Branch**: `feature/new-component`
2. **Develop Component**: Follow established patterns
3. **Write Tests**: Ensure full coverage
4. **Update Documentation**: Add to this documentation
5. **Submit PR**: Include examples and tests

## 📚 Component Reference

### Quick Reference Table

| Method | DomainSelector | CaseList | CaseDetail | NotificationBadge | ThemeToggle |
|--------|----------------|----------|------------|-------------------|-------------|
| `render()` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `setValue()` | ✅ | ❌ | ✅ | ✅ | ✅ |
| `getValue()` | ✅ | ❌ | ✅ | ✅ | ✅ |
| `reset()` | ❌ | ❌ | ❌ | ✅ | ❌ |
| `destroy()` | ❌ | ❌ | ❌ | ✅ | ✅ |

### Event Reference Table

| Event | Emitted By | Data | Description |
|-------|------------|------|-------------|
| `domainSelected` | DomainSelector | `{domain}` | Domain selection changed |
| `caseSelected` | CaseList | `{case}` | Case item selected |
| `caseSaved` | CaseDetail | `{case}` | Case data saved |
| `countChanged` | NotificationBadge | `{oldCount, newCount}` | Badge count updated |
| `themeChanged` | ThemeToggle | `{theme}` | Theme switched |

## 🚀 Future Roadmap

### Planned Components
- **DataTable** - Advanced data grid with sorting/filtering
- **Modal** - Overlay dialogs and confirmations
- **DatePicker** - Medical appointment scheduling
- **Chart** - Data visualization components
- **Form** - Complex form handling with validation

### Planned Features
- **Component Builder** - Visual component creation tool
- **Theme Editor** - Custom theme creation interface
- **Analytics** - Component usage tracking
- **A11y Scanner** - Automated accessibility testing
- **Performance Monitor** - Runtime performance tracking

---

## 📞 Support

For component-specific questions or issues:

1. **Check Documentation**: Individual component docs
2. **View Examples**: Live examples in demo page
3. **Search Issues**: GitHub issue tracker
4. **Create Issue**: For bugs or feature requests
5. **Community**: Discussions and Q&A

**Next Steps**: Choose a component above to dive into detailed documentation!
