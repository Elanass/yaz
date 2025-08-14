# Surge Platform - Clean Directory Structure

## 🎯 Root Directory (Essential Files Only)

```
/workspaces/yaz/
├── .env                      # Active environment (local only)
├── .gitignore               # Git ignore patterns
├── .pre-commit-config.yaml  # Pre-commit hooks
├── CONTRIBUTING.md          # Contribution guidelines
├── Makefile                 # Build automation
├── README.md                # Project overview
├── main.py                  # Application entry point
├── pyproject.toml           # Python project configuration
├── requirements.txt         # Python dependencies
│
├── .devcontainer/           # Development container config
├── .github/                 # GitHub workflows and templates
├── .venv/                   # Python virtual environment (local)
└── .vscode/                 # VS Code workspace settings
```

## 📁 Organized Directories

```
├── config/                  # 🔧 Configuration files
│   ├── alembic.ini         # Database migration config
│   ├── logging.ini         # Logging configuration
│   ├── mypy.ini            # Type checking config
│   ├── ruff.toml           # Linting configuration
│   └── tasks.yaml          # Task definitions
│
├── deployment/              # 🚀 Deployment configurations
│   ├── docker-compose.yml  # Development containers
│   ├── docker-compose.prod.yml # Production containers
│   ├── Dockerfile          # Container build instructions
│   ├── .dockerignore       # Docker ignore patterns
│   ├── .env.example        # Environment template
│   ├── .env.production     # Production environment template
│   └── .env.chat.example   # Chat service template
│
├── data/                    # 📊 Runtime data
│   ├── database/           # Database files
│   ├── logs/               # Application logs
│   ├── outputs/            # Generated outputs
│   ├── uploads/            # User uploads
│   ├── model/              # AI/ML models
│   └── backups/            # Database backups
│
├── infra/                   # 🏗️ Infrastructure
│   ├── network/            # Network configurations
│   └── n8n/               # Workflow automation
│
├── src/surge/               # 💻 Main application code
│   └── apps/               # Modular applications
│
├── scripts/                # 🛠️ Utility scripts
├── docs/                   # 📚 Documentation
├── tests/                  # 🧪 Test suites
└── tools/                  # 🔨 Development tools
```

## ✨ Benefits of This Structure

1. **Clean Root**: Only essential files visible at top level
2. **Logical Grouping**: Related files organized together
3. **Clear Separation**: Configuration, deployment, and runtime data separated
4. **Development Friendly**: Easy to find and manage files
5. **Production Ready**: Clear deployment and configuration structure
