#!/usr/bin/env python3
"""
Variants API handlers
"""

import os
import json
from datetime import datetime
from ..core.config import VARIANTS_DIR, TEMPLATES_DIR
from ..utils.metadata_parser import extract_variant_info


class VariantsAPI:
    """Handles variant-related API endpoints"""
    
    @staticmethod
    def get_variants_list(handler):
        """Handle GET /api/variants"""
        try:
            variants = []
            
            if os.path.exists(VARIANTS_DIR):
                for filename in os.listdir(VARIANTS_DIR):
                    if filename.endswith('.html'):
                        variant_info = extract_variant_info(
                            os.path.join(VARIANTS_DIR, filename)
                        )
                        variant_info['filename'] = filename
                        variants.append(variant_info)
            
            # Sort by creation time (newest first)
            variants.sort(key=lambda x: x.get('created', ''), reverse=True)
            
            handler.send_json_response(variants)
            
        except Exception as e:
            handler.send_error_response(500, f"Error reading variants: {str(e)}")
    
    @staticmethod
    def delete_variant(handler):
        """Handle POST /api/delete-variant"""
        try:
            data = handler.get_post_data()
            filename = data.get('filename', '')
            
            if not filename:
                handler.send_error_response(400, "Filename required")
                return
            
            # Sanitize filename to prevent path traversal
            filename = os.path.basename(filename)
            
            # Construct variant file path
            variant_path = os.path.join(VARIANTS_DIR, filename)
            
            if not os.path.exists(variant_path):
                handler.send_error_response(404, f"Variant '{filename}' not found")
                return
            
            # Security check
            real_variant_path = os.path.realpath(variant_path)
            real_variants_dir = os.path.realpath(VARIANTS_DIR)
            
            if not real_variant_path.startswith(real_variants_dir):
                handler.send_error_response(403, "Access denied - file outside variants directory")
                return
            
            # Delete the file
            os.remove(variant_path)
            print(f"Successfully deleted variant: {filename}")
            
            # Also delete corresponding PDF if it exists
            from ..core.config import OUTPUT_DIR
            if filename.endswith('.html'):
                pdf_filename = filename.replace('.html', '.pdf')
            else:
                pdf_filename = filename + '.pdf'
            
            pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                print(f"Also deleted corresponding PDF: {pdf_filename}")
            
            response = {
                "success": True,
                "filename": filename,
                "message": f"Variant '{filename}' deleted successfully"
            }
            
            handler.send_json_response(response)
            
        except json.JSONDecodeError as e:
            handler.send_error_response(400, f"Invalid JSON format: {str(e)}")
        except Exception as e:
            handler.send_error_response(500, str(e))