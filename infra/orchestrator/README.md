# YAZ Orchestration System

A lean, scriptable orchestration system with Incus primary and Multipass fallback for multi-VM and multi-container environments.

## Features

- **Multi-Provider Support**: Incus (primary) with Multipass fallback
- **Instance Lifecycle**: Create, start, stop, destroy with idempotent operations
- **Cloud-Init Integration**: Automated instance configuration
- **Health Monitoring**: Comprehensive health checks and auto-recovery
- **Metadata & Tagging**: Flexible instance metadata system
- **Snapshots & Backup**: Instance state management
- **File Operations**: Push/pull files to/from instances
- **CLI Interface**: Comprehensive command-line tool
- **Makefile Integration**: Convenient development targets

## Quick Start

### 1. Initialize the System

```bash
# Initialize orchestration (auto-detects and installs Incus or Multipass)
make incus.init

# Or use CLI directly
python -m infra.orchestrator.cli init
```

### 2. Apply Demo Environment

```bash
# Deploy the demo environment (3 instances: gateway, worker, storage)
make env.apply

# Check status
make env.status
```

### 3. Manage Environment

```bash
# Health check
make env.health

# Create snapshots
make env.snapshot

# Destroy environment
make env.destroy
```

## CLI Usage

The orchestration system provides a comprehensive CLI:

```bash
# Initialize system
python -m infra.orchestrator.cli init

# Apply a plan
python -m infra.orchestrator.cli apply plans/demo.yaml

# Show status
python -m infra.orchestrator.cli status

# Execute commands
python -m infra.orchestrator.cli exec yaz-gateway "uptime"

# Create snapshots
python -m infra.orchestrator.cli snapshot yaz-gateway backup-001

# Health checks
python -m infra.orchestrator.cli health --json

# Switch providers
python -m infra.orchestrator.cli switch multipass

# Destroy instances
python -m infra.orchestrator.cli destroy --plan plans/demo.yaml
```

## Plans Configuration

Plans are YAML files that define infrastructure as code:

```yaml
instances:
  yaz-gateway:
    image: "ubuntu:22.04"
    type: "container"
    memory: "1GB"
    cpus: 2
    disk: "10GB"
    metadata:
      role: "gateway"
      environment: "demo"
    network:
      type: "bridge"
      ipv4: "auto"
    cloud_init: |
      #cloud-config
      users:
        - name: yaz
          groups: sudo
          shell: /bin/bash
          sudo: ALL=(ALL) NOPASSWD:ALL
      packages:
        - nginx
      runcmd:
        - systemctl enable nginx
        - systemctl start nginx

profiles:
  default:
    description: "Default profile for YAZ instances"
    config:
      limits.cpu: "2"
      limits.memory: "2GB"
    devices:
      root:
        path: "/"
        pool: "incus-pool"
        type: "disk"
```

## Provider Support

### Incus (Primary)
- Full container and VM support
- Advanced networking and storage
- Snapshots and live migration
- Resource limits and profiles
- Project isolation

### Multipass (Fallback)
- VM-only support
- Cloud-init integration
- Bridged networking
- Basic resource allocation
- Limited snapshot support (exports)

## Architecture

```
infra/orchestrator/
├── __init__.py           # Main module exports
├── cli.py               # Command-line interface
├── health.py            # Health checks and provider management
├── utils.py             # Utility functions and error classes
├── providers/
│   ├── __init__.py      # Provider exports
│   ├── base.py          # Abstract provider interface
│   ├── incus.py         # Incus provider implementation
│   └── multipass.py     # Multipass fallback provider
├── plans/
│   └── demo.yaml        # Example infrastructure plan
└── assets/
    └── cloudinit/
        ├── base-user.yaml   # Base user setup
        └── surge-node.yaml  # Surge processing node
```

## Makefile Targets

### Core Operations
- `make incus.init` - Initialize orchestration system
- `make env.apply` - Apply demo environment plan
- `make env.destroy` - Destroy environment instances
- `make env.status` - Show environment status
- `make env.health` - Check orchestration health

### Management
- `make env.snapshot` - Create environment snapshots
- `make env.start` - Start all instances
- `make env.stop` - Stop all instances
- `make env.logs` - Show instance logs

## Error Handling

The system includes comprehensive error handling:

- **ProviderError**: Base provider operation errors
- **InstanceNotFoundError**: Missing instance errors
- **ProviderUnavailableError**: Provider not available
- **HealthCheckError**: Health check failures

## Health Monitoring

The health system provides:

- **Provider availability** checks
- **Resource utilization** monitoring
- **Instance status** tracking
- **Automatic failover** to backup providers
- **Recovery recommendations**

## Cloud-Init Integration

The system supports full cloud-init configuration:

```yaml
cloud_init: |
  #cloud-config
  users:
    - name: yaz
      groups: sudo
      shell: /bin/bash
      sudo: ALL=(ALL) NOPASSWD:ALL
  packages:
    - docker.io
    - python3
  runcmd:
    - systemctl enable docker
    - systemctl start docker
```

## Metadata and Tagging

Instances support flexible metadata:

```yaml
metadata:
  role: "worker"
  environment: "production"
  version: "1.0"
  cost_center: "engineering"
```

## Backup and Snapshots

- **Incus**: Native snapshot support with instant creation
- **Multipass**: Export-based backup system
- **Automated**: Snapshot all instances with timestamped names
- **Storage**: Backups stored in `/var/backups/yaz/`

## Network Configuration

### Incus
- Bridge networks with DHCP
- Custom IP ranges
- Port forwarding
- Network isolation

### Multipass
- Bridged networking
- Host network access
- Limited configuration options

## Security

- Cloud-init SSH key injection
- Sudo configuration management
- Network isolation
- Resource limits enforcement
- Metadata access controls

## Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   # Add user to incus-admin group
   sudo usermod -aG incus-admin $USER
   # Log out and back in
   ```

2. **Incus Not Available**
   ```bash
   # Install Incus
   sudo snap install incus --classic
   # Initialize
   sudo incus admin init --minimal
   ```

3. **Provider Switch**
   ```bash
   # Force switch to Multipass
   python -m infra.orchestrator.cli switch multipass
   ```

### Health Check
```bash
# Detailed health information
make env.health

# JSON output for scripting
python -m infra.orchestrator.cli health --json
```

### Logs
```bash
# System logs
make env.logs

# Specific instance
python -m infra.orchestrator.cli exec yaz-gateway "journalctl -n 50"
```

## Requirements

- **OS**: Ubuntu 22.04+ (with KVM support for VMs)
- **Python**: 3.8+
- **Providers**: Incus (preferred) or Multipass
- **Optional**: PyYAML for YAML support (falls back to JSON)

## Installation

The system is self-contained within the YAZ platform. Providers are installed automatically during initialization.

## License

Part of the YAZ Platform - see main project license.
