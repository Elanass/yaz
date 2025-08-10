"""
Command-line interface for the orchestration system.
"""
import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any
from .health import get_provider, health_check, switch_provider
from .utils import load_yaml_file, save_yaml_file, get_backup_path, ProviderError

logger = logging.getLogger(__name__)

def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def cmd_init(args):
    """Initialize orchestration system."""
    try:
        provider = get_provider(args.project)
        if provider.ensure_host():
            print(f"✓ Orchestration system initialized with {provider.__class__.__name__}")
            return 0
        else:
            print("✗ Failed to initialize orchestration system")
            return 1
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return 1

def cmd_apply(args):
    """Apply a plan to create/update instances."""
    try:
        plan_path = Path(args.plan)
        if not plan_path.exists():
            print(f"✗ Plan file not found: {plan_path}")
            return 1
        
        plan = load_yaml_file(plan_path)
        provider = get_provider(args.project)
        
        # Ensure host is ready
        if not provider.ensure_host():
            print("✗ Failed to prepare host")
            return 1
        
        instances_config = plan.get("instances", {})
        if not instances_config:
            print("✗ No instances defined in plan")
            return 1
        
        success_count = 0
        for instance_name, config in instances_config.items():
            try:
                print(f"Creating instance: {instance_name}")
                
                # Check if instance already exists
                existing = provider.get_instance(instance_name)
                if existing:
                    print(f"  Instance {instance_name} already exists, skipping")
                    continue
                
                instance = provider.create_instance(instance_name, config)
                print(f"  ✓ Created {instance_name} - IP: {instance.ip_address}")
                success_count += 1
                
            except Exception as e:
                print(f"  ✗ Failed to create {instance_name}: {e}")
        
        print(f"\nCreated {success_count}/{len(instances_config)} instances")
        return 0 if success_count > 0 else 1
        
    except Exception as e:
        print(f"✗ Apply failed: {e}")
        return 1

def cmd_destroy(args):
    """Destroy instances from a plan."""
    try:
        provider = get_provider(args.project)
        
        if args.plan:
            plan_path = Path(args.plan)
            if not plan_path.exists():
                print(f"✗ Plan file not found: {plan_path}")
                return 1
            
            plan = load_yaml_file(plan_path)
            instance_names = list(plan.get("instances", {}).keys())
        else:
            # Destroy all instances
            instances = provider.list_instances()
            instance_names = [inst.name for inst in instances]
        
        if not instance_names:
            print("No instances to destroy")
            return 0
        
        if not args.force:
            print(f"About to destroy {len(instance_names)} instances:")
            for name in instance_names:
                print(f"  - {name}")
            
            response = input("Continue? (y/N): ")
            if response.lower() != 'y':
                print("Cancelled")
                return 0
        
        success_count = 0
        for instance_name in instance_names:
            try:
                print(f"Destroying instance: {instance_name}")
                if provider.destroy_instance(instance_name):
                    print(f"  ✓ Destroyed {instance_name}")
                    success_count += 1
                else:
                    print(f"  ✗ Failed to destroy {instance_name}")
            except Exception as e:
                print(f"  ✗ Error destroying {instance_name}: {e}")
        
        print(f"\nDestroyed {success_count}/{len(instance_names)} instances")
        return 0
        
    except Exception as e:
        print(f"✗ Destroy failed: {e}")
        return 1

def cmd_status(args):
    """Show status of instances and system."""
    try:
        provider = get_provider(args.project)
        
        # Show provider info
        health = health_check()
        print(f"Active Provider: {provider.__class__.__name__}")
        print(f"Overall Status: {health.get('overall_status', 'unknown')}")
        
        if health.get('recommendations'):
            print("\nRecommendations:")
            for rec in health['recommendations']:
                print(f"  • {rec}")
        
        # Show instances
        instances = provider.list_instances()
        if not instances:
            print("\nNo instances found")
            return 0
        
        print(f"\nInstances ({len(instances)}):")
        print(f"{'Name':<20} {'Status':<12} {'IP Address':<15} {'Memory':<10}")
        print("-" * 60)
        
        for instance in instances:
            memory_str = f"{instance.memory_usage // (1024**2)}MB" if instance.memory_usage else "N/A"
            print(f"{instance.name:<20} {instance.status.value:<12} {instance.ip_address or 'N/A':<15} {memory_str:<10}")
        
        return 0
        
    except Exception as e:
        print(f"✗ Status check failed: {e}")
        return 1

def cmd_exec(args):
    """Execute command in instance."""
    try:
        provider = get_provider(args.project)
        
        output = provider.exec_command(args.instance, args.command)
        print(output)
        return 0
        
    except Exception as e:
        print(f"✗ Command execution failed: {e}")
        return 1

def cmd_snapshot(args):
    """Create instance snapshot."""
    try:
        provider = get_provider(args.project)
        
        if provider.snapshot_instance(args.instance, args.name):
            print(f"✓ Snapshot '{args.name}' created for {args.instance}")
            return 0
        else:
            print(f"✗ Failed to create snapshot")
            return 1
            
    except Exception as e:
        print(f"✗ Snapshot failed: {e}")
        return 1

def cmd_health(args):
    """Show detailed health information."""
    try:
        health = health_check()
        
        if args.json:
            print(json.dumps(health, indent=2))
        else:
            print(f"Overall Status: {health.get('overall_status', 'unknown')}")
            print(f"Active Provider: {health.get('active_provider', 'none')}")
            
            print("\nProvider Details:")
            for name, details in health.get("providers", {}).items():
                status = "✓" if details.get("available") else "✗"
                version = details.get("version", "unknown")
                instances = details.get("instances", 0)
                print(f"  {status} {name}: {version} ({instances} instances)")
                
                errors = details.get("errors", [])
                if errors:
                    for error in errors:
                        print(f"    Error: {error}")
            
            recommendations = health.get("recommendations", [])
            if recommendations:
                print("\nRecommendations:")
                for rec in recommendations:
                    print(f"  • {rec}")
        
        return 0
        
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return 1

def cmd_switch(args):
    """Switch active provider."""
    try:
        if switch_provider(args.provider):
            print(f"✓ Switched to {args.provider}")
            return 0
        else:
            print(f"✗ Failed to switch to {args.provider}")
            return 1
            
    except Exception as e:
        print(f"✗ Provider switch failed: {e}")
        return 1

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="YAZ Orchestration CLI")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-p", "--project", default="yaz", help="Project name")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Init command
    parser_init = subparsers.add_parser("init", help="Initialize orchestration system")
    parser_init.set_defaults(func=cmd_init)
    
    # Apply command
    parser_apply = subparsers.add_parser("apply", help="Apply plan to create instances")
    parser_apply.add_argument("plan", help="Path to plan YAML file")
    parser_apply.set_defaults(func=cmd_apply)
    
    # Destroy command
    parser_destroy = subparsers.add_parser("destroy", help="Destroy instances")
    parser_destroy.add_argument("--plan", help="Path to plan YAML file (optional)")
    parser_destroy.add_argument("--force", action="store_true", help="Skip confirmation")
    parser_destroy.set_defaults(func=cmd_destroy)
    
    # Status command
    parser_status = subparsers.add_parser("status", help="Show system status")
    parser_status.set_defaults(func=cmd_status)
    
    # Exec command
    parser_exec = subparsers.add_parser("exec", help="Execute command in instance")
    parser_exec.add_argument("instance", help="Instance name")
    parser_exec.add_argument("command", help="Command to execute")
    parser_exec.set_defaults(func=cmd_exec)
    
    # Snapshot command
    parser_snapshot = subparsers.add_parser("snapshot", help="Create instance snapshot")
    parser_snapshot.add_argument("instance", help="Instance name")
    parser_snapshot.add_argument("name", help="Snapshot name")
    parser_snapshot.set_defaults(func=cmd_snapshot)
    
    # Health command
    parser_health = subparsers.add_parser("health", help="Show health information")
    parser_health.add_argument("--json", action="store_true", help="Output as JSON")
    parser_health.set_defaults(func=cmd_health)
    
    # Switch command
    parser_switch = subparsers.add_parser("switch", help="Switch active provider")
    parser_switch.add_argument("provider", choices=["incus", "multipass"], help="Provider to switch to")
    parser_switch.set_defaults(func=cmd_switch)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    setup_logging(args.verbose)
    
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\nCancelled")
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
