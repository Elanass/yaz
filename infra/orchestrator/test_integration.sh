#!/bin/bash
# Integration test script for YAZ Orchestration System

set -e

echo "🧪 YAZ Orchestration System - Integration Test"
echo "=============================================="

# Test 1: Module imports
echo "📦 Testing module imports..."
python -c "import infra.orchestrator; print('✓ Main module imports successfully')"
python -c "from infra.orchestrator import get_provider, health_check; print('✓ Core functions accessible')"
python -c "from infra.orchestrator.providers import BaseProvider, IncusProvider, MultipassProvider; print('✓ All providers importable')"

# Test 2: CLI help
echo ""
echo "📋 Testing CLI interface..."
python -m infra.orchestrator.cli --help > /dev/null && echo "✓ CLI help works"

# Test 3: Health check
echo ""
echo "🏥 Testing health check system..."
python -m infra.orchestrator.cli health --json > /tmp/health.json
if [ -f /tmp/health.json ]; then
    echo "✓ Health check produces JSON output"
    # Check if it contains expected fields
    if grep -q "overall_status" /tmp/health.json && grep -q "providers" /tmp/health.json; then
        echo "✓ Health check output format is correct"
    else
        echo "✗ Health check output format is incorrect"
        exit 1
    fi
else
    echo "✗ Health check failed to produce output"
    exit 1
fi

# Test 4: Provider error handling
echo ""
echo "🔄 Testing provider error handling..."
if python -m infra.orchestrator.cli status 2>/dev/null; then
    echo "✗ Expected status to fail with no providers"
    exit 1
else
    echo "✓ Status correctly fails when no providers available"
fi

# Test 5: Plan validation
echo ""
echo "📋 Testing plan file validation..."
if [ -f "infra/orchestrator/plans/demo.yaml" ]; then
    echo "✓ Demo plan file exists"
    # Test YAML parsing
    python -c "
import yaml
import sys
try:
    with open('infra/orchestrator/plans/demo.yaml', 'r') as f:
        plan = yaml.safe_load(f)
    if 'instances' in plan:
        print('✓ Demo plan has valid structure')
    else:
        print('✗ Demo plan missing instances section')
        sys.exit(1)
except Exception as e:
    print(f'✗ Demo plan YAML parsing failed: {e}')
    sys.exit(1)
"
else
    echo "✗ Demo plan file missing"
    exit 1
fi

# Test 6: Cloud-init templates
echo ""
echo "☁️  Testing cloud-init templates..."
for template in infra/orchestrator/assets/cloudinit/*.yaml; do
    if [ -f "$template" ]; then
        filename=$(basename "$template")
        echo "✓ Cloud-init template exists: $filename"
        # Basic YAML validation
        python -c "
import yaml
try:
    with open('$template', 'r') as f:
        yaml.safe_load(f)
    print('✓ $filename is valid YAML')
except Exception as e:
    print('✗ $filename YAML parsing failed: $e')
    exit(1)
"
    fi
done

# Test 7: Makefile targets
echo ""
echo "🔨 Testing Makefile targets..."
if make help | grep -q "Orchestration"; then
    echo "✓ Makefile contains orchestration targets"
else
    echo "✗ Makefile missing orchestration section"
    exit 1
fi

# Test 8: Error handling
echo ""
echo "⚠️  Testing error handling..."
# Test with invalid plan file
if python -m infra.orchestrator.cli apply /nonexistent/plan.yaml 2>/dev/null; then
    echo "✗ Expected apply to fail with nonexistent plan"
    exit 1
else
    echo "✓ Apply correctly fails with nonexistent plan"
fi

# Test 9: Documentation
echo ""
echo "📚 Testing documentation..."
if [ -f "infra/orchestrator/README.md" ]; then
    echo "✓ README.md exists"
    if grep -q "Quick Start" infra/orchestrator/README.md; then
        echo "✓ README contains Quick Start section"
    else
        echo "✗ README missing Quick Start section"
        exit 1
    fi
else
    echo "✗ README.md missing"
    exit 1
fi

# Test 10: Code organization
echo ""
echo "📁 Testing code organization..."
expected_files=(
    "infra/orchestrator/__init__.py"
    "infra/orchestrator/__main__.py"
    "infra/orchestrator/cli.py"
    "infra/orchestrator/health.py"
    "infra/orchestrator/utils.py"
    "infra/orchestrator/providers/__init__.py"
    "infra/orchestrator/providers/base.py"
    "infra/orchestrator/providers/incus.py"
    "infra/orchestrator/providers/multipass.py"
)

for file in "${expected_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file missing"
        exit 1
    fi
done

echo ""
echo "🎉 All integration tests passed!"
echo ""
echo "📊 Summary:"
echo "- Module structure: ✓ Complete"
echo "- CLI interface: ✓ Functional"
echo "- Health system: ✓ Working"
echo "- Error handling: ✓ Robust"
echo "- Documentation: ✓ Present"
echo "- Code quality: ✓ Organized"
echo ""
echo "🚀 YAZ Orchestration System is ready for deployment!"

# Clean up
rm -f /tmp/health.json

exit 0
