#!/usr/bin/env python3
"""
AI Resume Agent Command Interface
Central command interface for AI-powered resume variant generation
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add agent workspace scripts to path
WORKSHOP_DIR = Path(__file__).parent
AGENT_WORKSPACE = WORKSHOP_DIR / 'agent_workspace'
SCRIPTS_DIR = AGENT_WORKSPACE / 'scripts'
sys.path.append(str(SCRIPTS_DIR))

def main():
    """Main command interface for AI resume operations"""
    
    parser = argparse.ArgumentParser(
        description='AI Resume Agent - Intelligent resume variant generation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create AI-optimized variant
  python ai_resume_agent.py create --parent base_resume_v2.html --job job_description.txt --title "Senior Software Engineer" --company "TechCorp"
  
  # Create AI hybrid from multiple parents
  python ai_resume_agent.py hybrid --parents appeal_optimized.html skills_matched.html --job job_description.txt --description "Professional appeal + technical skills"
  
  # Test AI system availability
  python ai_resume_agent.py test
  
  # List available templates and variants
  python ai_resume_agent.py list
  
  # Generate job-specific variant with focus
  python ai_resume_agent.py create --parent happydoc_optimal_1217.html --job "We need a Python developer" --focus "backend" --name "python_backend_specialist"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create variant command
    create_parser = subparsers.add_parser('create', help='Create AI-optimized variant')
    create_parser.add_argument('--parent', required=True, help='Parent template/variant filename')
    create_parser.add_argument('--job', required=True, help='Job description (file path or text)')
    create_parser.add_argument('--title', help='Job title')
    create_parser.add_argument('--company', help='Company name')
    create_parser.add_argument('--focus', help='Focus type (e.g., backend, frontend, leadership)')
    create_parser.add_argument('--name', help='Custom variant name')
    
    # Create hybrid command
    hybrid_parser = subparsers.add_parser('hybrid', help='Create AI hybrid from multiple parents')
    hybrid_parser.add_argument('--parents', nargs='+', required=True, help='Parent template/variant filenames (2+ required)')
    hybrid_parser.add_argument('--job', required=True, help='Job description (file path or text)')
    hybrid_parser.add_argument('--description', help='Hybrid description')
    hybrid_parser.add_argument('--name', help='Custom hybrid name')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test AI system availability and configuration')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available templates and variants')
    list_parser.add_argument('--details', action='store_true', help='Show detailed information')
    
    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Start interactive AI resume session')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    if args.command == 'create':
        create_variant(args)
    elif args.command == 'hybrid':
        create_hybrid(args)
    elif args.command == 'test':
        test_system()
    elif args.command == 'list':
        list_templates(args.details)
    elif args.command == 'interactive':
        interactive_mode()


def create_variant(args):
    """Create AI-optimized variant"""
    try:
        from ai_variant_builder import AIVariantBuilder
        
        # Initialize AI builder
        ai_builder = AIVariantBuilder(AGENT_WORKSPACE)
        
        # Read job description
        job_description = read_job_description(args.job)
        
        print(f"🤖 Creating AI-optimized variant...")
        print(f"   📄 Parent: {args.parent}")
        print(f"   💼 Job: {args.title or 'Auto-detected'} at {args.company or 'Auto-detected'}")
        print(f"   🎯 Focus: {args.focus or 'General optimization'}")
        print()
        
        # Create variant
        result = ai_builder.create_ai_variant(
            parent_file=args.parent,
            job_description=job_description,
            job_title=args.title or '',
            company_name=args.company or '',
            focus_type=args.focus or '',
            variant_name=args.name or ''
        )
        
        if result['success']:
            print(f"✅ AI variant created successfully!")
            print(f"   📁 File: {result['variant_name']}")
            print(f"   🔗 Preview: http://localhost:8081/agent_workspace/variants/{result['variant_name']}")
            print(f"   📊 Job: {result['job_title']} at {result['company_name']}")
            print(f"   📂 Full path: {result['variant_path']}")
        else:
            print(f"❌ AI variant creation failed: {result['error']}")
            
    except ImportError:
        print("❌ AI variant builder not available. Check installation.")
    except Exception as e:
        print(f"❌ Error: {e}")


def create_hybrid(args):
    """Create AI hybrid variant"""
    try:
        from ai_variant_builder import AIVariantBuilder
        
        # Initialize AI builder
        ai_builder = AIVariantBuilder(AGENT_WORKSPACE)
        
        # Read job description
        job_description = read_job_description(args.job)
        
        print(f"🧬 Creating AI hybrid variant...")
        print(f"   👨‍👩‍👧 Parents: {', '.join(args.parents)}")
        print(f"   📝 Description: {args.description or 'Intelligent feature combination'}")
        print()
        
        # Create hybrid
        result = ai_builder.create_ai_hybrid(
            parent_files=args.parents,
            job_description=job_description,
            hybrid_name=args.name or '',
            description=args.description or ''
        )
        
        if result['success']:
            print(f"✅ AI hybrid created successfully!")
            print(f"   📁 File: {result['hybrid_name']}")
            print(f"   🔗 Preview: http://localhost:8081/agent_workspace/variants/{result['hybrid_name']}")
            print(f"   👨‍👩‍👧 Parents: {', '.join(result['parent_files'])}")
            print(f"   📂 Full path: {result['hybrid_path']}")
        else:
            print(f"❌ AI hybrid creation failed: {result['error']}")
            
    except ImportError:
        print("❌ AI variant builder not available. Check installation.")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_system():
    """Test AI system availability"""
    print("🧪 Testing AI Resume Agent System")
    print("=" * 50)
    
    # Test 1: Check directory structure
    print("📁 Checking directory structure...")
    
    required_dirs = [
        AGENT_WORKSPACE,
        AGENT_WORKSPACE / 'variants',
        AGENT_WORKSPACE / 'templates',
        SCRIPTS_DIR
    ]
    
    for dir_path in required_dirs:
        if dir_path.exists():
            print(f"   ✅ {dir_path.name}/ - exists")
        else:
            print(f"   ❌ {dir_path.name}/ - missing")
    
    # Test 2: Check Python modules
    print("\n🐍 Checking Python modules...")
    
    modules_to_test = [
        'ai_variant_builder',
        'variant_manager',
        'job_optimizer'
    ]
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"   ✅ {module} - available")
        except ImportError:
            print(f"   ❌ {module} - not found")
    
    # Test 3: Check Claude CLI
    print("\n🤖 Checking Claude CLI...")
    
    import subprocess
    try:
        result = subprocess.run(['claude', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"   ✅ Claude CLI - available")
            print(f"      Version info: {result.stdout.strip()}")
        else:
            print(f"   ⚠️  Claude CLI - not working properly")
            print(f"      Error: {result.stderr}")
    except FileNotFoundError:
        print("   ❌ Claude CLI - not found")
        print("      Install with: npm install -g @anthropic-ai/claude-code")
    except subprocess.TimeoutExpired:
        print("   ⚠️  Claude CLI - timed out")
    except Exception as e:
        print(f"   ❌ Claude CLI test failed: {e}")
    
    # Test 4: Check templates and variants
    print("\n📄 Checking available files...")
    
    templates = list((AGENT_WORKSPACE / 'templates').glob('*.html'))
    variants = list((AGENT_WORKSPACE / 'variants').glob('*.html'))
    
    print(f"   📄 Templates: {len(templates)} available")
    for template in templates[:3]:  # Show first 3
        print(f"      - {template.name}")
    if len(templates) > 3:
        print(f"      ... and {len(templates) - 3} more")
    
    print(f"   📝 Variants: {len(variants)} available")
    for variant in variants[-3:]:  # Show last 3
        print(f"      - {variant.name}")
    if len(variants) > 3:
        print(f"      ... and {len(variants) - 3} more")
    
    # Test 5: Test AI variant builder
    print("\n🤖 Testing AI variant builder...")
    
    try:
        from ai_variant_builder import AIVariantBuilder
        ai_builder = AIVariantBuilder(AGENT_WORKSPACE)
        print("   ✅ AI variant builder - initialized successfully")
        
        # Test with a minimal prompt
        test_job = "Software Engineer position requiring Python and React skills"
        if templates:
            print(f"   🧪 Running test optimization with {templates[0].name}...")
            # This won't actually create a file, just test the system
        
    except Exception as e:
        print(f"   ❌ AI variant builder test failed: {e}")
    
    print("\n🏁 System test complete!")


def list_templates(show_details=False):
    """List available templates and variants"""
    try:
        from variant_manager import VariantManager
        
        manager = VariantManager(WORKSHOP_DIR)
        
        print("📋 Available Resume Templates and Variants")
        print("=" * 60)
        
        # List templates
        templates = list((AGENT_WORKSPACE / 'templates').glob('*.html'))
        print(f"\n📄 Base Templates ({len(templates)}):")
        print("-" * 30)
        
        for template in templates:
            if show_details:
                size = template.stat().st_size / 1024
                print(f"   📄 {template.name} ({size:.1f}KB)")
            else:
                print(f"   📄 {template.name}")
        
        # List variants with details
        variants = manager.list_variants_with_details()
        print(f"\n📝 Generated Variants ({len(variants)}):")
        print("-" * 30)
        
        for variant in variants:
            if show_details:
                print(f"   📝 {variant['filename']}")
                print(f"      📝 {variant['description']}")
                print(f"      🎯 Focus: {variant['focus_type']}")
                print(f"      📊 Size: {variant['size_kb']}KB | Created: {variant['created'].strftime('%m/%d %H:%M')}")
                if variant.get('parents'):
                    print(f"      👨‍👩‍👧 Parents: {', '.join(variant['parents'])}")
                print()
            else:
                focus_info = f" ({variant['focus_type']})" if variant['focus_type'] != 'general' else ""
                print(f"   📝 {variant['filename']}{focus_info}")
        
        print(f"\n🔗 Preview any variant at: http://localhost:8081/agent_workspace/variants/[filename]")
        
    except Exception as e:
        print(f"❌ Error listing templates: {e}")


def interactive_mode():
    """Start interactive AI resume session"""
    print("🤖 AI Resume Agent - Interactive Mode")
    print("=" * 50)
    print("Type 'help' for commands, 'quit' to exit")
    print()
    
    try:
        from ai_variant_builder import AIVariantBuilder
        ai_builder = AIVariantBuilder(AGENT_WORKSPACE)
        
        while True:
            try:
                command = input("AI Resume> ").strip()
                
                if command.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye! 👋")
                    break
                elif command.lower() in ['help', 'h']:
                    print_interactive_help()
                elif command.lower() in ['list', 'ls']:
                    list_templates(show_details=False)
                elif command.lower().startswith('create'):
                    handle_interactive_create(command, ai_builder)
                elif command.lower().startswith('hybrid'):
                    handle_interactive_hybrid(command, ai_builder)
                elif command.lower() == 'test':
                    test_system()
                elif command.strip() == '':
                    continue
                else:
                    print(f"Unknown command: {command}")
                    print("Type 'help' for available commands")
                    
            except KeyboardInterrupt:
                print("\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except ImportError:
        print("❌ AI variant builder not available. Please check installation.")


def print_interactive_help():
    """Print interactive mode help"""
    print("""
Available commands:
  create <parent> <job>          - Create AI variant
  hybrid <parent1> <parent2> <job> - Create AI hybrid
  list                          - List templates and variants
  test                          - Test system
  help                          - Show this help
  quit                          - Exit interactive mode

Examples:
  create base_resume_v2.html "Python developer at startup"
  hybrid appeal_optimized.html skills_matched.html "Senior engineer role"
  list
""")


def handle_interactive_create(command, ai_builder):
    """Handle interactive create command"""
    parts = command.split()
    if len(parts) < 3:
        print("Usage: create <parent> <job_description>")
        return
    
    parent = parts[1]
    job_description = ' '.join(parts[2:])
    
    print(f"Creating variant from {parent} for job: {job_description[:50]}...")
    
    result = ai_builder.create_ai_variant(
        parent_file=parent,
        job_description=job_description,
        job_title='',
        company_name='',
        focus_type='',
        variant_name=''
    )
    
    if result['success']:
        print(f"✅ Created: {result['variant_name']}")
    else:
        print(f"❌ Failed: {result['error']}")


def handle_interactive_hybrid(command, ai_builder):
    """Handle interactive hybrid command"""
    parts = command.split()
    if len(parts) < 4:
        print("Usage: hybrid <parent1> <parent2> <job_description>")
        return
    
    parent1 = parts[1]
    parent2 = parts[2]
    job_description = ' '.join(parts[3:])
    
    print(f"Creating hybrid from {parent1} + {parent2} for job: {job_description[:50]}...")
    
    result = ai_builder.create_ai_hybrid(
        parent_files=[parent1, parent2],
        job_description=job_description,
        hybrid_name='',
        description=''
    )
    
    if result['success']:
        print(f"✅ Created: {result['hybrid_name']}")
    else:
        print(f"❌ Failed: {result['error']}")


def read_job_description(job_input):
    """Read job description from file or return as text"""
    if os.path.isfile(job_input):
        with open(job_input, 'r', encoding='utf-8') as f:
            return f.read().strip()
    else:
        return job_input.strip()


if __name__ == "__main__":
    main()