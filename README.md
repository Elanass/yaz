# YAZ Platform

A lean, modern healthcare platform built with FastAPI and modular architecture.

## Project Structure

```
/workspaces/yaz/
├── apps/           # All application modules (core, surge, move, clinica, educa, insura)
├── config/         # All configuration files
├── data/           # All data, logs, uploads, databases
├── infra/          # Infrastructure, networking, shared utilities  
├── scripts/        # Utility scripts
├── tests/          # Test suite
├── docs/           # Documentation
├── main.py         # Main entry point
├── pyproject.toml  # Python configuration
├── requirements.txt # Dependencies
├── Dockerfile      # Container config
└── docker-compose.yml # Orchestration
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the platform:**
   ```bash
   python main.py
   ```

3. **Run with Docker:**
   ```bash
   docker-compose up
   ```

## Applications

- **core** - Core platform services and management
- **surge** - Surgery analytics and case management
- **move** - Medical logistics and supply chain
- **clinica** - Integrated clinical care
- **educa** - Medical education platform
- **insura** - Insurance and billing management

## Development

- Configuration files are in `config/`
- All data, logs, and uploads are in `data/`
- Infrastructure utilities are in `infra/`
- Scripts and tools are in `scripts/`
- Tests are in `tests/`
- Documentation is in `docs/`

For detailed documentation, see `docs/README.md`.
