#!/usr/bin/env python3
"""
Job-Specific Resume Optimizer
Analyzes job descriptions and optimizes resume content for ATS compatibility
while maintaining factual accuracy.
"""

import re
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple

class JobResumeOptimizer:
    """Optimizes resume content based on job requirements"""
    
    def __init__(self, base_template_path: str):
        self.base_template_path = base_template_path
        self.optimization_rules = self._load_optimization_rules()
    
    def _load_optimization_rules(self) -> Dict:
        """Load optimization rules for different job types"""
        return {
            "software_engineer": {
                "emphasize": ["technical skills", "architecture", "coding experience"],
                "keywords": ["python", "javascript", "react", "docker", "api", "database"],
                "reorder_priority": ["technical_skills", "professional_experience", "education"]
            },
            "lead_engineer": {
                "emphasize": ["leadership", "team management", "technical strategy"],
                "keywords": ["led team", "mentored", "architecture", "strategy", "ci/cd"],
                "reorder_priority": ["professional_experience", "technical_skills", "education"]
            },
            "remote_position": {
                "emphasize": ["remote work experience", "self-direction", "communication"],
                "keywords": ["remote", "distributed", "asynchronous", "self-directed"],
                "location_emphasis": True
            },
            "local_position": {
                "emphasize": ["local presence", "on-site availability"],
                "keywords": ["denver", "colorado", "local", "on-site"],
                "location_emphasis": True
            },
            "startup": {
                "emphasize": ["versatility", "rapid development", "ownership"],
                "keywords": ["full-stack", "agile", "mvp", "rapid", "ownership"],
                "tone": "dynamic"
            },
            "enterprise": {
                "emphasize": ["scale", "reliability", "process"],
                "keywords": ["enterprise", "scalable", "robust", "compliance", "process"],
                "tone": "professional"
            }
        }
    
    def analyze_job_description(self, job_description: str) -> Dict:
        """Analyze job description to determine optimization strategy"""
        job_desc_lower = job_description.lower()
        
        analysis = {
            "job_type": "software_engineer",  # default
            "company_type": "enterprise",     # default
            "work_style": "hybrid",           # default
            "required_skills": [],
            "nice_to_have_skills": [],
            "location_requirements": None,
            "experience_level": "mid_senior",
            "emphasis_areas": []
        }
        
        # Detect job type
        if any(word in job_desc_lower for word in ["lead", "senior", "principal", "staff"]):
            analysis["job_type"] = "lead_engineer"
        elif any(word in job_desc_lower for word in ["engineer", "developer", "programmer"]):
            analysis["job_type"] = "software_engineer"
        
        # Detect company type
        if any(word in job_desc_lower for word in ["startup", "early stage", "fast-paced"]):
            analysis["company_type"] = "startup"
        elif any(word in job_desc_lower for word in ["enterprise", "fortune", "established"]):
            analysis["company_type"] = "enterprise"
        
        # Detect work style
        if any(word in job_desc_lower for word in ["remote", "work from home", "distributed"]):
            analysis["work_style"] = "remote"
        elif any(word in job_desc_lower for word in ["on-site", "in office", "local"]):
            analysis["work_style"] = "local"
        
        # Extract skills
        tech_skills = [
            "python", "javascript", "typescript", "react", "node.js", "docker", 
            "kubernetes", "aws", "mysql", "postgresql", "mongodb", "redis",
            "ci/cd", "git", "linux", "rest", "graphql", "tensorflow", "pandas"
        ]
        
        for skill in tech_skills:
            if skill in job_desc_lower:
                analysis["required_skills"].append(skill)
        
        # Location analysis
        if any(word in job_desc_lower for word in ["denver", "colorado", "co"]):
            analysis["location_requirements"] = "denver_preferred"
        
        return analysis
    
    def optimize_resume(self, job_analysis: Dict, job_title: str = "", company_name: str = "") -> str:
        """Create optimized resume variant based on job analysis"""
        
        with open(self.base_template_path, 'r', encoding='utf-8') as f:
            resume_content = f.read()
        
        # Apply optimizations
        optimized_content = self._apply_content_optimizations(resume_content, job_analysis)
        optimized_content = self._apply_styling_optimizations(optimized_content, job_analysis)
        optimized_content = self._add_variant_metadata(optimized_content, job_analysis, job_title, company_name)
        
        return optimized_content
    
    def _apply_content_optimizations(self, content: str, job_analysis: Dict) -> str:
        """Apply content-based optimizations"""
        
        # Adjust title based on job type
        if job_analysis["job_type"] == "lead_engineer":
            content = content.replace(
                "<h1>Enrico Patarini</h1>",
                "<h1>Enrico Patarini</h1>"
            )
            content = content.replace(
                "<div class=\"subtitle\">Lead Software Engineer</div>",
                "<div class=\"subtitle\">Lead Software Engineer & Technical Leader</div>"
            )
        
        # Emphasize location for local positions
        if job_analysis.get("location_requirements") == "denver_preferred":
            content = content.replace(
                "<span>Denver, CO 80218</span>",
                "<span><strong>Denver, CO 80218</strong> | Local Candidate</span>"
            )
        
        # Reorder skills based on job requirements
        if job_analysis["required_skills"]:
            content = self._reorder_skills_section(content, job_analysis["required_skills"])
        
        # Adjust experience bullet points
        content = self._optimize_experience_bullets(content, job_analysis)
        
        return content
    
    def _apply_styling_optimizations(self, content: str, job_analysis: Dict) -> str:
        """Apply ATS-friendly styling optimizations"""
        
        # Ensure clean, ATS-readable styling is maintained
        # (The base template should already be ATS-optimized)
        
        # Add emphasis styling for key skills
        if job_analysis["required_skills"]:
            for skill in job_analysis["required_skills"]:
                # Make matching skills slightly more prominent (but still ATS-friendly)
                pattern = f"\\b{re.escape(skill)}\\b"
                replacement = f"<strong>{skill}</strong>"
                content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        return content
    
    def _reorder_skills_section(self, content: str, priority_skills: List[str]) -> str:
        """Reorder skills to put job-relevant ones first"""
        
        # Find the skills section
        skills_start = content.find('<div class="skills-grid">')
        skills_end = content.find('</div>', skills_start) + 6
        
        if skills_start == -1:
            return content
        
        skills_section = content[skills_start:skills_end]
        
        # Extract skill rows
        skill_rows = re.findall(r'<div class="skill-row">.*?</div>', skills_section, re.DOTALL)
        
        # Prioritize rows containing required skills
        prioritized_rows = []
        other_rows = []
        
        for row in skill_rows:
            has_priority_skill = any(skill.lower() in row.lower() for skill in priority_skills)
            if has_priority_skill:
                prioritized_rows.append(row)
            else:
                other_rows.append(row)
        
        # Reconstruct skills section
        new_skills_content = '\n            '.join(prioritized_rows + other_rows)
        new_skills_section = f'<div class="skills-grid">\n            {new_skills_content}\n        </div>'
        
        return content[:skills_start] + new_skills_section + content[skills_end:]
    
    def _optimize_experience_bullets(self, content: str, job_analysis: Dict) -> str:
        """Optimize experience bullet points based on job requirements"""
        
        # This is where you'd implement bullet point reordering/emphasis
        # For now, maintaining original structure to preserve factual accuracy
        
        return content
    
    def _add_variant_metadata(self, content: str, job_analysis: Dict, job_title: str, company_name: str) -> str:
        """Add metadata to track variant purpose"""
        
        metadata_comment = f"""<!-- VARIANT_TYPE: {job_analysis['job_type'].replace('_', ' ').title()} -->
<!-- VARIANT_DESC: Optimized for {job_title} at {company_name} - {job_analysis['work_style']} position -->
<!-- GENERATED: {datetime.now().isoformat()} -->
<!-- JOB_ANALYSIS: {json.dumps(job_analysis)} -->"""
        
        # Insert after opening <head> tag
        head_pos = content.find('<head>') + 6
        return content[:head_pos] + '\n    ' + metadata_comment + content[head_pos:]
    
    def create_cover_letter_template(self, job_analysis: Dict, job_title: str, company_name: str) -> str:
        """Generate a cover letter template based on job analysis"""
        
        template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cover Letter - Enrico Patarini</title>
    <style>
        body {{
            font-family: Georgia, 'Times New Roman', serif;
            line-height: 1.6;
            color: #000000;
            max-width: 700px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #ffffff;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #000000;
            padding-bottom: 20px;
        }}
        
        h1 {{
            margin: 0;
            font-size: 24pt;
            font-weight: bold;
        }}
        
        .contact {{
            margin-top: 10px;
            font-size: 12pt;
        }}
        
        .date {{
            text-align: right;
            margin-bottom: 30px;
            font-size: 12pt;
        }}
        
        .employer-info {{
            margin-bottom: 30px;
            font-size: 12pt;
        }}
        
        .content {{
            font-size: 12pt;
            text-align: justify;
        }}
        
        .content p {{
            margin-bottom: 15px;
        }}
        
        .signature {{
            margin-top: 30px;
            font-size: 12pt;
        }}
        
        @media print {{
            body {{
                padding: 0.5in;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>ENRICO PATARINI</h1>
        <div class="contact">
            Denver, CO 80218 | (860) 817-4548 | Rvpatarini@gmail.com
        </div>
    </div>
    
    <div class="date">
        {datetime.now().strftime('%B %d, %Y')}
    </div>
    
    <div class="employer-info">
        Hiring Manager<br>
        {company_name}<br>
        [Company Address]
    </div>
    
    <div class="content">
        <p>Dear Hiring Manager,</p>
        
        <p>I am writing to express my strong interest in the {job_title} position at {company_name}. With over {self._get_years_experience()} years of software engineering experience and proven leadership in delivering enterprise healthcare solutions, I am excited about the opportunity to contribute to your team's success.</p>
        
        <p>{self._get_personalized_paragraph(job_analysis)}</p>
        
        <p>In my current role as Lead Software Engineer at Davin Healthcare Workforce Solutions, I have successfully led a team of 5 developers while architecting systems that reduced deployment time by over 60%. My experience spans the full technology stack, from frontend React applications to backend API integrations, with a strong focus on scalable, maintainable solutions.</p>
        
        <p>{self._get_location_paragraph(job_analysis)}</p>
        
        <p>I would welcome the opportunity to discuss how my technical expertise, leadership experience, and passion for innovative solutions can contribute to {company_name}'s continued success. Thank you for your consideration.</p>
        
        <div class="signature">
            Sincerely,<br><br>
            Enrico Patarini
        </div>
    </div>
</body>
</html>"""
        
        return template
    
    def _get_years_experience(self) -> int:
        """Calculate years of experience based on resume data"""
        # Started May 2020, so approximately 4+ years
        return 4
    
    def _get_personalized_paragraph(self, job_analysis: Dict) -> str:
        """Generate personalized paragraph based on job analysis"""
        
        if job_analysis["company_type"] == "startup":
            return "I am particularly drawn to fast-paced environments where I can wear multiple hats and drive rapid innovation. My experience building generalized systems and custom AI tools demonstrates my ability to think creatively and deliver solutions that scale with growing organizations."
        
        elif job_analysis["company_type"] == "enterprise":
            return "My experience in enterprise environments has taught me the importance of robust, scalable solutions and thorough documentation. I have successfully managed complex CI/CD pipelines and integrated with multiple enterprise systems while maintaining high standards for code quality and reliability."
        
        else:
            return "Your organization's commitment to technical excellence aligns perfectly with my passion for building high-quality software solutions. I thrive in collaborative environments where I can both contribute technical expertise and mentor fellow developers."
    
    def _get_location_paragraph(self, job_analysis: Dict) -> str:
        """Generate location-specific paragraph"""
        
        if job_analysis["work_style"] == "remote":
            return "As someone who has worked exclusively in remote environments for the past 4+ years, I have developed strong communication skills and self-direction that enable me to excel in distributed teams. I am comfortable with asynchronous collaboration and have experience managing projects across multiple time zones."
        
        elif job_analysis["work_style"] == "local":
            return "As a Denver-based professional, I am excited about the opportunity to contribute to the local tech community. I am available for on-site collaboration and value the benefits of in-person teamwork and mentoring relationships."
        
        else:
            return "I am flexible regarding work arrangements and have experience thriving in both remote and collaborative in-person environments. My focus is always on delivering exceptional results regardless of the work setting."

def main():
    """Example usage of the Job Resume Optimizer"""
    
    # Example job description
    sample_job_description = """
    We are seeking a Senior Software Engineer to join our growing team in Denver, CO.
    The ideal candidate will have experience with Python, React, and Docker, and will be
    comfortable working in a fast-paced startup environment. Remote work is available,
    but we prefer local candidates for occasional in-person collaboration.
    
    Requirements:
    - 3+ years of Python development experience
    - Experience with React and modern JavaScript
    - Docker and containerization experience
    - Strong communication skills for remote work
    - Located in Denver area preferred
    """
    
    # Initialize optimizer
    base_template = "../templates/base_resume.html"
    optimizer = JobResumeOptimizer(base_template)
    
    # Analyze job
    analysis = optimizer.analyze_job_description(sample_job_description)
    print("Job Analysis:", json.dumps(analysis, indent=2))
    
    # Create optimized resume
    if os.path.exists(base_template):
        optimized_resume = optimizer.optimize_resume(analysis, "Senior Software Engineer", "TechCorp")
        
        # Save variant
        output_path = "../variants/techcorp_senior_engineer.html"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(optimized_resume)
        
        print(f"Optimized resume saved to: {output_path}")
        
        # Create cover letter
        cover_letter = optimizer.create_cover_letter_template(analysis, "Senior Software Engineer", "TechCorp")
        cover_path = "../output/techcorp_cover_letter.html"
        
        with open(cover_path, 'w', encoding='utf-8') as f:
            f.write(cover_letter)
        
        print(f"Cover letter template saved to: {cover_path}")
    
    else:
        print(f"Base template not found: {base_template}")

if __name__ == "__main__":
    main()