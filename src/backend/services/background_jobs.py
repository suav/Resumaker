#!/usr/bin/env python3
"""
Background job management service
"""

import uuid
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from ..core.config import MAX_WORKERS, WORKSHOP_DIR


class BackgroundJobService:
    """Manages background variant creation jobs"""
    
    def __init__(self):
        self.variant_jobs = {}
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
    
    def create_job(self, job_data):
        """Create a new background job"""
        job_id = str(uuid.uuid4())
        
        self.variant_jobs[job_id] = {
            "status": "processing",
            "progress": "Starting AI generation...",
            "created_at": datetime.now().isoformat(),
            "job_data": job_data
        }
        
        # Submit job to executor
        self.executor.submit(self._process_variant_job, job_id)
        
        return job_id
    
    def get_job_status(self, job_id):
        """Get status of a specific job"""
        return self.variant_jobs.get(job_id)
    
    def get_all_statuses(self):
        """Get status of all jobs"""
        status_updates = []
        
        for job_id, job_info in self.variant_jobs.items():
            status_updates.append({
                "job_id": job_id,
                "status": job_info["status"],
                "progress": job_info["progress"],
                "created_at": job_info["created_at"],
                "result": job_info.get("result"),
                "error": job_info.get("error")
            })
        
        return status_updates
    
    def _process_variant_job(self, job_id):
        """Background method to create variant with AI"""
        try:
            job_data = self.variant_jobs[job_id]["job_data"]
            
            # Update progress
            self.variant_jobs[job_id]["progress"] = "Initializing AI builder..."
            
            # Try AI-powered variant creation
            import sys
            import os
            sys.path.append(os.path.join(WORKSHOP_DIR, 'agent_workspace', 'scripts'))
            
            try:
                from ai_variant_builder import AIVariantBuilder
                
                self.variant_jobs[job_id]["progress"] = "Loading AI builder..."
                ai_builder = AIVariantBuilder(os.path.join(WORKSHOP_DIR, 'agent_workspace'))
                
                self.variant_jobs[job_id]["progress"] = "Running AI generation (this may take 2-5 minutes)..."
                
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
                    self.variant_jobs[job_id].update({
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
                    self.variant_jobs[job_id].update({
                        "status": "failed",
                        "progress": f"AI generation failed: {ai_result.get('error', 'Unknown error')}",
                        "error": ai_result.get('error', 'Unknown error')
                    })
                    print(f"❌ Background job {job_id} failed: {ai_result.get('error')}")
                    
            except Exception as ai_error:
                self.variant_jobs[job_id].update({
                    "status": "failed",
                    "progress": f"AI builder error: {str(ai_error)}",
                    "error": str(ai_error)
                })
                print(f"❌ Background job {job_id} AI error: {ai_error}")
                
        except Exception as e:
            self.variant_jobs[job_id].update({
                "status": "failed",
                "progress": f"Background processing error: {str(e)}",
                "error": str(e)
            })
            print(f"❌ Background job {job_id} error: {e}")


# Global instance
background_service = BackgroundJobService()