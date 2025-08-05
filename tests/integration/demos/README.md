# Integration Demonstrations

This directory contains demonstration scripts that showcase the platform's capabilities and integrations.

## Available Demonstrations

### `demonstrate_integration.py`
Comprehensive demonstration of the Universal Research Module integration with the Surgify platform. Shows:

- Backward compatibility preservation
- Enhanced research capabilities
- API integrations
- Data analysis features
- Optional research enhancements

**Usage:**
```bash
cd tests/integration/demos
PYTHONPATH=/workspaces/yaz/src python demonstrate_integration.py
```

## Running Demonstrations

All demonstration scripts should be run from this directory with the proper Python path:

```bash
cd /workspaces/yaz/tests/integration/demos
PYTHONPATH=/workspaces/yaz/src python <script_name>.py
```

This ensures proper import resolution for the Surgify platform modules.
