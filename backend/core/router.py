#!/usr/bin/env python3
"""
Route handler for modular server
"""

from urllib.parse import urlparse
from ..handlers.base_handler import BaseHandler
from ..api.variants import VariantsAPI
from ..api.job_descriptions import JobDescriptionsAPI
from ..api.linkedin import LinkedInAPI
from ..api.genealogy import GenealogyAPI
from ..services.background_jobs import background_service


class ModularHandler(BaseHandler):
    """Main request handler with modular routing"""
    
    def do_HEAD(self):
        """Handle HEAD requests - delegate to GET but don't send body"""
        self._head_request = True
        self.do_GET()
        
    def do_GET(self):
        """Handle GET requests with modular routing"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        head_request = getattr(self, '_head_request', False)
        
        # API routes - lazy load modules only when needed
        if path == '/api/variants':
            VariantsAPI.get_variants_list(self)
            return
        elif path == '/api/job-descriptions':
            JobDescriptionsAPI.get_job_descriptions(self)
            return
        elif path == '/api/fetch-linkedin':
            LinkedInAPI.fetch_linkedin_job(self)
            return
        elif path == '/api/genealogy':
            GenealogyAPI.get_genealogy_tree(self)
            return
        elif path == '/api/variant-status':
            self._serve_variant_status()
            return
        elif path == '/api/generate-pdf':
            self._handle_pdf_generation()
            return
        
        # Serve frontend files
        elif path == '/' or path == '':
            self.path = '/frontend/index.html'
        elif path.startswith('/frontend/'):
            # Allow direct access to frontend files
            pass
        
        # Agent workspace files (variants, PDFs, etc.)
        elif path.startswith('/agent_workspace/'):
            # Check if it's a PDF request that might need generation
            if path.endswith('.pdf') and '/output/' in path:
                self._serve_pdf_with_generation()
                return
            else:
                # Strip the leading slash and serve from workshop directory
                self.path = path[1:]  # Remove leading slash
                super().do_GET()
                return
            
        # Legacy PDF downloads
        elif path.startswith('/output/'):
            self.path = f'/agent_workspace{path}'
            super().do_GET()
            return
        
        # Default static file handling
        super().do_GET()
    
    def do_POST(self):
        """Handle POST requests with modular routing"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Route to appropriate API handlers
        if path == '/api/delete-variant':
            VariantsAPI.delete_variant(self)
        elif path == '/api/save-job-description':
            JobDescriptionsAPI.save_job_description(self)
        elif path == '/api/delete-job-description':
            JobDescriptionsAPI.delete_job_description(self)
        elif path == '/api/create-variant':
            self._handle_create_variant()
        else:
            self.send_error(404, "API endpoint not found")
    
    def _serve_variant_status(self):
        """Serve variant status updates for polling"""
        try:
            status_updates = background_service.get_all_statuses()
            self.send_json_response(status_updates)
        except Exception as e:
            self.send_error_response(500, f"Variant status error: {str(e)}")
    
    def _handle_create_variant(self):
        """Handle variant creation with background processing"""
        try:
            data = self.get_post_data()
            
            # Extract parameters
            parent_variant = data.get('parent') or data.get('parent_template') or 'base_resume_v2.html'
            job_description = data.get('job_description', '')
            focus_type = data.get('focus_type', '')
            variant_name = data.get('variant_name', '')
            job_title = data.get('job_title', '')
            company_name = data.get('company_name', '')
            
            # Create background job
            job_data = {
                "parent_variant": parent_variant,
                "job_description": job_description,
                "job_title": job_title,
                "company_name": company_name,
                "focus_type": focus_type,
                "variant_name": variant_name
            }
            
            job_id = background_service.create_job(job_data)
            
            response = {
                "success": True,
                "job_id": job_id,
                "message": "Variant creation started",
                "status": "processing"
            }
            
            self.send_json_response(response, 202)  # 202 Accepted
            
        except Exception as e:
            self.send_error_response(500, f"Variant creation error: {str(e)}")
    
    def _serve_pdf_with_generation(self):
        """Serve PDF files, generating them on-demand if needed"""
        import os
        import subprocess
        from ..core.config import WORKSHOP_DIR, OUTPUT_DIR, VARIANTS_DIR
        
        try:
            # Extract filename from path
            path_parts = self.path.split('/')
            filename = path_parts[-1]
            
            pdf_path = os.path.join(OUTPUT_DIR, filename)
            
            if not os.path.exists(pdf_path):
                # Try to generate PDF if it doesn't exist
                if filename.endswith('.pdf'):
                    html_filename = filename.replace('.pdf', '.html')
                    html_path = os.path.join(VARIANTS_DIR, html_filename)
                    
                    if os.path.exists(html_path):
                        print(f"🔄 Generating PDF for {html_filename}...")
                        # Generate PDF using the converter script
                        converter_script = os.path.join(WORKSHOP_DIR, 'scripts', 'pdf_converter.sh')
                        
                        try:
                            # Run PDF conversion - script expects filename without .html extension
                            variant_base_name = html_filename.replace('.html', '')
                            result = subprocess.run([
                                'bash', converter_script, variant_base_name
                            ], cwd=WORKSHOP_DIR, capture_output=True, text=True, timeout=30)
                            
                            if result.returncode == 0 and os.path.exists(pdf_path):
                                print(f"✅ PDF generated successfully: {filename}")
                            else:
                                print(f"❌ PDF generation failed for {filename}: {result.stderr}")
                                self.send_error(500, "PDF generation failed")
                                return
                        except subprocess.TimeoutExpired:
                            self.send_error(500, "PDF generation timed out")
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
            file_size = os.path.getsize(pdf_path)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/pdf')
            self.send_header('Content-Disposition', f'inline; filename="{filename}"')
            self.send_header('Content-Length', str(file_size))
            self.end_headers()
            
            # Only send content for GET requests, not HEAD
            head_request = getattr(self, '_head_request', False)
            if not head_request:
                with open(pdf_path, 'rb') as f:
                    pdf_content = f.read()
                self.wfile.write(pdf_content)
            
        except Exception as e:
            print(f"❌ PDF serving error: {str(e)}")
            self.send_error(500, f"PDF download error: {str(e)}")
    
    def _handle_pdf_generation(self):
        """Handle manual PDF generation requests"""
        import os
        import subprocess
        from ..core.config import WORKSHOP_DIR, OUTPUT_DIR, VARIANTS_DIR
        
        try:
            # Get query parameters
            query_params = self.get_query_params()
            variant_name = query_params.get('variant', [''])[0]
            
            if not variant_name:
                self.send_error_response(400, "Variant name required")
                return
            
            # Ensure .html extension
            if not variant_name.endswith('.html'):
                variant_name += '.html'
            
            html_path = os.path.join(VARIANTS_DIR, variant_name)
            
            if not os.path.exists(html_path):
                self.send_error_response(404, f"Variant '{variant_name}' not found")
                return
            
            pdf_name = variant_name.replace('.html', '.pdf')
            pdf_path = os.path.join(OUTPUT_DIR, pdf_name)
            
            print(f"🔄 Generating PDF for {variant_name}...")
            
            # Generate PDF using the converter script
            converter_script = os.path.join(WORKSHOP_DIR, 'scripts', 'pdf_converter.sh')
            
            try:
                # Run PDF conversion - script expects filename without .html extension
                variant_base_name = variant_name.replace('.html', '')
                result = subprocess.run([
                    'bash', converter_script, variant_base_name
                ], cwd=WORKSHOP_DIR, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0 and os.path.exists(pdf_path):
                    print(f"✅ PDF generated successfully: {pdf_name}")
                    
                    response = {
                        "success": True,
                        "message": f"PDF generated successfully for {variant_name}",
                        "pdf_path": f"/agent_workspace/output/{pdf_name}",
                        "pdf_name": pdf_name
                    }
                    self.send_json_response(response)
                else:
                    print(f"❌ PDF generation failed for {variant_name}: {result.stderr}")
                    self.send_error_response(500, f"PDF generation failed: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                self.send_error_response(500, "PDF generation timed out")
            except Exception as e:
                self.send_error_response(500, f"PDF generation error: {str(e)}")
                
        except Exception as e:
            print(f"❌ PDF generation request error: {str(e)}")
            self.send_error_response(500, f"PDF generation request error: {str(e)}")
    
