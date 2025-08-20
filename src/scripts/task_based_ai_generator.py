#!/usr/bin/env python3
"""
Task-based AI Generator for Resume Variants
Uses the Task tool to leverage Claude Code's agent system for resume optimization
"""

import os
import json
import tempfile
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

class TaskBasedAIGenerator:
    """AI generator using Claude Code task system"""
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = Path(workspace_dir)
        self.variants_dir = self.workspace_dir / 'variants'
        self.templates_dir = self.workspace_dir / 'templates'
    
    def create_ai_variant(self, parent_file: str, job_description: str, 
                         job_title: str = "", company_name: str = "",
                         focus_type: str = "", variant_name: str = "") -> Dict:
        """Create an AI-optimized resume variant using task approach"""
        
        try:
            # Resolve parent path
            parent_path = self._resolve_parent_path(parent_file)
            if not parent_path.exists():
                return {'success': False, 'error': f'Parent file not found: {parent_file}'}
            
            # Read parent content
            with open(parent_path, 'r', encoding='utf-8') as f:
                parent_content = f.read()
            
            # Generate variant name if not provided
            if not variant_name:
                timestamp = datetime.now().strftime("%m%d_%H%M")
                safe_company = ''.join(c for c in (company_name or 'ai')[:10] if c.isalnum()).lower()
                variant_name = f"{safe_company}_ai_{timestamp}.html"
            
            # Create task instructions for Claude
            task_instructions = self._create_task_instructions(
                parent_content, job_description, job_title, 
                company_name, focus_type, variant_name
            )
            
            # Save task instructions to temporary file
            task_file = self.workspace_dir / f"task_{variant_name.replace('.html', '.md')}"
            with open(task_file, 'w', encoding='utf-8') as f:
                f.write(task_instructions)
            
            print(f"📝 Task instructions saved to: {task_file}")
            print(f"🤖 To execute the AI optimization:")
            print(f"   1. Open the task file: {task_file}")
            print(f"   2. Copy the instructions")
            print(f"   3. Use Claude to optimize the resume")
            print(f"   4. Save the result as: {self.variants_dir / variant_name}")
            
            return {
                'success': True,
                'variant_name': variant_name,
                'task_file': str(task_file),
                'parent_file': parent_file,
                'job_title': job_title,
                'company_name': company_name,
                'instructions': 'Task file created - manual execution required'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Task creation failed: {str(e)}'}
    
    def _resolve_parent_path(self, parent_file: str) -> Path:
        """Resolve the full path to a parent file"""
        if parent_file.startswith('base_'):
            return self.templates_dir / parent_file
        else:
            return self.variants_dir / parent_file
    
    def _create_task_instructions(self, parent_content: str, job_description: str,
                                job_title: str, company_name: str, focus_type: str,
                                variant_name: str) -> str:
        """Create comprehensive task instructions for Claude"""
        
        # Analyze current resume for context
        sections_info = self._analyze_resume_sections(parent_content)
        
        instructions = f"""# AI Resume Optimization Task

## Task Overview
You are an expert resume writer and ATS optimization specialist. Your task is to intelligently optimize the provided resume for the specific job posting below while maintaining factual accuracy and professional formatting.

## Target Position Details
- **Job Title:** {job_title or 'Not specified'}
- **Company:** {company_name or 'Not specified'}  
- **Focus Area:** {focus_type or 'General optimization'}
- **Output Filename:** {variant_name}

## Current Resume Analysis
{sections_info}

## Job Description to Optimize For
```
{job_description}
```

## Optimization Requirements

### 1. Content Strategy
- **Reorder experience bullets** to put most job-relevant accomplishments first
- **Emphasize relevant technologies** mentioned in the job description
- **Adjust professional summary** to align with the role and company culture
- **Prioritize skills** that match job requirements
- **Maintain factual accuracy** - only reorder, emphasize, or rephrase existing content

### 2. ATS Optimization
- Ensure critical keywords from job description are present and prominent
- Use <strong> tags to emphasize relevant skills and technologies
- Maintain clean, scannable structure
- Avoid keyword stuffing while ensuring relevance

### 3. Technical Requirements
- **Preserve exact HTML structure** and all CSS classes
- **Keep all contact information** and personal details unchanged
- **Maintain single-page PDF compatibility**
- **Use semantic HTML** for better ATS parsing

### 4. Specific Focus Areas
{self._get_focus_guidance(focus_type, job_description)}

## Output Requirements
Please provide the complete, optimized HTML resume. The output should be production-ready and can be saved directly as `{variant_name}`.

## Original Resume Content
```html
{parent_content}
```

---

## Instructions for Execution
1. Analyze the job description for key requirements and technologies
2. Identify the most relevant experience and skills from the current resume
3. Reorder and emphasize content to match job priorities
4. Ensure ATS keyword optimization without compromising readability
5. Return the complete, optimized HTML resume

**Important:** Return ONLY the complete HTML document, no explanations or additional text.
"""
        
        return instructions
    
    def _analyze_resume_sections(self, content: str) -> str:
        """Analyze resume content to provide context"""
        
        analysis = "**Current Resume Structure:**\n\n"
        
        # Extract professional summary
        if '<div class="professional-summary">' in content:
            summary_start = content.find('<div class="professional-summary">') + len('<div class="professional-summary">')
            summary_end = content.find('</div>', summary_start)
            summary_text = content[summary_start:summary_end]
            # Clean HTML tags
            import re
            clean_summary = re.sub(r'<[^>]+>', '', summary_text).strip()
            analysis += f"- **Professional Summary:** {clean_summary[:200]}...\n\n"
        
        # Count sections
        experience_count = content.count('<div class="experience-item">')
        skill_count = content.count('<div class="skill-row">')
        
        analysis += f"- **Experience Positions:** {experience_count} roles listed\n"
        analysis += f"- **Technical Skills:** {skill_count} skill categories\n"
        
        # Identify key technologies
        import re
        tech_keywords = [
            'Python', 'JavaScript', 'TypeScript', 'React', 'Node.js', 'Docker', 
            'Kubernetes', 'AWS', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis',
            'CI/CD', 'Git', 'Linux', 'REST', 'GraphQL', 'TensorFlow', 'Django', 'Flask'
        ]
        
        found_tech = []
        for tech in tech_keywords:
            if tech.lower() in content.lower():
                found_tech.append(tech)
        
        if found_tech:
            analysis += f"- **Technologies Present:** {', '.join(found_tech[:10])}\n"
        
        return analysis
    
    def _get_focus_guidance(self, focus_type: str, job_description: str) -> str:
        """Get specific guidance based on focus type"""
        
        guidance = ""
        
        if focus_type.lower() in ['backend', 'server', 'api']:
            guidance = """
**Backend Development Focus:**
- Emphasize server-side technologies and APIs
- Highlight database design and optimization experience
- Prioritize scalability and performance achievements
- Feature CI/CD and DevOps experience prominently
"""
        elif focus_type.lower() in ['frontend', 'ui', 'ux']:
            guidance = """
**Frontend Development Focus:**
- Emphasize React, JavaScript, and modern frontend frameworks
- Highlight user experience and interface design work
- Prioritize responsive design and cross-browser compatibility
- Feature performance optimization and accessibility work
"""
        elif focus_type.lower() in ['fullstack', 'full-stack']:
            guidance = """
**Full-Stack Development Focus:**
- Balance both frontend and backend experience
- Emphasize end-to-end application development
- Highlight versatility across the technology stack
- Feature integration and architecture experience
"""
        elif focus_type.lower() in ['leadership', 'lead', 'senior']:
            guidance = """
**Leadership/Senior Focus:**
- Emphasize mentoring and team leadership experience
- Highlight architectural decisions and technical strategy
- Prioritize project management and cross-team collaboration
- Feature process improvement and technical initiative leadership
"""
        elif focus_type.lower() in ['startup', 'agile']:
            guidance = """
**Startup/Agile Focus:**
- Emphasize rapid development and iteration
- Highlight ownership and versatility
- Prioritize adaptability and learning agility
- Feature MVP development and scaling experience
"""
        else:
            guidance = """
**General Optimization:**
- Analyze job description for key themes and requirements
- Emphasize most relevant experience and achievements
- Ensure strong alignment between resume content and job needs
- Maintain professional presentation while maximizing relevance
"""
        
        return guidance.strip()


def main():
    """CLI interface for task-based AI generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Task-based AI Resume Generator')
    parser.add_argument('--parent', required=True, help='Parent template file')
    parser.add_argument('--job', required=True, help='Job description')
    parser.add_argument('--title', help='Job title')
    parser.add_argument('--company', help='Company name')
    parser.add_argument('--focus', help='Focus type')
    parser.add_argument('--name', help='Output variant name')
    
    args = parser.parse_args()
    
    # Initialize generator
    workspace_dir = Path(__file__).parent.parent
    generator = TaskBasedAIGenerator(workspace_dir)
    
    # Read job description
    if os.path.isfile(args.job):
        with open(args.job, 'r') as f:
            job_desc = f.read()
    else:
        job_desc = args.job
    
    # Create task
    result = generator.create_ai_variant(
        parent_file=args.parent,
        job_description=job_desc,
        job_title=args.title or '',
        company_name=args.company or '',
        focus_type=args.focus or '',
        variant_name=args.name or ''
    )
    
    if result['success']:
        print(f"✅ Task created successfully!")
        print(f"   📁 Task file: {result['task_file']}")
        print(f"   📄 Target variant: {result['variant_name']}")
        print(f"   💼 Job: {result['job_title']} at {result['company_name']}")
        print(f"\n📝 Next steps:")
        print(f"   1. Review the task file: {result['task_file']}")
        print(f"   2. Use Claude to execute the optimization")
        print(f"   3. Save result as: {result['variant_name']}")
    else:
        print(f"❌ Task creation failed: {result['error']}")


if __name__ == "__main__":
    main()