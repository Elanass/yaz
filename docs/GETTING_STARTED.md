# Getting Started - YAZ Healthcare Platform

**⏱️ Target: Get fully running in ≤15 minutes**

## Quick Start

### Prerequisites (2 minutes)
```bash
# Check requirements
python --version  # Python 3.11+
podman --version  # or docker
git --version
```

### One-Command Setup (5 minutes)
```bash
# Clone and setup
git clone <repo-url> yaz-platform
cd yaz-platform
make setup  # Installs deps, creates .env, sets up pre-commit
```

### Start Development Stack (3 minutes)
```bash
# Start full healthcare stack
make dev
# This starts:
# - FastAPI server (localhost:8000)
# - PostgreSQL database
# - Redis cache  
# - Orthanc PACS (localhost:8042)
# - OHIF viewer (localhost:3000)
# - HAPI FHIR server (localhost:8080)
```

### Verify Installation (2 minutes)
```bash
# Run health checks
make test-canary

# Check endpoints
curl http://localhost:8000/health
curl http://localhost:8000/fhir/metadata
curl http://localhost:8000/imaging/studies
```

### Access Applications (1 minute)
- **Platform Dashboard**: http://localhost:8000
- **Surge (Surgery)**: http://localhost:8000/surge  
- **Clinica (Clinical)**: http://localhost:8000/clinica
- **API Docs**: http://localhost:8000/docs
- **OHIF Viewer**: http://localhost:3000
- **Orthanc PACS**: http://localhost:8042

### Stop Stack (1 minute)
```bash
make stop  # Gracefully stops all services
```

---

## Development Workflow

### Daily Development
```bash
# Start coding
make dev

# Run tests while developing
make test-watch

# Lint and format
make lint
make format

# Type check
make typecheck
```

### Database Operations
```bash
# Run migrations
make migrate

# Seed test data
make seed

# Reset database
make db-reset
```

### Component Development
```bash
# Start component demo
make dev-components
# Visit: http://localhost:8000/demo/components
```

---

## Project Structure

```
yaz/
├── apps/                    # Domain applications
│   ├── external/surge/      # Surgery analytics
│   └── internal/clinica/    # Clinical operations
├── infra/                   # Infrastructure clients
│   ├── fhir_client.py      # FHIR integration
│   └── orthanc_client.py   # PACS integration  
├── api/routers/            # API route handlers
│   ├── fhir_proxy.py      # /fhir/* endpoints
│   └── imaging.py         # /imaging/* endpoints
├── src/shared/             # Shared core
│   ├── config/            # Configuration
│   └── database/          # DB setup
├── tests/                  # Test suites
├── docs/                   # Documentation
└── scripts/               # Utility scripts
```

---

## Configuration

### Environment Setup
```bash
# Copy example config
cp .env.example .env

# Edit configuration
nano .env
```

### Key Environment Variables
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/yaz

# FHIR Integration  
FHIR_BASE_URL=http://localhost:8080/fhir
FHIR_TOKEN=your-token

# Imaging
ORTHANC_URL=http://localhost:8042
ORTHANC_USER=orthanc
ORTHANC_PASS=orthanc

# SMART on FHIR
SMART_CLIENT_ID=demo-client
SMART_CLIENT_SECRET=demo-secret
```

---

## Common Tasks

### Adding a New Domain
```bash
# Use scaffolding script
python scripts/scaffold_domain.py --name NewDomain

# This creates:
# - apps/internal/newdomain/
# - API routers
# - Database models
# - Tests
```

### Adding FHIR Resources
```python
# In your domain code
from infra.fhir_client import FHIRClient

client = FHIRClient()
patient = await client.get_patient("patient-123")
```

### Adding UI Components
```javascript
// Create new component
class MyComponent extends BaseComponent {
    constructor(containerId, options) {
        super(containerId, options);
    }
    
    render() {
        // Component logic
    }
}
```

---

## Troubleshooting

### Common Issues

**Port conflicts**
```bash
# Check what's using ports
lsof -i :8000
make ports-check
```

**Database connection**
```bash
# Check database status
make db-status

# Reset database
make db-reset
```

**FHIR backend not responding**
```bash
# Check FHIR server
curl http://localhost:8080/fhir/metadata

# Restart FHIR stack
make restart-fhir
```

**Build failures**
```bash
# Clean build
make clean
make setup
```

### Debug Mode
```bash
# Start with debug logging
DEBUG=true make dev

# Check logs
make logs
```

### Reset Everything
```bash
# Nuclear option - fresh start
make clean-all
make setup
make dev
```

---

## Next Steps

### For New Developers
1. **Read Architecture**: [ARCHITECTURE.md](./ARCHITECTURE.md)
2. **Explore APIs**: Visit http://localhost:8000/docs
3. **Run Tests**: `make test`
4. **Check Examples**: `docs/examples/`

### For Healthcare Integrators  
1. **FHIR Setup**: [docs/integrations/fhir.md](./docs/integrations/fhir.md)
2. **Imaging Setup**: [docs/integrations/imaging.md](./docs/integrations/imaging.md)
3. **SMART Apps**: [docs/integrations/smart.md](./docs/integrations/smart.md)

### For Production Deployment
1. **Operations Guide**: [OPERATIONS.md](./OPERATIONS.md)
2. **Security Setup**: [SECURITY.md](./SECURITY.md)
3. **Monitoring**: [docs/monitoring/](./docs/monitoring/)

---

## Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions  
- **Documentation**: `docs/` directory
- **Examples**: `docs/examples/`

**🎉 You're ready to build healthcare applications!**
