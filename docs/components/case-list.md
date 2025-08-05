# CaseList Component

> **Comprehensive case management interface with search, filtering, and HTMX integration**

## 📋 Overview

The CaseList component provides a powerful interface for managing and displaying medical cases. It includes advanced search capabilities, filtering options, pagination, and seamless integration with server-side data through HTMX.

### Key Features
- ✅ **Advanced Search** - Full-text search across case data
- ✅ **Multi-Filter System** - Filter by status, priority, date, and custom fields
- ✅ **Pagination** - Handle large datasets efficiently
- ✅ **HTMX Integration** - Real-time data loading and updates
- ✅ **Responsive Design** - Optimized for all screen sizes
- ✅ **Accessibility** - Full keyboard navigation and screen reader support
- ✅ **Batch Operations** - Select and operate on multiple cases
- ✅ **Real-time Updates** - Live case status updates

### Component Stats
- **Bundle Size**: 12.8KB (minified)
- **Dependencies**: None (optional HTMX integration)
- **Browser Support**: Modern browsers (Chrome 80+, Firefox 75+, Safari 13+)
- **Performance**: Virtualized scrolling for 1000+ items

## 🚀 Quick Start

### Basic Usage

```javascript
// Initialize with minimal configuration
const caseList = new CaseList('case-list-container', {
    searchable: true,
    filterable: true,
    paginated: true,
    onCaseSelect: (caseData) => {
        console.log('Selected case:', caseData);
    }
});

caseList.render();
```

### HTML Structure

```html
<!-- Container for the component -->
<div id="case-list-container" class="w-full"></div>

<!-- Or with auto-initialization -->
<div id="auto-case-list" 
     data-component="case-list"
     data-auto-init="true"
     data-searchable="true"
     data-endpoint="/api/cases"
     class="container mx-auto">
</div>
```

### With HTMX Integration

```html
<!-- HTMX-enabled case list -->
<div id="htmx-case-list"
     data-component="case-list"
     data-htmx="true"
     hx-get="/api/cases"
     hx-trigger="load"
     hx-target="#case-list-content">
</div>
```

## ⚙️ Configuration Options

### Constructor Options

```javascript
const options = {
    // Data Configuration
    endpoint: '/api/cases',           // API endpoint for case data
    cases: [],                       // Static case data (optional)
    pageSize: 20,                    // Items per page
    
    // Feature Toggles
    searchable: true,                // Enable search functionality
    filterable: true,                // Enable filtering
    paginated: true,                 // Enable pagination
    selectable: true,                // Enable case selection
    batchOperations: false,          // Enable batch operations
    
    // Search Configuration
    searchPlaceholder: 'Search cases...',
    searchFields: ['title', 'description', 'patientId'],
    searchDebounce: 300,             // Search delay in ms
    
    // Filter Configuration
    filters: {
        status: ['active', 'pending', 'completed', 'archived'],
        priority: ['low', 'medium', 'high', 'urgent'],
        dateRange: true,             // Enable date range filter
        customFilters: {}            // Custom filter definitions
    },
    
    // Display Options
    layout: 'card',                  // 'card', 'table', 'compact'
    showPreview: true,               // Show case preview on hover
    showMetadata: true,              // Show case metadata
    
    // HTMX Options
    htmx: {
        enabled: false,              // Enable HTMX integration
        loadingIndicator: true,      // Show loading states
        errorHandling: true,         // Handle errors gracefully
        realTimeUpdates: false       // Enable WebSocket updates
    },
    
    // Callbacks
    onCaseSelect: null,              // Case selection callback
    onFilter: null,                  // Filter change callback
    onSearch: null,                  // Search callback
    onPageChange: null,              // Pagination callback
    onBatchOperation: null,          // Batch operation callback
    
    // Styling
    theme: 'default',                // 'default', 'minimal', 'clinical'
    customClasses: {}                // Custom CSS classes
};
```

### Data Structure

```javascript
// Expected case data structure
const caseData = {
    id: 'case-001',
    title: 'Gastric Adenocarcinoma - Stage II',
    description: 'Patient presenting with early gastric cancer...',
    patientId: 'P12345',
    status: 'active',
    priority: 'high',
    createdAt: '2024-01-15T10:30:00Z',
    updatedAt: '2024-01-20T14:45:00Z',
    assignedTo: 'Dr. Smith',
    metadata: {
        department: 'Oncology',
        location: 'Room 302',
        tags: ['urgent', 'surgery-candidate']
    },
    // Optional preview data
    preview: {
        imageCount: 5,
        reportCount: 3,
        lastActivity: '2 hours ago'
    }
};
```

## 🎨 Layout Options

### Card Layout (Default)

```javascript
const caseList = new CaseList('container', {
    layout: 'card',
    showPreview: true,
    showMetadata: true
});
```

**Features:**
- Visual card-based display
- Case preview on hover
- Metadata badges
- Responsive grid layout

### Table Layout

```javascript
const caseList = new CaseList('container', {
    layout: 'table',
    columns: ['title', 'status', 'priority', 'updatedAt']
});
```

**Features:**
- Tabular data display
- Sortable columns
- Compact information density
- Excel-like navigation

### Compact Layout

```javascript
const caseList = new CaseList('container', {
    layout: 'compact',
    showMetadata: false
});
```

**Features:**
- Minimal space usage
- List-style display
- Essential information only
- Mobile-optimized

## 🔍 Search & Filtering

### Search Configuration

```javascript
const caseList = new CaseList('container', {
    searchable: true,
    searchFields: ['title', 'description', 'patientId', 'assignedTo'],
    searchPlaceholder: 'Search by case title, patient ID, or doctor...',
    searchDebounce: 500,
    onSearch: (query, results) => {
        console.log(`Found ${results.length} cases for "${query}"`);
    }
});
```

### Advanced Filtering

```javascript
const caseList = new CaseList('container', {
    filterable: true,
    filters: {
        status: {
            label: 'Case Status',
            options: ['active', 'pending', 'completed', 'archived'],
            multiple: true
        },
        priority: {
            label: 'Priority Level',
            options: ['low', 'medium', 'high', 'urgent'],
            multiple: false
        },
        dateRange: {
            label: 'Date Range',
            type: 'daterange',
            enabled: true
        },
        assignedTo: {
            label: 'Assigned Doctor',
            type: 'autocomplete',
            endpoint: '/api/doctors'
        }
    },
    onFilter: (filters, results) => {
        console.log('Applied filters:', filters);
        console.log('Filtered results:', results.length);
    }
});
```

## 📄 Pagination

### Basic Pagination

```javascript
const caseList = new CaseList('container', {
    paginated: true,
    pageSize: 25,
    showPageSizeSelector: true,
    pageSizeOptions: [10, 25, 50, 100],
    onPageChange: (page, pageSize) => {
        console.log(`Page ${page} with ${pageSize} items`);
    }
});
```

### Infinite Scroll

```javascript
const caseList = new CaseList('container', {
    paginated: true,
    paginationType: 'infinite',
    pageSize: 20,
    loadMoreThreshold: 200 // pixels from bottom
});
```

## 🔗 HTMX Integration

### Server-Side Loading

```html
<!-- HTML template -->
<div id="htmx-case-list"
     data-component="case-list"
     data-htmx="true"
     hx-get="/api/cases"
     hx-trigger="load, caseUpdate from:body"
     hx-target="#case-list-content"
     hx-indicator="#loading-spinner">
    
    <div id="loading-spinner" class="htmx-indicator">
        Loading cases...
    </div>
    
    <div id="case-list-content">
        <!-- Cases will be loaded here -->
    </div>
</div>
```

### Search with HTMX

```javascript
const caseList = new CaseList('container', {
    htmx: {
        enabled: true,
        searchEndpoint: '/api/cases/search',
        filterEndpoint: '/api/cases/filter'
    },
    searchable: true,
    onSearch: (query) => {
        // HTMX request will be triggered automatically
        htmx.trigger('#case-list-container', 'search', {query});
    }
});
```

### Real-time Updates

```javascript
const caseList = new CaseList('container', {
    htmx: {
        enabled: true,
        realTimeUpdates: true,
        websocketUrl: 'ws://localhost:8000/ws/cases'
    }
});

// Listen for real-time case updates
document.addEventListener('caseUpdated', (event) => {
    caseList.updateCase(event.detail.caseId, event.detail.caseData);
});
```

## 🎯 Event System

### Built-in Events

```javascript
const caseList = new CaseList('container');

// Case selection events
caseList.addEventListener('caseSelect', (event) => {
    console.log('Case selected:', event.detail);
});

// Search events
caseList.addEventListener('search', (event) => {
    console.log('Search performed:', event.detail.query);
});

// Filter events
caseList.addEventListener('filter', (event) => {
    console.log('Filters applied:', event.detail.filters);
});

// Pagination events
caseList.addEventListener('pageChange', (event) => {
    console.log('Page changed:', event.detail.page);
});

// Data loading events
caseList.addEventListener('dataLoaded', (event) => {
    console.log('Data loaded:', event.detail.cases.length);
});
```

### Custom Events

```javascript
// Dispatch custom events
caseList.dispatchEvent('customEvent', {
    action: 'bulk-archive',
    caseIds: ['case-1', 'case-2', 'case-3']
});

// Listen for custom events
document.addEventListener('customEvent', (event) => {
    if (event.detail.action === 'bulk-archive') {
        // Handle bulk archive operation
    }
});
```

## 📱 Responsive Design

### Breakpoint Configuration

```javascript
const caseList = new CaseList('container', {
    responsive: {
        mobile: {
            layout: 'compact',
            pageSize: 10,
            showMetadata: false
        },
        tablet: {
            layout: 'card',
            pageSize: 15,
            showMetadata: true
        },
        desktop: {
            layout: 'table',
            pageSize: 25,
            showMetadata: true
        }
    }
});
```

### Mobile Optimizations

```javascript
const caseList = new CaseList('container', {
    mobile: {
        swipeActions: true,          // Enable swipe gestures
        pullToRefresh: true,         // Pull-to-refresh support
        virtualScrolling: true,      // Performance optimization
        touchOptimized: true         // Larger touch targets
    }
});
```

## 🎨 Theming & Styling

### Built-in Themes

```javascript
// Clinical theme - optimized for medical environments
const caseList = new CaseList('container', {
    theme: 'clinical',
    customClasses: {
        container: 'clinical-case-list',
        card: 'clinical-card',
        urgent: 'clinical-urgent'
    }
});

// Minimal theme - clean and simple
const caseList = new CaseList('container', {
    theme: 'minimal'
});
```

### Custom Styling

```css
/* Custom CSS for case list */
.custom-case-list {
    --case-card-bg: #ffffff;
    --case-card-border: #e5e7eb;
    --case-urgent-bg: #fef2f2;
    --case-urgent-border: #fca5a5;
}

.custom-case-list .case-card {
    background: var(--case-card-bg);
    border: 1px solid var(--case-card-border);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
}

.custom-case-list .case-card.urgent {
    background: var(--case-urgent-bg);
    border-color: var(--case-urgent-border);
}
```

## 🔧 Advanced Usage

### Batch Operations

```javascript
const caseList = new CaseList('container', {
    batchOperations: true,
    batchActions: [
        {
            id: 'archive',
            label: 'Archive Selected',
            icon: 'archive',
            action: (selectedCases) => {
                console.log('Archiving cases:', selectedCases);
            }
        },
        {
            id: 'assign',
            label: 'Assign Doctor',
            icon: 'user',
            action: (selectedCases) => {
                // Show doctor assignment modal
                showDoctorAssignmentModal(selectedCases);
            }
        }
    ]
});
```

### Custom Case Rendering

```javascript
const caseList = new CaseList('container', {
    customRenderer: (caseData) => {
        return `
            <div class="custom-case-card" data-case-id="${caseData.id}">
                <div class="case-header">
                    <h3>${caseData.title}</h3>
                    <span class="priority priority-${caseData.priority}">
                        ${caseData.priority.toUpperCase()}
                    </span>
                </div>
                <div class="case-content">
                    <p>${caseData.description}</p>
                    <div class="case-metadata">
                        <span>Patient: ${caseData.patientId}</span>
                        <span>Doctor: ${caseData.assignedTo}</span>
                        <span>Updated: ${formatDate(caseData.updatedAt)}</span>
                    </div>
                </div>
            </div>
        `;
    }
});
```

### Data Transformation

```javascript
const caseList = new CaseList('container', {
    dataTransformer: (rawData) => {
        // Transform server data to component format
        return rawData.map(item => ({
            id: item.case_id,
            title: item.case_title,
            description: item.case_description,
            patientId: item.patient_identifier,
            status: item.current_status,
            priority: item.priority_level,
            createdAt: item.created_timestamp,
            updatedAt: item.last_modified,
            assignedTo: item.assigned_doctor_name,
            metadata: {
                department: item.department_name,
                location: item.room_number,
                tags: item.case_tags || []
            }
        }));
    }
});
```

## 🧪 Testing

### Unit Testing

```javascript
// Test case list initialization
describe('CaseList Component', () => {
    let container;
    
    beforeEach(() => {
        container = document.createElement('div');
        container.id = 'test-container';
        document.body.appendChild(container);
    });
    
    afterEach(() => {
        document.body.removeChild(container);
    });
    
    test('should initialize with default options', () => {
        const caseList = new CaseList('test-container');
        expect(caseList.options.searchable).toBe(true);
        expect(caseList.options.filterable).toBe(true);
        expect(caseList.options.paginated).toBe(true);
    });
    
    test('should render cases correctly', () => {
        const testCases = [
            { id: '1', title: 'Test Case 1', status: 'active' },
            { id: '2', title: 'Test Case 2', status: 'pending' }
        ];
        
        const caseList = new CaseList('test-container', { cases: testCases });
        caseList.render();
        
        expect(container.querySelectorAll('.case-card')).toHaveLength(2);
    });
    
    test('should handle search correctly', async () => {
        const caseList = new CaseList('test-container', {
            cases: [
                { id: '1', title: 'Gastric Cancer', status: 'active' },
                { id: '2', title: 'Lung Cancer', status: 'pending' }
            ]
        });
        
        caseList.render();
        
        const searchResult = await caseList.search('gastric');
        expect(searchResult).toHaveLength(1);
        expect(searchResult[0].title).toBe('Gastric Cancer');
    });
});
```

### Integration Testing

```javascript
// Test HTMX integration
describe('CaseList HTMX Integration', () => {
    test('should load cases via HTMX', async () => {
        // Mock HTMX response
        const mockResponse = [
            { id: '1', title: 'Remote Case 1', status: 'active' }
        ];
        
        fetchMock.get('/api/cases', mockResponse);
        
        const caseList = new CaseList('test-container', {
            htmx: { enabled: true },
            endpoint: '/api/cases'
        });
        
        await caseList.loadData();
        
        expect(caseList.cases).toHaveLength(1);
        expect(caseList.cases[0].title).toBe('Remote Case 1');
    });
});
```

## 🚨 Error Handling

### Common Issues

```javascript
const caseList = new CaseList('container', {
    errorHandling: {
        onLoadError: (error) => {
            console.error('Failed to load cases:', error);
            showErrorMessage('Unable to load cases. Please try again.');
        },
        onSearchError: (error, query) => {
            console.error('Search failed:', error);
            showErrorMessage(`Search for "${query}" failed. Please try again.`);
        },
        onFilterError: (error, filters) => {
            console.error('Filter application failed:', error);
            resetFilters();
        },
        retryAttempts: 3,
        retryDelay: 1000
    }
});
```

### Error Recovery

```javascript
// Automatic error recovery
caseList.addEventListener('error', (event) => {
    const { type, error, context } = event.detail;
    
    switch (type) {
        case 'network':
            // Retry network requests
            setTimeout(() => caseList.retry(), 2000);
            break;
        case 'data':
            // Handle data format errors
            console.warn('Data format error:', error);
            caseList.showErrorState('Invalid data format');
            break;
        case 'render':
            // Handle rendering errors
            console.error('Render error:', error);
            caseList.fallbackRender();
            break;
    }
});
```

## 📊 Performance Optimization

### Virtual Scrolling

```javascript
const caseList = new CaseList('container', {
    virtualization: {
        enabled: true,
        itemHeight: 120,        // Fixed item height in pixels
        bufferSize: 10,         // Number of items to render outside viewport
        threshold: 1000         // Enable virtualization when > 1000 items
    }
});
```

### Lazy Loading

```javascript
const caseList = new CaseList('container', {
    lazyLoading: {
        enabled: true,
        pageSize: 50,
        preloadPages: 2,        // Preload next 2 pages
        loadingIndicator: true
    }
});
```

### Data Caching

```javascript
const caseList = new CaseList('container', {
    caching: {
        enabled: true,
        maxAge: 300000,         // 5 minutes
        maxItems: 1000,         // Cache up to 1000 cases
        strategy: 'lru'         // Least recently used eviction
    }
});
```

## 🔗 API Reference

### Methods

```javascript
const caseList = new CaseList(containerId, options);

// Data methods
caseList.loadData()                    // Load cases from endpoint
caseList.addCase(caseData)             // Add a new case
caseList.updateCase(id, caseData)      // Update existing case
caseList.removeCase(id)                // Remove a case
caseList.getCases()                    // Get all cases
caseList.getCase(id)                   // Get specific case

// Search methods
caseList.search(query)                 // Perform search
caseList.clearSearch()                 // Clear search results
caseList.getSearchResults()            // Get current search results

// Filter methods
caseList.applyFilter(filterName, value) // Apply single filter
caseList.applyFilters(filters)         // Apply multiple filters
caseList.clearFilters()                // Clear all filters
caseList.getActiveFilters()            // Get current filters

// Pagination methods
caseList.goToPage(page)                // Navigate to page
caseList.setPageSize(size)             // Change page size
caseList.getCurrentPage()              // Get current page
caseList.getTotalPages()               // Get total pages

// Selection methods
caseList.selectCase(id)                // Select a case
caseList.deselectCase(id)              // Deselect a case
caseList.selectAll()                   // Select all cases
caseList.deselectAll()                 // Deselect all cases
caseList.getSelectedCases()            // Get selected cases

// UI methods
caseList.render()                      // Render the component
caseList.refresh()                     // Refresh data and UI
caseList.destroy()                     // Clean up component
caseList.showLoading()                 // Show loading state
caseList.hideLoading()                 // Hide loading state
```

### Properties

```javascript
// Read-only properties
caseList.cases                         // Array of all cases
caseList.filteredCases                 // Array of filtered cases
caseList.selectedCases                 // Array of selected cases
caseList.currentPage                   // Current page number
caseList.totalPages                    // Total number of pages
caseList.isLoading                     // Loading state boolean
caseList.hasError                      // Error state boolean
```

## 📚 Examples

### Basic Medical Case List

```javascript
const medicalCaseList = new CaseList('medical-cases', {
    endpoint: '/api/medical-cases',
    searchFields: ['diagnosis', 'patientId', 'symptoms'],
    filters: {
        department: ['oncology', 'surgery', 'radiology'],
        urgency: ['low', 'medium', 'high', 'critical'],
        status: ['new', 'in-progress', 'review', 'completed']
    },
    layout: 'card',
    theme: 'clinical',
    onCaseSelect: (caseData) => {
        window.location.href = `/cases/${caseData.id}`;
    }
});

medicalCaseList.render();
```

### Research Case Database

```javascript
const researchCaseList = new CaseList('research-cases', {
    endpoint: '/api/research-cases',
    layout: 'table',
    columns: ['id', 'title', 'category', 'lastModified', 'status'],
    batchOperations: true,
    batchActions: [
        {
            id: 'export',
            label: 'Export to CSV',
            action: (cases) => exportToCsv(cases)
        }
    ],
    filters: {
        category: ['gastric', 'lung', 'liver', 'pancreatic'],
        dateRange: true,
        dataQuality: ['complete', 'partial', 'incomplete']
    }
});
```

## 🎯 Best Practices

### Performance
- Use virtualization for large datasets (1000+ items)
- Implement proper caching strategies
- Debounce search inputs (300-500ms)
- Use lazy loading for images and metadata

### Accessibility
- Ensure keyboard navigation works
- Provide proper ARIA labels
- Use semantic HTML structure
- Test with screen readers

### User Experience
- Show loading states during data fetching
- Provide clear error messages
- Implement progressive disclosure
- Use consistent visual hierarchy

### Data Management
- Validate data structure before rendering
- Handle missing or malformed data gracefully
- Implement proper error boundaries
- Use immutable data patterns

## 🔍 Troubleshooting

### Common Issues

**Cases not loading:**
```javascript
// Check endpoint configuration
console.log('Endpoint:', caseList.options.endpoint);

// Verify data structure
caseList.addEventListener('dataLoaded', (event) => {
    console.log('Loaded data:', event.detail);
});
```

**Search not working:**
```javascript
// Verify search fields
console.log('Search fields:', caseList.options.searchFields);

// Check search debounce
caseList.options.searchDebounce = 0; // Remove debounce for testing
```

**Filters not applying:**
```javascript
// Check filter configuration
console.log('Filter config:', caseList.options.filters);

// Listen for filter events
caseList.addEventListener('filter', (event) => {
    console.log('Applied filters:', event.detail);
});
```

### Debug Mode

```javascript
const caseList = new CaseList('container', {
    debug: true,  // Enable debug logging
    logLevel: 'info'  // 'error', 'warn', 'info', 'debug'
});
```

## 📖 Related Documentation

- **[Component Overview](./README.md)** - All UI components
- **[CaseDetail Component](./case-detail.md)** - Detailed case view
- **[API Documentation](../api/cases.md)** - Cases API endpoints
- **[HTMX Integration Guide](../examples/htmx-integration.md)** - HTMX patterns
- **[Testing Guide](../guides/testing.md)** - Component testing strategies

---

**Last Updated:** January 2025  
**Version:** 1.0.0  
**Status:** Production Ready
