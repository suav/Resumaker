#!/usr/bin/env python3
"""
LinkedIn API handlers
"""

import subprocess
import re
from ..core.config import LINKEDIN_SUPPORT


class LinkedInAPI:
    """Handles LinkedIn-related API endpoints"""
    
    @staticmethod
    def fetch_linkedin_job(handler):
        """Handle GET /api/fetch-linkedin"""
        try:
            query_params = handler.get_query_params()
            linkedin_url = query_params.get('url', [''])[0]
            
            if not linkedin_url:
                handler.send_error_response(400, "LinkedIn URL required")
                return
            
            # Extract job ID from URL
            job_id = None
            if '/jobs/view/' in linkedin_url:
                try:
                    job_id = linkedin_url.split('/jobs/view/')[-1].split('?')[0].split('/')[0]
                except:
                    pass
            
            # Default values
            job_title = "Software Engineer"
            company_name = "Target Company"
            location = "Remote/Hybrid"
            full_job_content = ""
            
            try:
                # Use curl to fetch the page
                headers = [
                    '-H', 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    '-H', 'Accept-Language: en-US,en;q=0.5',
                    '-H', 'Connection: keep-alive',
                    '-H', 'Upgrade-Insecure-Requests: 1'
                ]
                
                curl_cmd = ['curl', '-s', '-L', '--compressed', '--max-redirs', '3', 
                           '--connect-timeout', '5', '--max-time', '8'] + headers + [linkedin_url]
                result_curl = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=8)
                
                if result_curl.returncode == 0:
                    html_content = result_curl.stdout
                    
                    # Extract job title
                    title_patterns = [
                        r'<title>([^|]+?)(?:\s*\|\s*LinkedIn)?</title>',
                        r'"jobTitle":"([^"]+)"',
                        r'<h1[^>]*class="[^"]*job[^"]*title[^"]*"[^>]*>([^<]+)</h1>',
                    ]
                    
                    for pattern in title_patterns:
                        match = re.search(pattern, html_content, re.IGNORECASE)
                        if match:
                            extracted_title = match.group(1).strip()
                            if len(extracted_title) > 5 and len(extracted_title) < 150:
                                if ' hiring ' in extracted_title:
                                    parts = extracted_title.split(' hiring ')
                                    if len(parts) == 2:
                                        company_name = parts[0].strip()
                                        title_location = parts[1].strip()
                                        if ' in ' in title_location:
                                            title_part, location_part = title_location.split(' in ', 1)
                                            job_title = title_part.strip()
                                            location = location_part.replace(' | LinkedIn', '').strip()
                                        else:
                                            job_title = title_location
                                        break
                                else:
                                    job_title = extracted_title
                                    break
                    
                    # Extract company name if not found above
                    if company_name == "Target Company":
                        company_patterns = [
                            r'"companyName":"([^"]+)"',
                            r'"hiringOrganization":\s*\{\s*"name":"([^"]+)"',
                            r'<span[^>]*class="[^"]*company[^"]*"[^>]*>([^<]+)</span>',
                        ]
                        
                        for pattern in company_patterns:
                            match = re.search(pattern, html_content, re.IGNORECASE)
                            if match:
                                extracted_company = match.group(1).strip()
                                if len(extracted_company) > 2 and len(extracted_company) < 50:
                                    company_name = extracted_company
                                    break
                    
                    # Extract job description content
                    job_section_patterns = [
                        r'<div class="show-more-less-html__markup[^"]*"[^>]*>(.*?)</div>',
                        r'<section class="show-more-less-html"[^>]*>.*?<div[^>]*class="show-more-less-html__markup[^"]*"[^>]*>(.*?)</div>',
                    ]
                    
                    for pattern in job_section_patterns:
                        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
                        if match:
                            job_html = match.group(1)
                            
                            # Convert HTML to readable text
                            job_text = re.sub(r'<br[^>]*>', '\n', job_html)
                            job_text = re.sub(r'<li[^>]*>', '\n• ', job_text)
                            job_text = re.sub(r'</li>', '', job_text)
                            job_text = re.sub(r'<ul[^>]*>', '\n', job_text)
                            job_text = re.sub(r'</ul>', '\n', job_text)
                            job_text = re.sub(r'<p[^>]*>', '\n\n', job_text)
                            job_text = re.sub(r'</p>', '', job_text)
                            job_text = re.sub(r'<strong[^>]*>', '**', job_text)
                            job_text = re.sub(r'</strong>', '**', job_text)
                            job_text = re.sub(r'<[^>]+>', '', job_text)
                            
                            # Clean up whitespace
                            job_text = re.sub(r'\n\s*\n\s*\n', '\n\n', job_text)
                            job_text = re.sub(r'[ \t]+', ' ', job_text)
                            job_text = re.sub(r' \n', '\n', job_text)
                            
                            # Decode HTML entities
                            job_text = job_text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")
                            
                            full_job_content = job_text.strip()
                            break
                
            except Exception as fetch_error:
                print(f"LinkedIn fetch error: {fetch_error}")
            
            # Create template content
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
            else:
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
"""
            
            result = {
                "success": True,
                "title": job_title,
                "company": company_name,
                "location": location,
                "job_id": job_id,
                "content": template_content,
                "url": linkedin_url,
                "extraction_note": "Basic details extracted. Please copy full job description for optimal results."
            }
            
            handler.send_json_response(result)
            
        except Exception as e:
            result = {
                "success": False,
                "error": f"LinkedIn processing error: {str(e)}",
                "message": "Please copy and paste the job description manually"
            }
            handler.send_json_response(result)