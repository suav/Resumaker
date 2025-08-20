#!/bin/bash

# AI Resume Agent Setup Script
# Sets up permissions, dependencies, and environment for AI-powered resume generation

WORKSHOP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_WORKSPACE="$WORKSHOP_DIR/agent_workspace"

echo "🤖 Setting up AI Resume Agent"
echo "==============================="
echo "Workshop directory: $WORKSHOP_DIR"
echo "Agent workspace: $AGENT_WORKSPACE"
echo

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Step 1: Check Python
echo "🐍 Checking Python..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "   ✅ Python found: $PYTHON_VERSION"
else
    echo "   ❌ Python 3 not found. Please install Python 3.8+."
    exit 1
fi

# Step 2: Create directory structure
echo
echo "📁 Setting up directory structure..."
mkdir -p "$AGENT_WORKSPACE/variants"
mkdir -p "$AGENT_WORKSPACE/templates"
mkdir -p "$AGENT_WORKSPACE/scripts"
mkdir -p "$AGENT_WORKSPACE/output"

echo "   ✅ Created agent_workspace directories"

# Step 3: Set proper permissions
echo
echo "🔐 Setting up permissions..."

# Make AI agent scripts executable
chmod +x "$WORKSHOP_DIR/ai_resume_agent.py"
chmod +x "$AGENT_WORKSPACE/scripts/ai_variant_builder.py"
chmod +x "$AGENT_WORKSPACE/scripts/variant_manager.py"

# Ensure all scripts are readable/writable
chmod 755 "$AGENT_WORKSPACE/scripts"/*.py 2>/dev/null || true
chmod 664 "$AGENT_WORKSPACE/variants"/*.html 2>/dev/null || true
chmod 664 "$AGENT_WORKSPACE/templates"/*.html 2>/dev/null || true

echo "   ✅ Set executable permissions"

# Step 4: Check Claude CLI
echo
echo "🤖 Checking Claude CLI availability..."

if command_exists claude; then
    CLAUDE_VERSION=$(claude --version 2>&1)
    echo "   ✅ Claude CLI found: $CLAUDE_VERSION"
else
    echo "   ⚠️  Claude CLI not found"
    echo "   📝 To install Claude CLI:"
    echo "      npm install -g @anthropic-ai/claude-code"
    echo "   📝 Or set up API key:"
    echo "      export ANTHROPIC_API_KEY='your-api-key-here'"
    echo
fi

# Step 5: Test AI variant builder
echo
echo "🧪 Testing AI variant builder..."

cd "$WORKSHOP_DIR"

if python3 -c "import sys; sys.path.append('$AGENT_WORKSPACE/scripts'); from ai_variant_builder import AIVariantBuilder" 2>/dev/null; then
    echo "   ✅ AI variant builder imports successfully"
else
    echo "   ❌ AI variant builder import failed"
fi

# Step 6: Test the command interface
echo
echo "🎛️  Testing command interface..."

if python3 "$WORKSHOP_DIR/ai_resume_agent.py" test >/dev/null 2>&1; then
    echo "   ✅ Command interface working"
else
    echo "   ⚠️  Command interface may have issues"
fi

# Step 7: Create sample job description file
echo
echo "📄 Creating sample job description..."

SAMPLE_JOB="$WORKSHOP_DIR/sample_job_description.txt"
cat > "$SAMPLE_JOB" << 'EOF'
Company: TechCorp Inc.
Role: Senior Software Engineer
Location: Denver, CO (Remote/Hybrid)

Job Description:
We are seeking a talented Senior Software Engineer to join our growing engineering team. The ideal candidate will have strong experience with Python, JavaScript, and modern web frameworks.

Requirements:
- 5+ years of software development experience
- Strong proficiency in Python and JavaScript
- Experience with React and modern frontend frameworks
- Knowledge of Docker, Kubernetes, and cloud platforms (AWS preferred)
- Experience with CI/CD pipelines and DevOps practices
- Strong communication skills for remote collaboration
- Bachelor's degree in Computer Science or related field

Responsibilities:
- Design and develop scalable web applications
- Collaborate with cross-functional teams in an agile environment
- Mentor junior developers and contribute to technical decisions
- Implement automated testing and deployment processes
- Participate in code reviews and maintain high code quality standards

Benefits:
- Competitive salary and equity package
- Comprehensive health benefits
- Remote work flexibility
- Professional development budget
- Collaborative and innovative work environment
EOF

echo "   ✅ Created sample job description: sample_job_description.txt"

# Step 8: Create quick start guide
echo
echo "📖 Creating quick start guide..."

QUICKSTART="$WORKSHOP_DIR/AI_AGENT_QUICKSTART.md"
cat > "$QUICKSTART" << 'EOF'
# AI Resume Agent - Quick Start Guide

## Overview
The AI Resume Agent uses Claude to intelligently optimize resume variants based on job descriptions.

## Prerequisites
- Python 3.8+
- Claude CLI installed (`npm install -g @anthropic-ai/claude-code`)
- OR Anthropic API key set in environment

## Quick Commands

### Test the system
```bash
python3 ai_resume_agent.py test
```

### List available templates
```bash
python3 ai_resume_agent.py list --details
```

### Create AI-optimized variant
```bash
python3 ai_resume_agent.py create \
  --parent base_resume_v2.html \
  --job sample_job_description.txt \
  --title "Senior Software Engineer" \
  --company "TechCorp"
```

### Create AI hybrid from multiple parents
```bash
python3 ai_resume_agent.py hybrid \
  --parents appeal_optimized.html skills_matched.html \
  --job sample_job_description.txt \
  --description "Professional appeal + technical expertise"
```

### Interactive mode
```bash
python3 ai_resume_agent.py interactive
```

## Web Interface Integration
The AI system is automatically integrated into the web interface at:
http://localhost:8081/

When you create variants through the web interface, it will:
1. Try AI-powered generation first
2. Fall back to rule-based optimization if AI is unavailable

## Troubleshooting

### Claude CLI not found
Install with: `npm install -g @anthropic-ai/claude-code`

### API key issues
Set environment variable: `export ANTHROPIC_API_KEY='your-key'`

### Permission errors
Run: `bash setup_ai_agent.sh`

## File Structure
```
resume_workshop/
├── ai_resume_agent.py          # Main command interface
├── agent_workspace/
│   ├── scripts/
│   │   ├── ai_variant_builder.py    # AI generation engine
│   │   ├── variant_manager.py       # Variant management
│   │   └── job_optimizer.py         # Rule-based fallback
│   ├── variants/               # Generated variants
│   ├── templates/              # Base templates
│   └── output/                 # PDF outputs
└── server.py                   # Web server with AI integration
```

## Examples

### Command Line Usage
```bash
# Quick test
python3 ai_resume_agent.py test

# List templates
python3 ai_resume_agent.py list

# Create variant with job text
python3 ai_resume_agent.py create --parent base_resume_v2.html --job "Python developer at startup" --focus backend

# Create hybrid
python3 ai_resume_agent.py hybrid --parents appeal_optimized.html skills_matched.html --job "Lead engineer role"
```

### Interactive Mode
```
AI Resume> create base_resume_v2.html "Python developer at startup"
AI Resume> hybrid appeal_optimized.html skills_matched.html "Senior engineer role"
AI Resume> list
AI Resume> quit
```
EOF

echo "   ✅ Created quick start guide: AI_AGENT_QUICKSTART.md"

# Step 9: Final summary
echo
echo "🎉 AI Resume Agent Setup Complete!"
echo "=================================="
echo
echo "📂 Files created:"
echo "   • ai_resume_agent.py - Main command interface"
echo "   • agent_workspace/scripts/ai_variant_builder.py - AI generation engine"
echo "   • sample_job_description.txt - Sample job for testing"
echo "   • AI_AGENT_QUICKSTART.md - Quick start guide"
echo
echo "🚀 Quick start:"
echo "   1. Test system: python3 ai_resume_agent.py test"
echo "   2. List templates: python3 ai_resume_agent.py list"
echo "   3. Create variant: python3 ai_resume_agent.py create --parent base_resume_v2.html --job sample_job_description.txt"
echo
echo "🌐 Web interface:"
echo "   The AI system is integrated into the web interface at http://localhost:8081/"
echo "   Variant creation will automatically use AI when available."
echo
echo "📖 For detailed instructions, see: AI_AGENT_QUICKSTART.md"
echo

# Optional: Test the system
echo "🧪 Running quick system test..."
echo
cd "$WORKSHOP_DIR"
python3 ai_resume_agent.py test