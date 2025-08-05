# Surgify Platform Documentation

> **Version:** 1.0.0  
> **Last Updated:** August 5, 2025  
> **Status:** Active Development

## 📚 Documentation Overview

Welcome to the comprehensive documentation for the Surgify Platform - a gastric oncology-surgery decision support system. This documentation is designed for **reproducibility**, **modularity**, and **maintainability**.

## 🏗️ Documentation Structure

### 📖 Core Documentation
- **[Getting Started](./guides/getting-started.md)** - Quick setup and first steps
- **[Architecture Overview](./architecture/README.md)** - System design and patterns
- **[Installation Guide](./guides/installation.md)** - Complete setup instructions
- **[Configuration](./guides/configuration.md)** - Environment and settings

### 🎨 Component Library
- **[Component Overview](./components/README.md)** - All UI components
- **[DomainSelector](./components/domain-selector.md)** - Medical domain selection
- **[CaseList](./components/case-list.md)** - Case management interface
- **[CaseDetail](./components/case-detail.md)** - Detailed case view
- **[NotificationBadge](./components/notification-badge.md)** - Notification system
- **[ThemeToggle](./components/theme-toggle.md)** - Theme switching

### 🔌 API Documentation
- **[API Overview](./api/README.md)** - REST API documentation
- **[Authentication](./api/authentication.md)** - Auth endpoints and flow
- **[Cases API](./api/cases.md)** - Case management endpoints
- **[Users API](./api/users.md)** - User management
- **[Analytics API](./api/analytics.md)** - Data analytics endpoints

### 🛠️ Development Guides
- **[Development Setup](./guides/development.md)** - Local development environment
- **[Component Development](./guides/component-development.md)** - Creating new components
- **[Testing Guide](./guides/testing.md)** - Testing strategies and tools
- **[Deployment](./guides/deployment.md)** - Production deployment
- **[Contributing](./guides/contributing.md)** - Contribution guidelines

### 📋 Examples & Tutorials
- **[Basic Usage](./examples/basic-usage.md)** - Simple implementation examples
- **[Advanced Integration](./examples/advanced-integration.md)** - Complex scenarios
- **[HTMX Integration](./examples/htmx-integration.md)** - Dynamic content loading
- **[Custom Components](./examples/custom-components.md)** - Building extensions

## 🎯 Quick Navigation

### For Developers
1. **New to the project?** → [Getting Started](./guides/getting-started.md)
2. **Setting up locally?** → [Development Setup](./guides/development.md)
3. **Building components?** → [Component Development](./guides/component-development.md)
4. **Need API docs?** → [API Overview](./api/README.md)

### For Users
1. **Using components?** → [Component Overview](./components/README.md)
2. **Need examples?** → [Basic Usage](./examples/basic-usage.md)
3. **Customizing themes?** → [ThemeToggle](./components/theme-toggle.md)
4. **Integration help?** → [HTMX Integration](./examples/htmx-integration.md)

### For Administrators
1. **Installation?** → [Installation Guide](./guides/installation.md)
2. **Configuration?** → [Configuration](./guides/configuration.md)
3. **Deployment?** → [Deployment](./guides/deployment.md)
4. **Architecture?** → [Architecture Overview](./architecture/README.md)

## 🔍 Search & Index

### Components Index
| Component | Description | Size | Dependencies |
|-----------|-------------|------|--------------|
| [DomainSelector](./components/domain-selector.md) | Medical domain dropdown | 6.5KB | None |
| [CaseList](./components/case-list.md) | Case management list | 12KB | None |
| [CaseDetail](./components/case-detail.md) | Detailed case view | 15KB | None |
| [NotificationBadge](./components/notification-badge.md) | Notification badges | 8KB | None |
| [ThemeToggle](./components/theme-toggle.md) | Theme switching | 10KB | None |

### API Endpoints Index
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/cases` | GET | List cases | Yes |
| `/api/cases/{id}` | GET | Get case details | Yes |
| `/api/auth/login` | POST | User authentication | No |
| `/api/users/profile` | GET | User profile | Yes |
| `/api/analytics/dashboard` | GET | Dashboard data | Yes |

### File Structure Index
```
surgify/
├── src/surgify/              # Main application code
│   ├── ui/                   # User interface components
│   ├── api/                  # API endpoints
│   ├── core/                 # Core business logic
│   └── modules/              # Feature modules
├── tests/                    # Test suites
├── docs/                     # This documentation
├── data/                     # Data management
└── scripts/                  # Utility scripts
```

## 📊 Documentation Metrics

- **Components Documented**: 5/5 ✅
- **API Endpoints Documented**: 15+ ✅
- **Examples Provided**: 20+ ✅
- **Code Coverage**: 85% ✅
- **Last Review**: August 5, 2025 ✅

## 🚀 Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd surgify

# Install dependencies
pip install -r requirements.txt
npm install

# Start development server
make dev

# View documentation
cd docs && python -m http.server 8080
```

## 🔄 Documentation Maintenance

### Update Schedule
- **Weekly**: Component documentation review
- **Monthly**: API documentation sync
- **Quarterly**: Architecture review
- **Per Release**: Version updates and new features

### Contribution Process
1. **Create/Update** documentation files
2. **Test** examples and code snippets
3. **Update** indexes and cross-references
4. **Submit** pull request with documentation changes

## 📞 Support & Contact

- **Issues**: Create GitHub issues for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Suggest improvements via pull requests
- **Email**: contact@surgify-platform.com

## 📄 License

This documentation is part of the Surgify Platform and follows the same license terms.

---

**📌 Bookmark this page** - It serves as your central hub for all Surgify Platform documentation.

**🔍 Need something specific?** Use the search functionality or browse the structured sections above.

**💡 Missing something?** Contribute to the documentation by submitting a pull request!
