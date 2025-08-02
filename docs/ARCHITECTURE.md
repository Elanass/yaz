# Gastric ADCI Platform Architecture

## Overview
State-of-the-art surgery decision support platform built with modern software engineering practices.

## Architecture Patterns
- **Clean Architecture**: Separation of concerns with clear dependency directions
- **Dependency Injection**: Loose coupling through DI container
- **Repository Pattern**: Data access abstraction
- **Strategy Pattern**: Algorithm selection (deployment modes, validation, etc.)
- **Observer Pattern**: Real-time updates and notifications
- **Command Pattern**: Form handling and API operations

## Layer Structure
```
┌─────────────────────────────────────────┐
│           Presentation Layer            │
│        (FastAPI routes, Web UI)         │
├─────────────────────────────────────────┤
│           Application Layer             │
│         (Services, Use Cases)           │
├─────────────────────────────────────────┤
│            Domain Layer                 │
│        (Models, Interfaces)             │
├─────────────────────────────────────────┤
│         Infrastructure Layer            │
│     (Database, External APIs)           │
└─────────────────────────────────────────┘
```

## Key Components
- **Unified Configuration**: Single source of truth for all settings
- **Dependency Injection**: Clean service management
- **Unified Utilities**: DRY JavaScript utilities
- **Type Safety**: Full type annotations in Python
- **Error Handling**: Consistent error management
- **Logging**: Structured logging with proper formatting

## Design Principles
- **DRY (Don't Repeat Yourself)**: Eliminated code duplication
- **SOLID Principles**: Single responsibility, open/closed, etc.
- **Separation of Concerns**: Clear module boundaries
- **Testability**: Easy to test components
- **Maintainability**: Clean, readable code
