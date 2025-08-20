#!/usr/bin/env python3
"""
Resume Workshop Live Preview Server
Serves resume templates and variants on port 8081 with live reload capability
"""

import os
import json
import http.server
import socketserver
import subprocess
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import threading
import time
import tempfile
import shutil
import uuid
from concurrent.futures import ThreadPoolExecutor
try:
    import requests
    from bs4 import BeautifulSoup
    LINKEDIN_SUPPORT = True
except ImportError:
    LINKEDIN_SUPPORT = False

PORT = 8081
WORKSHOP_DIR = os.path.dirname(os.path.abspath(__file__))

# Job tracking for async variant creation
variant_jobs = {}
executor = ThreadPoolExecutor(max_workers=3)

class ResumeWorkshopHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WORKSHOP_DIR, **kwargs)
    
    def do_GET(self):
        """Handle GET requests with special routing for workshop features"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # API endpoint for variants list
        if path == '/api/variants':
            self.serve_variants_api()
            return
        
        # API endpoint for generating PDFs
        elif path == '/api/generate-pdf':
            self.serve_pdf_generation()
            return
            
        # API endpoint for job descriptions
        elif path == '/api/job-descriptions':
            self.serve_job_descriptions_api()
            return
            
        # API endpoint for LinkedIn job fetching
        elif path == '/api/fetch-linkedin':
            self.serve_linkedin_fetch()
            return
            
        # API endpoint for genealogy tree
        elif path == '/api/genealogy':
            self.serve_genealogy_api()
            return
            
        # API endpoint for variant status
        elif path == '/api/variant-status':
            self.serve_variant_status_api()
            return
        
        # Serve index.html for root
        elif path == '/' or path == '':
            self.path = '/index.html'
        
        # Add cache headers for HTML files to ensure fresh content
        if path.endswith('.html'):
            super().do_GET()
            return
        
        # Handle PDF downloads - support both old and new paths
        elif path.startswith('/output/') or path.startswith('/agent_workspace/output/'):
            self.serve_pdf_download()
            return
        
        # Default handling for other files
        super().do_GET()
    
    def do_POST(self):
        """Handle POST requests for file uploads and form submissions"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/upload-resume':
            self.handle_resume_upload()
        elif path == '/api/create-variant':
            self.handle_create_variant()
        elif path == '/api/create-hybrid':
            self.handle_create_hybrid()
        elif path == '/api/save-job-description':
            self.handle_save_job_description()
        elif path == '/api/delete-job-description':
            self.handle_delete_job_description()
        elif path == '/api/convert-to-pdf':
            self.handle_convert_to_pdf()
        elif path == '/api/delete-variant':
            self.handle_delete_variant()
        elif path == '/api/save-quality-feedback':
            self.handle_save_quality_feedback()
        elif path == '/api/analyze-quality-gap':
            self.handle_analyze_quality_gap()
        else:
            self.send_error(404, "Not found")
    
    def serve_variants_api(self):
        """Serve JSON list of available variants"""
        try:
            variants_dir = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'variants')
            variants = []
            
            if os.path.exists(variants_dir):
                for filename in os.listdir(variants_dir):
                    if filename.endswith('.html'):
                        variant_info = self.extract_variant_info(
                            os.path.join(variants_dir, filename)
                        )
                        variant_info['filename'] = filename
                        variants.append(variant_info)
            
            # Sort by creation time (newest first)
            variants.sort(key=lambda x: x.get('created', ''), reverse=True)
            
            response = json.dumps(variants, indent=2)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response.encode())
            
        except Exception as e:
            self.send_error(500, f"Error reading variants: {str(e)}")
    
    def serve_pdf_generation(self):
        """Handle PDF generation requests"""
        try:
            query_params = parse_qs(urlparse(self.path).query)
            variant = query_params.get('variant', [''])[0]
            
            if not variant:
                self.send_error(400, "Variant parameter required")
                return
            
            # Execute PDF generation (placeholder)
            response = {
                "status": "success",
                "message": f"PDF generation initiated for {variant}",
                "pdf_path": f"agent_workspace/output/{variant.replace('.html', '.pdf')}"
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, f"PDF generation error: {str(e)}")
    
    def serve_job_descriptions_api(self):
        """Serve job descriptions management API"""
        try:
            job_descriptions_dir = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'job_descriptions')
            os.makedirs(job_descriptions_dir, exist_ok=True)
            
            job_descriptions = []
            for filename in os.listdir(job_descriptions_dir):
                if filename.endswith('.txt'):
                    job_path = os.path.join(job_descriptions_dir, filename)
                    with open(job_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract basic info
                    lines = content.split('\n')
                    title = "Unknown Position"
                    company = "Unknown Company"
                    
                    for line in lines:
                        if line.startswith('Role:') or line.startswith('Title:'):
                            title = line.split(':', 1)[1].strip()
                        elif line.startswith('Company:'):
                            company = line.split(':', 1)[1].strip()
                    
                    job_descriptions.append({
                        'filename': filename,
                        'title': title,
                        'company': company,
                        'preview': content[:200] + '...' if len(content) > 200 else content,
                        'created': datetime.fromtimestamp(os.path.getctime(job_path)).isoformat()
                    })
            
            # Also include the main job description
            main_job_file = os.path.join(WORKSHOP_DIR, '..', 'job_description.txt')
            if os.path.exists(main_job_file):
                with open(main_job_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                job_descriptions.insert(0, {
                    'filename': 'job_description.txt',
                    'title': 'Current Target Job',
                    'company': 'Active',
                    'preview': content[:200] + '...' if len(content) > 200 else content,
                    'created': datetime.fromtimestamp(os.path.getctime(main_job_file)).isoformat(),
                    'active': True
                })
            
            response = json.dumps(job_descriptions, indent=2)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response.encode())
            
        except Exception as e:
            self.send_error(500, f"Error reading job descriptions: {str(e)}")
    
    def serve_linkedin_fetch(self):
        """Fetch job description from LinkedIn URL with improved parsing"""
        try:
            query_params = parse_qs(urlparse(self.path).query)
            linkedin_url = query_params.get('url', [''])[0]
            
            if not linkedin_url:
                self.send_error(400, "LinkedIn URL required")
                return
            
            # Extract job ID from URL for better template
            job_id = None
            if '/jobs/view/' in linkedin_url:
                try:
                    job_id = linkedin_url.split('/jobs/view/')[-1].split('?')[0].split('/')[0]
                except:
                    pass
            
            # Try to fetch the page regardless of dependencies
            job_title = "Software Engineer"  # Default
            company_name = "Target Company"  # Default
            location = "Remote/Hybrid"  # Default
            
            try:
                # Import here to avoid startup dependency issues
                import subprocess
                import re
                
                # Use curl to fetch the page with compression handling
                headers = [
                    '-H', 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    '-H', 'Accept-Language: en-US,en;q=0.5',
                    '-H', 'Connection: keep-alive',
                    '-H', 'Upgrade-Insecure-Requests: 1'
                ]
                
                # Use --compressed to automatically decompress gzip/deflate responses
                # Add performance optimizations: limit redirects, set timeouts
                curl_cmd = ['curl', '-s', '-L', '--compressed', '--max-redirs', '3', '--connect-timeout', '5', '--max-time', '8'] + headers + [linkedin_url]
                result_curl = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=8)
                
                if result_curl.returncode == 0:
                    html_content = result_curl.stdout
                    
                    # Try to extract job title from LinkedIn title tag format
                    # LinkedIn format: "Company hiring Title in Location | LinkedIn"
                    title_patterns = [
                        r'<title>([^|]+?)(?:\s*\|\s*LinkedIn)?</title>',
                        r'"jobTitle":"([^"]+)"',
                        r'<h1[^>]*class="[^"]*job[^"]*title[^"]*"[^>]*>([^<]+)</h1>',
                        r'<h1[^>]*>([^<]*(?:Engineer|Developer|Manager|Analyst|Specialist|Director|Lead)[^<]*)</h1>',
                        r'"name":"([^"]*(?:Engineer|Developer|Manager|Analyst|Specialist|Director|Lead)[^"]*)"'
                    ]
                    
                    for pattern in title_patterns:
                        match = re.search(pattern, html_content, re.IGNORECASE)
                        if match:
                            extracted_title = match.group(1).strip()
                            if len(extracted_title) > 5 and len(extracted_title) < 150:
                                # Parse LinkedIn title format: "Company hiring Title in Location"
                                if ' hiring ' in extracted_title:
                                    parts = extracted_title.split(' hiring ')
                                    if len(parts) == 2:
                                        company_name = parts[0].strip()
                                        title_location = parts[1].strip()
                                        if ' in ' in title_location:
                                            title_part, location_part = title_location.split(' in ', 1)
                                            job_title = title_part.strip()
                                            # Clean up location by removing " | LinkedIn" suffix
                                            location = location_part.replace(' | LinkedIn', '').strip()
                                        else:
                                            job_title = title_location
                                        break
                                else:
                                    job_title = extracted_title
                                    break
                    
                    # Try to extract company name if not found above
                    if company_name == "Target Company":
                        company_patterns = [
                            r'"companyName":"([^"]+)"',
                            r'"hiringOrganization":\s*\{\s*"name":"([^"]+)"',
                            r'<span[^>]*class="[^"]*company[^"]*"[^>]*>([^<]+)</span>',
                            r'"company":\s*\{\s*"name":"([^"]+)"'
                        ]
                        
                        for pattern in company_patterns:
                            match = re.search(pattern, html_content, re.IGNORECASE)
                            if match:
                                extracted_company = match.group(1).strip()
                                if len(extracted_company) > 2 and len(extracted_company) < 50:
                                    company_name = extracted_company
                                    break
                    
                    # Try to extract location
                    location_patterns = [
                        r'"jobLocation":"([^"]+)"',
                        r'"addressLocality":"([^"]+)"',
                        r'"location":"([^"]+)"',
                        r'<span[^>]*class="[^"]*location[^"]*"[^>]*>([^<]+)</span>'
                    ]
                    
                    for pattern in location_patterns:
                        match = re.search(pattern, html_content, re.IGNORECASE)
                        if match:
                            extracted_location = match.group(1).strip()
                            if len(extracted_location) > 2 and len(extracted_location) < 50:
                                location = extracted_location
                                break
                
            except Exception as fetch_error:
                print(f"LinkedIn fetch error: {fetch_error}")
                # Use defaults
                pass
            
            # Create enhanced template with extracted info
            # Try to extract the full job description content
            full_job_content = ""
            
            # Look for the main job description content in LinkedIn's markup
            job_section_patterns = [
                r'<div class="show-more-less-html__markup[^"]*"[^>]*>(.*?)</div>',
                r'<section class="show-more-less-html"[^>]*>.*?<div[^>]*class="show-more-less-html__markup[^"]*"[^>]*>(.*?)</div>',
                r'class="jobs-description-details__text[^"]*"[^>]*>(.*?)</div>',
            ]
            
            for pattern in job_section_patterns:
                match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
                if match:
                    job_html = match.group(1)
                    
                    # Convert HTML to readable plaintext while preserving structure
                    # Replace HTML elements with appropriate text formatting
                    job_text = re.sub(r'<br[^>]*>', '\n', job_html)
                    job_text = re.sub(r'<li[^>]*>', '\n• ', job_text)
                    job_text = re.sub(r'</li>', '', job_text)
                    job_text = re.sub(r'<ul[^>]*>', '\n', job_text)
                    job_text = re.sub(r'</ul>', '\n', job_text)
                    job_text = re.sub(r'<p[^>]*>', '\n\n', job_text)
                    job_text = re.sub(r'</p>', '', job_text)
                    job_text = re.sub(r'<strong[^>]*>', '**', job_text)
                    job_text = re.sub(r'</strong>', '**', job_text)
                    job_text = re.sub(r'<em[^>]*>', '_', job_text)
                    job_text = re.sub(r'</em>', '_', job_text)
                    
                    # Remove any remaining HTML tags
                    job_text = re.sub(r'<[^>]+>', '', job_text)
                    
                    # Clean up whitespace and formatting
                    job_text = re.sub(r'\n\s*\n\s*\n', '\n\n', job_text)  # Max 2 consecutive newlines
                    job_text = re.sub(r'[ \t]+', ' ', job_text)  # Multiple spaces to single space
                    job_text = re.sub(r' \n', '\n', job_text)  # Remove trailing spaces before newlines
                    
                    # Decode HTML entities
                    job_text = job_text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")
                    
                    full_job_content = job_text.strip()
                    break
            
            # If we extracted real data, provide the full content
            if company_name != "Target Company" and job_title != "Software Engineer" and full_job_content:
                template_content = f"""Company: {company_name}
Role: {job_title}
Location: {location}
Source: LinkedIn ({linkedin_url})
Job ID: {job_id or 'N/A'}

{full_job_content}

---
Extracted from LinkedIn: {company_name} | {job_title} | {location}
"""
            elif company_name != "Target Company" and job_title != "Software Engineer":
                # Basic extraction without full content
                template_content = f"""Company: {company_name}
Role: {job_title}
Location: {location}
Source: LinkedIn ({linkedin_url})
Job ID: {job_id or 'N/A'}

Job Description:
We are looking for a talented {job_title} to join our team at {company_name} in {location}. 

[Please paste the complete job description from LinkedIn here for optimal resume matching. The system successfully extracted basic details above.]

---
Successfully extracted: {company_name} | {job_title} | {location}
"""
            else:
                # Fallback template when extraction fails
                template_content = f"""Company: [Company Name]
Role: [Job Title]
Location: [Location]
Source: LinkedIn ({linkedin_url})
Job ID: {job_id or 'N/A'}

Job Description:
[Please paste the full job description from LinkedIn here. Automatic extraction was limited.]

Requirements:
- [Paste key requirements here]

Responsibilities:
- [Paste main responsibilities here]

Benefits:
- [Include benefits and compensation if mentioned]

Additional Notes:
- Copy the complete job posting from LinkedIn for best optimization results
- Include any specific technologies, tools, or methodologies mentioned
"""
            
            result = {
                "success": True,  # We successfully created a useful template
                "title": job_title,
                "company": company_name,
                "location": location,
                "job_id": job_id,
                "content": template_content,
                "url": linkedin_url,
                "extraction_note": "Basic details extracted. Please copy full job description for optimal results."
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            # Ultimate fallback
            result = {
                "success": False,
                "error": f"LinkedIn processing error: {str(e)}",
                "message": "Please copy and paste the job description manually",
                "template": f"""Company: [Company Name]
Role: [Job Title]
Location: [Location]
Source: LinkedIn ({linkedin_url})

Job Description:
[Please paste the full job description here]
"""
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
    
    def serve_genealogy_api(self):
        """Serve genealogy tree data"""
        try:
            # Import variant manager
            import sys
            sys.path.append(os.path.join(WORKSHOP_DIR, 'agent_workspace', 'scripts'))
            from variant_manager import VariantManager
            
            manager = VariantManager(os.path.join(WORKSHOP_DIR, 'agent_workspace'))
            tree = manager.create_genealogy_tree()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(tree, default=str, indent=2).encode())
            
        except Exception as e:
            self.send_error(500, f"Genealogy tree error: {str(e)}")
    
    def serve_variant_status_api(self):
        """Serve variant status updates for polling"""
        try:
            # Return current job statuses
            status_updates = []
            
            for job_id, job_info in variant_jobs.items():
                status_updates.append({
                    "job_id": job_id,
                    "status": job_info["status"],
                    "progress": job_info["progress"],
                    "created_at": job_info["created_at"],
                    "result": job_info.get("result"),
                    "error": job_info.get("error")
                })
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(status_updates, default=str).encode())
            
        except Exception as e:
            self.send_error(500, f"Variant status error: {str(e)}")
    
    def create_variant_background(self, job_id):
        """Background method to create variant with AI"""
        try:
            job_data = variant_jobs[job_id]["job_data"]
            
            # Update progress
            variant_jobs[job_id]["progress"] = "Initializing AI builder..."
            
            # Try AI-powered variant creation
            import sys
            sys.path.append(os.path.join(WORKSHOP_DIR, 'agent_workspace', 'scripts'))
            
            try:
                from ai_variant_builder import AIVariantBuilder
                
                variant_jobs[job_id]["progress"] = "Loading AI builder..."
                ai_builder = AIVariantBuilder(os.path.join(WORKSHOP_DIR, 'agent_workspace'))
                
                variant_jobs[job_id]["progress"] = "Running AI generation (this may take 2-5 minutes)..."
                
                print(f"🔧 Background job {job_id} - Creating variant:")
                print(f"   Parent: {job_data['parent_variant']}")
                print(f"   Variant name: {job_data['variant_name']}")
                
                # Create AI-powered variant
                ai_result = ai_builder.create_ai_variant(
                    parent_file=job_data["parent_variant"],
                    job_description=job_data["job_description"],
                    job_title=job_data["job_title"] or '',
                    company_name=job_data["company_name"] or '',
                    focus_type=job_data["focus_type"],
                    variant_name=job_data["variant_name"]
                )
                
                if ai_result['success']:
                    variant_jobs[job_id].update({
                        "status": "completed",
                        "progress": "AI generation completed successfully",
                        "result": {
                            "variant_name": ai_result['variant_name'],
                            "preview_url": f"/agent_workspace/variants/{ai_result['variant_name']}",
                            "ai_generated": True,
                            "parent_file": ai_result['parent_file'],
                            "job_title": ai_result['job_title'],
                            "company_name": ai_result['company_name']
                        }
                    })
                    print(f"✅ Background job {job_id} completed: {ai_result['variant_name']}")
                else:
                    variant_jobs[job_id].update({
                        "status": "failed",
                        "progress": f"AI generation failed: {ai_result.get('error', 'Unknown error')}",
                        "error": ai_result.get('error', 'Unknown error')
                    })
                    print(f"❌ Background job {job_id} failed: {ai_result.get('error')}")
                    
            except Exception as ai_error:
                variant_jobs[job_id].update({
                    "status": "failed",
                    "progress": f"AI builder error: {str(ai_error)}",
                    "error": str(ai_error)
                })
                print(f"❌ Background job {job_id} AI error: {ai_error}")
                
        except Exception as e:
            variant_jobs[job_id].update({
                "status": "failed",
                "progress": f"Background processing error: {str(e)}",
                "error": str(e)
            })
            print(f"❌ Background job {job_id} error: {e}")
    
    def handle_resume_upload(self):
        """Handle resume file upload"""
        try:
            # Create upload directory
            upload_dir = os.path.join(WORKSHOP_DIR, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # For now, return a placeholder response
            # Full multipart parsing would require additional setup
            response = {
                "success": False,
                "message": "File upload feature coming soon",
                "note": "For now, save HTML files directly to uploads/ folder or use copy/paste",
                "upload_dir": upload_dir
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, f"Upload error: {str(e)}")
    
    def handle_create_variant(self):
        """Handle AI-powered variant creation request"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            # Extract parameters - support both parent and parent_template
            # Don't default to base_resume_v2.html if parent is explicitly provided
            parent_variant = data.get('parent') or data.get('parent_template')
            if not parent_variant:
                parent_variant = 'base_resume_v2.html'
                print(f"⚠️  No parent specified, defaulting to: {parent_variant}")
            else:
                print(f"✅ Using specified parent: {parent_variant}")
            job_description = data.get('job_description', '')
            focus_type = data.get('focus_type', '')
            variant_name = data.get('variant_name', '')
            job_title = data.get('job_title', '')
            company_name = data.get('company_name', '')
            batch_mode = data.get('batch_mode', False)
            single_mode = data.get('single_mode', False)
            agent_command = data.get('agent_command', '')
            generation_notes = data.get('generation_notes', '')
            
            # Check if this is a single variant request that should use batch-like processing
            if single_mode or (not batch_mode and agent_command):
                # Use the same mechanism as batch but for single variant
                batch_mode = True  # Force batch mode processing
                focus_type = agent_command or focus_type  # Use agent command as focus
                # Add generation notes to job description if provided
                if generation_notes:
                    job_description = f"{job_description}\n\nAdditional Instructions: {generation_notes}"
            
            # Create a unique job ID and start background processing
            job_id = str(uuid.uuid4())
            
            # Return immediately with job ID
            response = {
                "success": True,
                "job_id": job_id,
                "message": "Variant creation started",
                "status": "processing"
            }
            
            # Start background job
            variant_jobs[job_id] = {
                "status": "processing",
                "progress": "Starting AI generation...",
                "created_at": datetime.now().isoformat(),
                "job_data": {
                    "parent_variant": parent_variant,
                    "job_description": job_description,
                    "job_title": job_title,
                    "company_name": company_name,
                    "focus_type": focus_type,
                    "variant_name": variant_name
                }
            }
            
            print(f"📋 Creating variant with parent: {parent_variant}")
            print(f"   Job: {job_title} at {company_name}")
            print(f"   Variant name: {variant_name}")
            
            executor.submit(self.create_variant_background, job_id)
            
            self.send_response(202)  # 202 Accepted for async processing
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, default=str).encode())
            return
            
            # Fallback to rule-based variant creation
            from job_optimizer import JobResumeOptimizer
            from variant_manager import VariantManager
            
            # Determine parent file path
            if parent_variant.startswith('base_'):
                parent_path = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'templates', parent_variant)
            else:
                parent_path = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'variants', parent_variant)
            
            optimizer = JobResumeOptimizer(parent_path)
            manager = VariantManager(WORKSHOP_DIR)
            
            # Analyze job description
            job_analysis = optimizer.analyze_job_description(job_description)
            
            # Generate variant name if not provided
            if not variant_name:
                variant_name = manager.create_variant_name(
                    job_analysis.get('job_type', ''),
                    job_analysis.get('company', ''),
                    focus_type,
                    parent_variant
                )
            
            # Create optimized variant
            optimized_content = optimizer.optimize_resume(
                job_analysis,
                job_analysis.get('job_type', ''),
                job_analysis.get('company', '')
            )
            
            # Save variant
            variant_path = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'variants', variant_name)
            with open(variant_path, 'w', encoding='utf-8') as f:
                f.write(optimized_content)
            
            # Extract job title and company from job analysis for metadata
            extracted_title = job_analysis.get('job_type', '') or job_analysis.get('title', '')
            extracted_company = job_analysis.get('company', '')
            
            # Add parent metadata with job info
            manager.add_parent_metadata(variant_path, parent_variant, extracted_title, extracted_company)
            
            response = {
                "success": True,
                "variant_name": variant_name,
                "preview_url": f"/agent_workspace/variants/{variant_name}",
                "analysis": job_analysis,
                "message": "Variant created with rule-based optimizer (AI generation not available)",
                "ai_generated": False
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, default=str).encode())
            
        except Exception as e:
            self.send_error(500, f"Variant creation error: {str(e)}")
    
    def handle_create_hybrid(self):
        """Handle AI-powered hybrid variant creation from multiple parents"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            parents = data.get('parents', [])
            hybrid_name = data.get('hybrid_name', '')
            job_description = data.get('job_description', '')
            description = data.get('description', '')
            
            if len(parents) < 2:
                self.send_error(400, "At least 2 parents required for hybrid")
                return
            
            # Try AI-powered hybrid creation first
            import sys
            sys.path.append(os.path.join(WORKSHOP_DIR, 'agent_workspace', 'scripts'))
            
            try:
                from ai_variant_builder import AIVariantBuilder
                
                # Initialize AI builder
                ai_builder = AIVariantBuilder(os.path.join(WORKSHOP_DIR, 'agent_workspace'))
                
                # Create AI-powered hybrid
                ai_result = ai_builder.create_ai_hybrid(
                    parent_files=parents,
                    job_description=job_description,
                    hybrid_name=hybrid_name,
                    description=description
                )
                
                if ai_result['success']:
                    response = {
                        "success": True,
                        "hybrid_name": ai_result['hybrid_name'],
                        "preview_url": f"/agent_workspace/variants/{ai_result['hybrid_name']}",
                        "parents": ai_result['parent_files'],
                        "description": ai_result['description'],
                        "message": "AI-powered hybrid variant created successfully",
                        "ai_generated": True
                    }
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(response, default=str).encode())
                    return
                else:
                    print(f"AI hybrid creation failed: {ai_result['error']}")
                    # Fall back to simple hybrid system
                    
            except Exception as ai_error:
                print(f"AI hybrid builder error: {ai_error}")
                # Fall back to simple hybrid system
            
            # Fallback to simple hybrid creation
            # Read first parent as base
            first_parent = parents[0]
            if first_parent.startswith('base_'):
                parent_path = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'templates', first_parent)
            else:
                parent_path = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'variants', first_parent)
            
            with open(parent_path, 'r', encoding='utf-8') as f:
                hybrid_content = f.read()
            
            # Analyze job description if provided
            job_title = ''
            job_company = ''
            if job_description:
                # Import job optimizer for analysis
                from job_optimizer import JobResumeOptimizer
                
                optimizer = JobResumeOptimizer(parent_path)
                job_analysis = optimizer.analyze_job_description(job_description)
                job_title = job_analysis.get('job_type', '') or job_analysis.get('title', '')
                job_company = job_analysis.get('company', '')
            
            # Add hybrid metadata
            parent_list = ', '.join(parents)
            timestamp = datetime.now().isoformat()
            
            job_metadata = ''
            if job_title:
                job_metadata += f'<!-- JOB_TITLE: {job_title} -->\n'
            if job_company:
                job_metadata += f'<!-- JOB_COMPANY: {job_company} -->\n'
            
            hybrid_metadata = f"""<!-- PARENTS: {parent_list} -->
<!-- GENERATION: 2 -->
<!-- VARIANT_TYPE: Multi-Parent Hybrid -->
<!-- VARIANT_DESC: Simple hybrid combining features from: {parent_list} -->
<!-- GENERATED: {timestamp} -->
{job_metadata}"""
            
            # Insert metadata after <head>
            head_pos = hybrid_content.find('<head>') + 6
            hybrid_content = hybrid_content[:head_pos] + '\n    ' + hybrid_metadata + hybrid_content[head_pos:]
            
            # Generate hybrid name if not provided
            if not hybrid_name:
                timestamp_short = datetime.now().strftime("%m%d_%H%M")
                hybrid_name = f"hybrid_{timestamp_short}.html"
            
            # Save hybrid variant
            hybrid_path = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'variants', hybrid_name)
            with open(hybrid_path, 'w', encoding='utf-8') as f:
                f.write(hybrid_content)
            
            response = {
                "success": True,
                "hybrid_name": hybrid_name,
                "preview_url": f"/agent_workspace/variants/{hybrid_name}",
                "parents": parents,
                "message": "Simple hybrid variant created (AI generation not available)",
                "ai_generated": False
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, f"Hybrid creation error: {str(e)}")
    
    def handle_save_job_description(self):
        """Handle saving job description"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            job_content = data.get('content', '')
            job_name = data.get('name', '')
            is_main = data.get('is_main', False)
            
            if is_main:
                # Save as main job description
                job_file = os.path.join(WORKSHOP_DIR, '..', 'job_description.txt')
            else:
                # Save as named job description
                job_descriptions_dir = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'job_descriptions')
                os.makedirs(job_descriptions_dir, exist_ok=True)
                
                if not job_name:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    job_name = f"job_{timestamp}.txt"
                elif not job_name.endswith('.txt'):
                    job_name += '.txt'
                
                job_file = os.path.join(job_descriptions_dir, job_name)
            
            with open(job_file, 'w', encoding='utf-8') as f:
                f.write(job_content)
            
            response = {
                "success": True,
                "filename": os.path.basename(job_file),
                "path": job_file,
                "message": "Job description saved successfully"
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, f"Save job description error: {str(e)}")
    
    def handle_delete_job_description(self):
        """Handle deleting job description"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            filename = data.get('filename', '')
            
            if not filename:
                self.send_error(400, "Filename required")
                return
            
            # Determine if it's the main job description or a named one
            if filename == 'job_description.txt':
                # Delete main job description
                job_file = os.path.join(WORKSHOP_DIR, '..', 'job_description.txt')
            else:
                # Delete named job description
                job_descriptions_dir = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'job_descriptions')
                job_file = os.path.join(job_descriptions_dir, filename)
            
            # Check if file exists
            if not os.path.exists(job_file):
                self.send_error(404, f"Job description '{filename}' not found")
                return
            
            # Delete the file
            os.remove(job_file)
            
            response = {
                "success": True,
                "filename": filename,
                "message": f"Job description '{filename}' deleted successfully"
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, f"Delete job description error: {str(e)}")
    
    def handle_convert_to_pdf(self):
        """Handle PDF conversion request"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            variant_name = data.get('variant_name', '')
            
            if not variant_name:
                self.send_error(400, "Variant name required")
                return
            
            # Remove .html extension if present
            variant_name = variant_name.replace('.html', '')
            
            # Check if HTML file exists
            html_path = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'variants', f"{variant_name}.html")
            if not os.path.exists(html_path):
                self.send_error(404, f"Variant '{variant_name}' not found")
                return
            
            # Ensure output directory exists
            output_dir = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'output')
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate PDF using the converter script
            converter_script = os.path.join(WORKSHOP_DIR, 'scripts', 'pdf_converter.sh')
            try:
                print(f"Converting {variant_name} to PDF...")
                result = subprocess.run([
                    'bash', converter_script, variant_name
                ], cwd=WORKSHOP_DIR, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    pdf_path = os.path.join(output_dir, f"{variant_name}.pdf")
                    if os.path.exists(pdf_path):
                        response = {
                            "success": True,
                            "pdf_path": f"/agent_workspace/output/{variant_name}.pdf",
                            "message": "PDF generated successfully"
                        }
                    else:
                        raise Exception("PDF file not created despite successful conversion")
                else:
                    raise Exception(f"Conversion failed: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                raise Exception("PDF conversion timed out")
            except Exception as e:
                raise Exception(f"PDF conversion error: {str(e)}")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"PDF conversion error: {str(e)}")
            error_response = {
                "success": False,
                "message": str(e)
            }
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def handle_delete_variant(self):
        """Handle variant deletion request"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            # Handle case where post_data might contain HTML instead of JSON
            if post_data.strip().startswith('<!DOCTYPE'):
                self.send_error(400, "Invalid request format - received HTML instead of JSON")
                return
            
            data = json.loads(post_data)
            
            filename = data.get('filename', '')
            
            if not filename:
                self.send_error(400, "Filename required")
                return
            
            # Sanitize filename to prevent path traversal
            filename = os.path.basename(filename)
            
            # Construct variant file path
            variant_path = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'variants', filename)
            
            if not os.path.exists(variant_path):
                self.send_error(404, f"Variant '{filename}' not found")
                return
            
            # Check if file is actually within variants directory (security check)
            real_variant_path = os.path.realpath(variant_path)
            real_variants_dir = os.path.realpath(os.path.join(WORKSHOP_DIR, 'agent_workspace', 'variants'))
            
            if not real_variant_path.startswith(real_variants_dir):
                self.send_error(403, "Access denied - file outside variants directory")
                return
            
            # Delete the file
            os.remove(variant_path)
            print(f"Successfully deleted variant: {filename}")
            
            # Also delete corresponding PDF if it exists
            # Handle both .html and non-.html files
            if filename.endswith('.html'):
                pdf_filename = filename.replace('.html', '.pdf')
            else:
                pdf_filename = filename + '.pdf'
            
            pdf_path = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'output', pdf_filename)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                print(f"Also deleted corresponding PDF: {pdf_filename}")
            
            response = {
                "success": True,
                "filename": filename,
                "message": f"Variant '{filename}' deleted successfully"
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error in delete variant: {str(e)}")
            print(f"Received data: {post_data[:200]}...")
            error_response = {
                "success": False,
                "message": f"Invalid JSON format: {str(e)}"
            }
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
            
        except Exception as e:
            print(f"Delete variant error: {str(e)}")
            error_response = {
                "success": False,
                "message": str(e)
            }
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def handle_save_quality_feedback(self):
        """Handle saving quality feedback"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            feedback_data = json.loads(post_data)
            
            # Create quality feedback directory if it doesn't exist
            feedback_dir = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'quality_feedback')
            os.makedirs(feedback_dir, exist_ok=True)
            
            # Save feedback to file
            feedback_file = os.path.join(feedback_dir, f"{feedback_data['filename']}.json")
            with open(feedback_file, 'w', encoding='utf-8') as f:
                json.dump(feedback_data, f, indent=2)
            
            response = {
                "success": True,
                "message": "Quality feedback saved successfully"
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"Save quality feedback error: {str(e)}")
            error_response = {
                "success": False,
                "message": str(e)
            }
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def handle_analyze_quality_gap(self):
        """Handle quality gap analysis between variants"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            current_variant = data.get('current_variant', '')
            comparison_variant = data.get('comparison_variant', '')
            
            if not current_variant or not comparison_variant:
                self.send_error(400, "Both variant filenames required")
                return
            
            # Read both variant files
            variants_dir = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'variants')
            current_path = os.path.join(variants_dir, current_variant)
            comparison_path = os.path.join(variants_dir, comparison_variant)
            
            if not os.path.exists(current_path) or not os.path.exists(comparison_path):
                self.send_error(404, "One or both variants not found")
                return
            
            with open(current_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            with open(comparison_path, 'r', encoding='utf-8') as f:
                comparison_content = f.read()
            
            # Simple analysis - compare content length, structure, etc.
            differences = []
            recommendations = []
            
            # Compare content length
            current_length = len(current_content)
            comparison_length = len(comparison_content)
            if abs(current_length - comparison_length) > 1000:
                if current_length > comparison_length:
                    differences.append("Current variant is significantly longer")
                    recommendations.append("Consider condensing content for better single-page fit")
                else:
                    differences.append("Current variant is significantly shorter")
                    recommendations.append("Consider adding more relevant details and achievements")
            
            # Compare section structure
            current_sections = len([line for line in current_content.split('\n') if '<h' in line.lower()])
            comparison_sections = len([line for line in comparison_content.split('\n') if '<h' in line.lower()])
            if current_sections != comparison_sections:
                differences.append(f"Different number of sections ({current_sections} vs {comparison_sections})")
                recommendations.append("Align section structure with successful variant")
            
            # Check for common formatting patterns
            if 'style=' in comparison_content and 'style=' not in current_content:
                differences.append("High-quality variant uses more inline styling")
                recommendations.append("Consider adding professional formatting styles")
            
            # Basic keyword density comparison
            current_bullets = current_content.count('<li>')
            comparison_bullets = comparison_content.count('<li>')
            if abs(current_bullets - comparison_bullets) > 3:
                differences.append(f"Different content density ({current_bullets} vs {comparison_bullets} bullet points)")
                recommendations.append("Adjust content density to match successful examples")
            
            if not differences:
                differences.append("Variants appear structurally similar")
                recommendations.append("Focus on content quality and keyword optimization")
            
            response = {
                "success": True,
                "differences": differences,
                "recommendations": recommendations
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"Quality gap analysis error: {str(e)}")
            error_response = {
                "success": False,
                "message": str(e)
            }
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def serve_pdf_download(self):
        """Serve PDF files for download"""
        try:
            # Extract filename from path
            parsed_path = urlparse(self.path)
            filename = os.path.basename(parsed_path.path)
            
            output_dir = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'output')
            pdf_path = os.path.join(output_dir, filename)
            
            if not os.path.exists(pdf_path):
                # Try to generate PDF if it doesn't exist
                if filename.endswith('.pdf'):
                    html_filename = filename.replace('.pdf', '.html')
                    html_path = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'variants', html_filename)
                    
                    if os.path.exists(html_path):
                        # Generate PDF using the converter script
                        converter_script = os.path.join(WORKSHOP_DIR, 'scripts', 'pdf_converter.sh')
                        try:
                            result = subprocess.run([
                                'bash', converter_script, html_filename.replace('.html', '')
                            ], cwd=WORKSHOP_DIR, capture_output=True, text=True)
                            
                            if result.returncode == 0 and os.path.exists(pdf_path):
                                pass  # PDF generated successfully
                            else:
                                self.send_error(500, "PDF generation failed")
                                return
                        except Exception as e:
                            self.send_error(500, f"PDF generation error: {str(e)}")
                            return
                    else:
                        self.send_error(404, "Source HTML file not found")
                        return
                else:
                    self.send_error(404, "PDF file not found")
                    return
            
            # Serve the PDF file
            with open(pdf_path, 'rb') as f:
                pdf_content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/pdf')
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.send_header('Content-Length', str(len(pdf_content)))
            self.end_headers()
            self.wfile.write(pdf_content)
            
        except Exception as e:
            self.send_error(500, f"PDF download error: {str(e)}")
    
    def extract_variant_info(self, filepath):
        """Extract metadata from variant HTML file"""
        info = {
            'name': os.path.basename(filepath).replace('.html', '').replace('_', ' ').title(),
            'type': 'Custom',
            'description': 'Custom resume variant',
            'created': datetime.fromtimestamp(os.path.getctime(filepath)).isoformat(),
            'is_hybrid': False,
            'parents': [],
            'hybrid_features': ''
        }
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extract title if available
                if '<title>' in content:
                    title_start = content.find('<title>') + 7
                    title_end = content.find('</title>', title_start)
                    if title_end > title_start:
                        info['name'] = content[title_start:title_end].strip()
                
                # Look for special comment markers for metadata
                if '<!-- VARIANT_TYPE:' in content:
                    type_start = content.find('<!-- VARIANT_TYPE:') + 18
                    type_end = content.find('-->', type_start)
                    if type_end > type_start:
                        info['type'] = content[type_start:type_end].strip()
                
                if '<!-- VARIANT_DESC:' in content:
                    desc_start = content.find('<!-- VARIANT_DESC:') + 18
                    desc_end = content.find('-->', desc_start)
                    if desc_end > desc_start:
                        info['description'] = content[desc_start:desc_end].strip()
                
                # Extract hybrid-specific metadata
                if '<!-- PARENTS:' in content:
                    parents_start = content.find('<!-- PARENTS:') + 13
                    parents_end = content.find('-->', parents_start)
                    if parents_end > parents_start:
                        parents_str = content[parents_start:parents_end].strip()
                        info['parents'] = [p.strip() for p in parents_str.split(',')]
                        info['is_hybrid'] = True
                        
                if '<!-- HYBRID_FEATURES:' in content:
                    features_start = content.find('<!-- HYBRID_FEATURES:') + 21
                    features_end = content.find('-->', features_start)
                    if features_end > features_start:
                        info['hybrid_features'] = content[features_start:features_end].strip()
                
                # Extract generation metadata
                if '<!-- GENERATION:' in content:
                    gen_start = content.find('<!-- GENERATION:') + 16
                    gen_end = content.find('-->', gen_start)
                    if gen_end > gen_start:
                        try:
                            info['generation'] = int(content[gen_start:gen_end].strip())
                        except ValueError:
                            pass  # Use default if not a valid number
                
                # Extract job description metadata
                if '<!-- JOB_TITLE:' in content:
                    job_title_start = content.find('<!-- JOB_TITLE:') + 15
                    job_title_end = content.find('-->', job_title_start)
                    if job_title_end > job_title_start:
                        info['job_title'] = content[job_title_start:job_title_end].strip()
                        
                if '<!-- JOB_COMPANY:' in content:
                    job_company_start = content.find('<!-- JOB_COMPANY:') + 17
                    job_company_end = content.find('-->', job_company_start)
                    if job_company_end > job_company_start:
                        info['job_company'] = content[job_company_start:job_company_end].strip()
        
        except Exception:
            pass  # Use defaults if extraction fails
        
        return info
    
    def end_headers(self):
        """Add no-cache headers for HTML files"""
        if hasattr(self, 'path') and self.path.endswith('.html'):
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        super().end_headers()

class ResumeWorkshopServer:
    def __init__(self, port=PORT):
        self.port = port
        self.httpd = None
        self.server_thread = None
    
    def start(self):
        """Start the server in a separate thread"""
        try:
            self.httpd = socketserver.TCPServer(("", self.port), ResumeWorkshopHandler)
            self.server_thread = threading.Thread(target=self.httpd.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            print(f"🚀 Resume Workshop Server started!")
            print(f"📍 Server running at: http://localhost:{self.port}")
            print(f"🏠 Workshop home: http://localhost:{self.port}")
            print(f"📄 Base template: http://localhost:{self.port}/agent_workspace/templates/base_resume.html")
            print(f"📁 Variants: http://localhost:{self.port}/agent_workspace/variants/")
            print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("\n" + "="*60)
            
            return True
            
        except OSError as e:
            if e.errno == 48:  # Address already in use
                print(f"⚠️  Port {self.port} is already in use!")
                print(f"🔗 Workshop likely running at: http://localhost:{self.port}")
                return False
            else:
                print(f"❌ Error starting server: {e}")
                return False
    
    def stop(self):
        """Stop the server"""
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            print(f"🛑 Server stopped")
    
    def is_running(self):
        """Check if server is running"""
        return self.httpd is not None and self.server_thread.is_alive()

def create_sample_variants():
    """Create sample variants for demonstration"""
    variants_dir = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'variants')
    os.makedirs(variants_dir, exist_ok=True)
    
    # Read base template
    base_path = os.path.join(WORKSHOP_DIR, 'agent_workspace', 'templates', 'base_resume.html')
    if not os.path.exists(base_path):
        print(f"⚠️  Base template not found at {base_path}")
        return
    
    with open(base_path, 'r', encoding='utf-8') as f:
        base_content = f.read()
    
    # Sample variant 1: Tech-focused
    tech_variant = base_content.replace(
        '<title>Enrico Patarini - Resume</title>',
        '<!-- VARIANT_TYPE: Tech Focus -->\n<!-- VARIANT_DESC: Emphasizes technical architecture and development leadership -->\n<title>Enrico Patarini - Senior Software Engineer</title>'
    )
    
    with open(os.path.join(variants_dir, 'tech_focused.html'), 'w', encoding='utf-8') as f:
        f.write(tech_variant)
    
    print(f"✅ Sample variants created in {variants_dir}")

if __name__ == "__main__":
    # Create directories if they don't exist
    for subdir in ['agent_workspace/templates', 'agent_workspace/variants', 'agent_workspace/output', 'agent_workspace/scripts', 'scripts']:
        os.makedirs(os.path.join(WORKSHOP_DIR, subdir), exist_ok=True)
    
    # Create sample variants
    create_sample_variants()
    
    # Start server
    server = ResumeWorkshopServer(PORT)
    
    if server.start():
        try:
            print("🔄 Server running... Press Ctrl+C to stop")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down server...")
            server.stop()
    else:
        print("⚠️  Server may already be running. Try visiting the workshop URL above.")