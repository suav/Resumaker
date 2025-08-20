#!/usr/bin/env python3
"""
Job descriptions API handlers
"""

import os
import json
from datetime import datetime
from ..core.config import WORKSHOP_DIR, JOB_DESCRIPTIONS_DIR


class JobDescriptionsAPI:
    """Handles job description-related API endpoints"""
    
    @staticmethod
    def get_job_descriptions(handler):
        """Handle GET /api/job-descriptions"""
        try:
            os.makedirs(JOB_DESCRIPTIONS_DIR, exist_ok=True)
            
            job_descriptions = []
            for filename in os.listdir(JOB_DESCRIPTIONS_DIR):
                if filename.endswith('.txt'):
                    job_path = os.path.join(JOB_DESCRIPTIONS_DIR, filename)
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
            
            handler.send_json_response(job_descriptions)
            
        except Exception as e:
            handler.send_error_response(500, f"Error reading job descriptions: {str(e)}")
    
    @staticmethod
    def save_job_description(handler):
        """Handle POST /api/save-job-description"""
        try:
            data = handler.get_post_data()
            
            job_content = data.get('content', '')
            job_name = data.get('name', '')
            is_main = data.get('is_main', False)
            
            if is_main:
                # Save as main job description
                job_file = os.path.join(WORKSHOP_DIR, '..', 'job_description.txt')
            else:
                # Save as named job description
                os.makedirs(JOB_DESCRIPTIONS_DIR, exist_ok=True)
                
                if not job_name:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    job_name = f"job_{timestamp}.txt"
                elif not job_name.endswith('.txt'):
                    job_name += '.txt'
                
                job_file = os.path.join(JOB_DESCRIPTIONS_DIR, job_name)
            
            with open(job_file, 'w', encoding='utf-8') as f:
                f.write(job_content)
            
            response = {
                "success": True,
                "filename": os.path.basename(job_file),
                "path": job_file,
                "message": "Job description saved successfully"
            }
            
            handler.send_json_response(response)
            
        except Exception as e:
            handler.send_error_response(500, f"Save job description error: {str(e)}")
    
    @staticmethod
    def delete_job_description(handler):
        """Handle POST /api/delete-job-description"""
        try:
            data = handler.get_post_data()
            filename = data.get('filename', '')
            
            if not filename:
                handler.send_error_response(400, "Filename required")
                return
            
            # Determine if it's the main job description or a named one
            if filename == 'job_description.txt':
                job_file = os.path.join(WORKSHOP_DIR, '..', 'job_description.txt')
            else:
                job_file = os.path.join(JOB_DESCRIPTIONS_DIR, filename)
            
            # Check if file exists
            if not os.path.exists(job_file):
                handler.send_error_response(404, f"Job description '{filename}' not found")
                return
            
            # Delete the file
            os.remove(job_file)
            
            response = {
                "success": True,
                "filename": filename,
                "message": f"Job description '{filename}' deleted successfully"
            }
            
            handler.send_json_response(response)
            
        except Exception as e:
            handler.send_error_response(500, f"Delete job description error: {str(e)}")