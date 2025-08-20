#!/usr/bin/env python3
"""
Genealogy API handlers
"""

import os
import json
import sys
from ..core.config import WORKSHOP_DIR


class GenealogyAPI:
    """Handles genealogy tree-related API endpoints"""
    
    @staticmethod
    def get_genealogy_tree(handler):
        """Handle GET /api/genealogy"""
        try:
            # Try to import variant manager
            sys.path.append(os.path.join(WORKSHOP_DIR, 'agent_workspace', 'scripts'))
            
            try:
                from variant_manager import VariantManager
                
                manager = VariantManager(os.path.join(WORKSHOP_DIR, 'agent_workspace'))
                tree = manager.create_genealogy_tree()
                
                handler.send_json_response(tree)
                
            except ImportError as e:
                # If variant_manager is not available, create a simple tree from existing variants
                print(f"VariantManager not available: {e}")
                simple_tree = GenealogyAPI._create_simple_tree()
                handler.send_json_response(simple_tree)
                
        except Exception as e:
            handler.send_error_response(500, f"Genealogy tree error: {str(e)}")
    
    @staticmethod
    def _create_simple_tree():
        """Create a simple tree structure from available variant files"""
        from ..core.config import VARIANTS_DIR
        from ..utils.metadata_parser import extract_variant_info
        
        tree = {}
        
        if not os.path.exists(VARIANTS_DIR):
            return tree
        
        try:
            for filename in os.listdir(VARIANTS_DIR):
                if filename.endswith('.html'):
                    filepath = os.path.join(VARIANTS_DIR, filename)
                    variant_info = extract_variant_info(filepath)
                    
                    # Create tree node
                    tree[filename] = {
                        'name': variant_info.get('name', filename),
                        'type': variant_info.get('type', 'Unknown'),
                        'description': variant_info.get('description', ''),
                        'created': variant_info.get('created', ''),
                        'generation': variant_info.get('generation', 0),
                        'is_hybrid': variant_info.get('is_hybrid', False),
                        'parents': variant_info.get('parents', []),
                        'job_title': variant_info.get('job_title', ''),
                        'job_company': variant_info.get('job_company', '')
                    }
            
        except Exception as e:
            print(f"Error creating simple tree: {e}")
        
        return tree