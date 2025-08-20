#!/usr/bin/env python3
"""
AI-Powered Resume Variant Builder
Uses Claude to intelligently generate resume variants based on job descriptions
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import tempfile

class AIVariantBuilder:
    """AI-powered resume variant generator using Claude"""
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = Path(workspace_dir)
        self.variants_dir = self.workspace_dir / 'variants'
        self.templates_dir = self.workspace_dir / 'templates'
        self.scripts_dir = self.workspace_dir / 'scripts'
        
        # Load existing variant manager for metadata handling
        sys.path.append(str(self.scripts_dir))
        from variant_manager import VariantManager
        self.variant_manager = VariantManager(self.workspace_dir.parent)
        
    def create_ai_variant(self, parent_file: str, job_description: str, 
                         job_title: str = "", company_name: str = "",
                         focus_type: str = "", variant_name: str = "") -> Dict:
        """Create an AI-optimized resume variant"""
        
        try:
            # Determine parent file path
            parent_path = self._resolve_parent_path(parent_file)
            if not parent_path.exists():
                return {'success': False, 'error': f'Parent file not found: {parent_file}'}
            
            # Read parent content
            with open(parent_path, 'r', encoding='utf-8') as f:
                parent_content = f.read()
            
            # Generate variant name if not provided
            if not variant_name:
                variant_name = self.variant_manager.create_variant_name(
                    job_title, company_name, focus_type, parent_file
                )
            
            # Create AI prompt with full context
            ai_prompt = self._create_ai_prompt(
                parent_content, job_description, job_title, 
                company_name, focus_type, parent_file
            )
            
            # Execute AI generation
            optimized_content = self._execute_ai_generation(ai_prompt, parent_content)
            
            if not optimized_content:
                return {'success': False, 'error': 'AI generation failed'}
            
            # Add proper metadata
            final_content = self._add_ai_metadata(
                optimized_content, parent_file, job_title, 
                company_name, focus_type, job_description
            )
            
            # Save variant
            variant_path = self.variants_dir / variant_name
            variant_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(variant_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            return {
                'success': True,
                'variant_name': variant_name,
                'variant_path': str(variant_path),
                'parent_file': parent_file,
                'job_title': job_title,
                'company_name': company_name
            }
            
        except Exception as e:
            return {'success': False, 'error': f'AI variant creation failed: {str(e)}'}
    
    def create_ai_hybrid(self, parent_files: List[str], job_description: str,
                        hybrid_name: str = "", description: str = "") -> Dict:
        """Create an AI-optimized hybrid variant from multiple parents"""
        
        try:
            if len(parent_files) < 2:
                return {'success': False, 'error': 'Hybrid variants require at least 2 parent files'}
            
            # Read all parent contents
            parent_contents = {}
            for parent_file in parent_files:
                parent_path = self._resolve_parent_path(parent_file)
                if not parent_path.exists():
                    return {'success': False, 'error': f'Parent file not found: {parent_file}'}
                
                with open(parent_path, 'r', encoding='utf-8') as f:
                    parent_contents[parent_file] = f.read()
            
            # Generate hybrid name if not provided
            if not hybrid_name:
                hybrid_name = f"hybrid_{len(parent_files)}way_{datetime.now().strftime('%m%d_%H%M')}.html"
            
            # Create AI prompt for hybrid generation
            ai_prompt = self._create_hybrid_ai_prompt(
                parent_contents, job_description, description
            )
            
            # Execute AI hybrid generation
            hybrid_content = self._execute_ai_generation(ai_prompt, list(parent_contents.values())[0])
            
            if not hybrid_content:
                return {'success': False, 'error': 'AI hybrid generation failed'}
            
            # Add hybrid metadata
            final_content = self._add_hybrid_metadata(
                hybrid_content, parent_files, description, job_description
            )
            
            # Save hybrid variant
            hybrid_path = self.variants_dir / hybrid_name
            with open(hybrid_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            return {
                'success': True,
                'hybrid_name': hybrid_name,
                'hybrid_path': str(hybrid_path),
                'parent_files': parent_files,
                'description': description
            }
            
        except Exception as e:
            return {'success': False, 'error': f'AI hybrid creation failed: {str(e)}'}
    
    def _resolve_parent_path(self, parent_file: str) -> Path:
        """Resolve the full path to a parent file"""
        print(f"[AI Builder] Resolving parent path for: {parent_file}")
        
        if parent_file.startswith('base_'):
            resolved = self.templates_dir / parent_file
            print(f"[AI Builder] Resolved as template: {resolved}")
            return resolved
        else:
            # Handle variants (including those with special prefixes like __gen)
            resolved = self.variants_dir / parent_file
            print(f"[AI Builder] Resolved as variant: {resolved}")
            return resolved
    
    def _create_ai_prompt(self, parent_content: str, job_description: str,
                         job_title: str, company_name: str, focus_type: str,
                         parent_file: str) -> str:
        """Create comprehensive AI prompt for variant generation"""
        
        # Extract current resume sections for context
        sections_info = self._analyze_resume_sections(parent_content)
        
        prompt = f"""# Resume Optimization Task

**Target Role:** {job_title or 'Software Engineer'} at {company_name or 'Target Company'}
**Optimization Focus:** {focus_type or 'General optimization'}

## Job Requirements:
{job_description[:1500] if len(job_description) > 1500 else job_description}

## Current Resume to Optimize:
Located at: templates/{parent_file} and variants/ directory

## Your Task:
1. Read the source resume from the workspace
2. Analyze job requirements vs current resume content
3. Create an optimized version that:
   - Emphasizes most relevant experience first
   - Highlights matching skills and technologies
   - Uses <strong> tags for key terms that match the job
   - Maintains all factual accuracy and professional formatting
   - Follows ATS-friendly structure

4. Save the optimized resume as a new file in variants/ directory

Use your full capabilities as an autonomous agent. Read files, analyze content, and create the best possible optimization."""

        return prompt
    
    def _create_hybrid_ai_prompt(self, parent_contents: Dict[str, str], 
                                job_description: str, description: str) -> str:
        """Create AI prompt for hybrid variant generation"""
        
        prompt = f"""# Hybrid Resume Creation Task

You are an expert resume writer creating a hybrid resume that intelligently combines the best features from multiple parent resumes for a specific job.

## Task Overview

Create a hybrid resume that combines strengths from {len(parent_contents)} parent resumes:
{list(parent_contents.keys())}

**Hybrid Description:** {description or 'Intelligent combination of parent features'}

## Job Description

```
{job_description}
```

## Parent Resume Analysis

"""
        
        for i, (filename, content) in enumerate(parent_contents.items(), 1):
            sections_info = self._analyze_resume_sections(content)
            prompt += f"""
### Parent {i}: {filename}
{sections_info}

"""
        
        prompt += f"""
## Hybridization Instructions

1. **Content Strategy:**
   - Identify the strongest elements from each parent resume
   - Combine professional summaries to create a compelling narrative
   - Merge experience sections, taking the best bullet points from each
   - Consolidate skills, emphasizing those most relevant to the job

2. **Technical Requirements:**
   - Use the HTML structure from the most ATS-optimized parent
   - Maintain clean, professional formatting
   - Ensure single-page PDF compatibility
   - Preserve all CSS classes and styling

3. **Quality Standards:**
   - Maintain factual accuracy from all parents
   - Eliminate redundancy while preserving unique strengths
   - Ensure cohesive flow and professional presentation
   - Optimize for ATS while maintaining readability

## Parent Resume Contents

"""
        
        for filename, content in parent_contents.items():
            prompt += f"""
### {filename}
```html
{content}
```

"""
        
        prompt += """
## Output Requirements

Return ONLY the complete, hybrid HTML resume. No explanations, just the full HTML document that intelligently combines the best of all parents for this specific job.

Generate the hybrid resume now:"""
        
        return prompt
    
    def _analyze_resume_sections(self, content: str) -> str:
        """Analyze resume content to provide context for AI"""
        
        analysis = "**Resume Structure Analysis:**\n\n"
        
        # Extract key sections
        if '<div class="professional-summary">' in content:
            summary_start = content.find('<div class="professional-summary">') + len('<div class="professional-summary">')
            summary_end = content.find('</div>', summary_start)
            summary_text = content[summary_start:summary_end]
            # Clean HTML tags for analysis
            import re
            clean_summary = re.sub(r'<[^>]+>', '', summary_text).strip()
            analysis += f"- **Professional Summary:** {clean_summary[:150]}...\n"
        
        # Count experience items
        experience_count = content.count('<div class="experience-item">')
        analysis += f"- **Experience Items:** {experience_count} positions\n"
        
        # Count skills
        skill_count = content.count('<div class="skill-row">')
        analysis += f"- **Technical Skills:** {skill_count} skill categories\n"
        
        # Check for education
        if 'education' in content.lower():
            analysis += "- **Education:** Present\n"
        
        # Identify key technologies mentioned
        import re
        tech_keywords = ['Python', 'JavaScript', 'React', 'Node.js', 'Docker', 'AWS', 'MySQL', 'PostgreSQL']
        found_tech = []
        for tech in tech_keywords:
            if tech.lower() in content.lower():
                found_tech.append(tech)
        
        if found_tech:
            analysis += f"- **Key Technologies:** {', '.join(found_tech[:8])}\n"
        
        return analysis
    
    def _execute_ai_generation(self, prompt: str, fallback_content: str) -> Optional[str]:
        """Execute AI generation using Claude CLI as autonomous agent in workspace"""
        
        try:
            print("🤖 Starting autonomous AI agent optimization...")
            
            # Prepare the workspace-aware agent prompt
            agent_prompt = self._create_agent_prompt(prompt)
            
            # Execute Claude CLI as autonomous agent with full workspace access
            original_cwd = os.getcwd()
            
            try:
                os.chdir(str(self.workspace_dir))
                
                print(f"   💭 Launching autonomous agent in workspace...")
                
                # Use Claude CLI as agent with workspace access and permission bypass
                result = subprocess.run(
                    ['claude', '--print', '--dangerously-skip-permissions'],
                    input=agent_prompt,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minutes for autonomous agent work
                    cwd=str(self.workspace_dir)
                )
                
                print(f"   📊 Agent exit code: {result.returncode}")
                
                if result.returncode == 0 and result.stdout.strip():
                    print("   ✅ Autonomous agent completed successfully")
                    
                    # Check if agent created a new file
                    created_file = self._find_newly_created_variant()
                    if created_file:
                        print(f"   🎯 Agent created new variant: {created_file}")
                        with open(created_file, 'r', encoding='utf-8') as f:
                            return f.read()
                    
                    # Fallback: extract HTML from agent response
                    response = result.stdout.strip()
                    html_content = self._extract_html_content(response)
                    
                    if html_content and '<!DOCTYPE html>' in html_content:
                        print("   🎯 Agent returned HTML content directly")
                        return html_content
                    else:
                        print(f"   ⚠️  Agent completed but no valid output found")
                        print(f"   📝 Agent output: {response[:300]}...")
                        return None
                        
                else:
                    error_msg = result.stderr.strip() if result.stderr else f"Exit code: {result.returncode}"
                    print(f"   ❌ Autonomous agent failed: {error_msg}")
                    print(f"   📝 stderr: {result.stderr[:200] if result.stderr else 'none'}")
                    return None
                    
            finally:
                os.chdir(original_cwd)
                    
        except subprocess.TimeoutExpired:
            print("   ⏰ Autonomous agent timed out, trying Gemini...")
            return self._execute_gemini_generation(prompt)
        except FileNotFoundError:
            print("   ❌ Claude CLI not found, trying Gemini...")
            return self._execute_gemini_generation(prompt)
        except Exception as e:
            print(f"   ❌ Autonomous agent error: {e}, trying Gemini...")
            return self._execute_gemini_generation(prompt)
    
    def _create_agent_prompt(self, optimization_prompt: str) -> str:
        """Create an autonomous agent prompt for workspace-based resume optimization"""
        
        return f"""You are an autonomous AI agent working in a resume optimization workspace. Your task is to create an optimized resume variant.

## Your Workspace Environment

You have access to:
- `/variants/` directory with existing resume variants
- `/templates/` directory with base resume templates  
- `/scripts/` directory with helper tools (use if needed)
- File reading, writing, and analysis capabilities
- All standard tools for HTML manipulation

## Your Mission

{optimization_prompt}

## Instructions for Autonomous Operation

1. **Analyze the source resume** - Read and understand the structure
2. **Create optimized variant** - Build a new HTML file with improvements
3. **Use your judgment** - You have full autonomy to:
   - Reorder content for maximum impact
   - Emphasize relevant skills with <strong> tags
   - Adjust layout if beneficial
   - Use any workspace tools that help
   - Create the best possible resume for the target role

4. **Save your work** - Write the final optimized resume to a new file in `/variants/`

## Success Criteria

- Create a complete, valid HTML resume
- Maintain professional formatting
- Optimize for the specific job/focus provided
- Ensure ATS compatibility
- Preserve all factual information

## Output Format

After completing your work, respond with ONLY:
- Path to the created file, OR
- The complete HTML content if you couldn't create a file

Work autonomously and use whatever approach you think is best. You have full access to the workspace.

Begin your autonomous optimization now."""

    def _find_newly_created_variant(self) -> Optional[str]:
        """Find the most recently created variant file"""
        try:
            variant_files = list(self.variants_dir.glob('*.html'))
            if not variant_files:
                return None
            
            # Sort by modification time, get the newest
            newest = max(variant_files, key=lambda f: f.stat().st_mtime)
            
            # Check if it was created in the last 60 seconds
            import time
            if time.time() - newest.stat().st_mtime < 60:
                return str(newest)
            
            return None
        except Exception as e:
            print(f"   ⚠️  Error finding new variant: {e}")
            return None
    
    def _execute_gemini_generation(self, prompt: str) -> Optional[str]:
        """Fallback: Use Google Gemini API for AI generation"""
        try:
            import google.generativeai as genai
            import os
            
            # Check for API key
            api_key = os.environ.get('GEMINI_API_KEY')
            if not api_key:
                print("   ❌ No Gemini API key found (set GEMINI_API_KEY environment variable)")
                return None
            
            print("   🔄 Attempting Gemini AI generation...")
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Generate response
            response = model.generate_content(prompt)
            
            if response.text:
                print("   ✅ Gemini responded successfully")
                html_content = self._extract_html_content(response.text)
                
                if html_content and '<!DOCTYPE html>' in html_content:
                    print("   🎯 Valid HTML content generated with Gemini")
                    return html_content
                else:
                    print(f"   ⚠️  No valid HTML found in Gemini response")
                    return None
            else:
                print("   ❌ Gemini returned empty response")
                return None
                
        except ImportError:
            print("   ❌ Google Generative AI library not installed (pip install google-generativeai)")
            return None
        except Exception as e:
            print(f"   ❌ Gemini generation error: {e}")
            return None
    
    
    def _parse_claude_response(self, stdout: str) -> Optional[str]:
        """Parse Claude's JSON stream response format"""
        response_text = ""
        
        lines = stdout.split('\n')
        for line in lines:
            if line.strip():
                try:
                    json_data = json.loads(line)
                    
                    # Extract assistant message content
                    if json_data.get('type') == 'assistant' and 'message' in json_data:
                        message = json_data['message']
                        if 'content' in message:
                            for content_item in message['content']:
                                if content_item.get('type') == 'text' and 'text' in content_item:
                                    response_text += content_item['text']
                    
                    # Also capture final result
                    elif json_data.get('type') == 'result' and 'result' in json_data:
                        response_text += str(json_data['result'])
                        
                except json.JSONDecodeError:
                    # Not JSON, might be plain text - add it anyway
                    if not line.startswith('[') and 'INFO:' not in line:
                        response_text += line + '\n'
        
        return response_text.strip() if response_text else None
    
    def _extract_html_content(self, response: str) -> str:
        """Extract clean HTML content from Claude's response"""
        # Handle markdown code blocks
        if '```html' in response:
            # Extract from markdown code block
            start_marker = response.find('```html') + 7
            end_marker = response.find('```', start_marker)
            if end_marker > start_marker:
                html_content = response[start_marker:end_marker].strip()
            else:
                html_content = response[start_marker:].strip()
        elif '<!DOCTYPE html>' in response:
            # Direct HTML content
            html_start = response.find('<!DOCTYPE html>')
            html_content = response[html_start:]
            
            # Clean up any extra text after closing html tag
            html_end = html_content.rfind('</html>') + 7
            if html_end > 6:
                html_content = html_content[:html_end]
        else:
            # Return original if no clear HTML structure
            return response
        
        return html_content
    
    def _execute_task_based_generation(self, prompt: str) -> Optional[str]:
        """Fallback: Use task-based generation approach"""
        try:
            # Import task-based generator
            import sys
            sys.path.append(str(self.scripts_dir))
            from task_based_ai_generator import TaskBasedAIGenerator
            
            # For now, we'll create task instructions and indicate manual execution needed
            print("📝 Creating task-based optimization instructions...")
            print("   Manual execution will be required through Claude interface")
            
            # Return None to indicate AI generation not available automatically
            # But the task instructions will be created for manual execution
            return None
            
        except Exception as e:
            print(f"Task-based generation error: {e}")
            return None
    
    def _add_ai_metadata(self, content: str, parent_file: str, job_title: str,
                        company_name: str, focus_type: str, job_description: str) -> str:
        """Add AI generation metadata to the resume"""
        
        # Extract job analysis for metadata
        job_analysis = {
            'parent': parent_file,
            'job_title': job_title,
            'company': company_name,
            'focus_type': focus_type,
            'generated_by': 'AI (Claude)',
            'generation_time': datetime.now().isoformat()
        }
        
        metadata = f"""    <!-- AI_GENERATED: true -->
    <!-- PARENT: {parent_file} -->
    <!-- GENERATION: {self.variant_manager.get_next_generation(parent_file)} -->
    <!-- JOB_TITLE: {job_title} -->
    <!-- JOB_COMPANY: {company_name} -->
    <!-- VARIANT_TYPE: {focus_type or 'AI Optimized'} -->
    <!-- VARIANT_DESC: AI-optimized for {job_title} at {company_name} -->
    <!-- GENERATED: {datetime.now().isoformat()} -->
    <!-- JOB_ANALYSIS: {json.dumps(job_analysis)} -->"""
        
        # Insert metadata after <head> tag
        head_pos = content.find('<head>') + 6
        return content[:head_pos] + '\n' + metadata + content[head_pos:]
    
    def _add_hybrid_metadata(self, content: str, parent_files: List[str],
                           description: str, job_description: str) -> str:
        """Add hybrid metadata to the resume"""
        
        parents_str = ', '.join(parent_files)
        
        metadata = f"""    <!-- AI_GENERATED: true -->
    <!-- HYBRID: true -->
    <!-- PARENTS: {parents_str} -->
    <!-- GENERATION: {max(self.variant_manager.get_variant_generation(p) for p in parent_files) + 1} -->
    <!-- VARIANT_TYPE: AI Hybrid -->
    <!-- VARIANT_DESC: AI hybrid - {description} -->
    <!-- HYBRID_FEATURES: Intelligent combination of {len(parent_files)} parent resumes -->
    <!-- GENERATED: {datetime.now().isoformat()} -->"""
        
        # Insert metadata after <head> tag
        head_pos = content.find('<head>') + 6
        return content[:head_pos] + '\n' + metadata + content[head_pos:]


def main():
    """CLI interface for AI variant builder"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI-Powered Resume Variant Builder')
    parser.add_argument('command', choices=['create', 'hybrid', 'test'])
    parser.add_argument('--parent', required=False, help='Parent template file')
    parser.add_argument('--parents', nargs='+', help='Parent files for hybrid')
    parser.add_argument('--job', required=False, help='Job description file or text')
    parser.add_argument('--title', help='Job title')
    parser.add_argument('--company', help='Company name')
    parser.add_argument('--focus', help='Focus type')
    parser.add_argument('--name', help='Output variant name')
    parser.add_argument('--description', help='Hybrid description')
    
    args = parser.parse_args()
    
    # Initialize builder
    workspace_dir = Path(__file__).parent.parent
    builder = AIVariantBuilder(workspace_dir)
    
    if args.command == 'create':
        if not args.parent or not args.job:
            print("Error: --parent and --job are required for create command")
            return
        
        # Read job description
        if os.path.isfile(args.job):
            with open(args.job, 'r') as f:
                job_desc = f.read()
        else:
            job_desc = args.job
        
        result = builder.create_ai_variant(
            parent_file=args.parent,
            job_description=job_desc,
            job_title=args.title or '',
            company_name=args.company or '',
            focus_type=args.focus or '',
            variant_name=args.name or ''
        )
        
        if result['success']:
            print(f"✅ AI variant created: {result['variant_name']}")
            print(f"   📄 Parent: {result['parent_file']}")
            print(f"   💼 Job: {result['job_title']} at {result['company_name']}")
            print(f"   📁 Path: {result['variant_path']}")
        else:
            print(f"❌ Failed: {result['error']}")
    
    elif args.command == 'hybrid':
        if not args.parents or len(args.parents) < 2 or not args.job:
            print("Error: --parents (2+) and --job are required for hybrid command")
            return
        
        # Read job description
        if os.path.isfile(args.job):
            with open(args.job, 'r') as f:
                job_desc = f.read()
        else:
            job_desc = args.job
        
        result = builder.create_ai_hybrid(
            parent_files=args.parents,
            job_description=job_desc,
            hybrid_name=args.name or '',
            description=args.description or ''
        )
        
        if result['success']:
            print(f"✅ AI hybrid created: {result['hybrid_name']}")
            print(f"   👨‍👩‍👧 Parents: {', '.join(result['parent_files'])}")
            print(f"   📝 Description: {result['description']}")
            print(f"   📁 Path: {result['hybrid_path']}")
        else:
            print(f"❌ Failed: {result['error']}")
    
    elif args.command == 'test':
        print("🧪 Testing AI variant builder...")
        
        # Check if Claude CLI is available
        try:
            result = subprocess.run(['claude', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Claude CLI is available")
            else:
                print("❌ Claude CLI not working properly")
        except FileNotFoundError:
            print("❌ Claude CLI not found")
        
        # List available templates
        templates = list(builder.templates_dir.glob('*.html'))
        variants = list(builder.variants_dir.glob('*.html'))
        
        print(f"📄 Templates available: {len(templates)}")
        for t in templates:
            print(f"   - {t.name}")
        
        print(f"📝 Variants available: {len(variants)}")
        for v in variants[-5:]:  # Show last 5
            print(f"   - {v.name}")


if __name__ == "__main__":
    main()