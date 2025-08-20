#!/usr/bin/env python3
"""
HTML metadata extraction utilities
"""

import os
from datetime import datetime


def extract_variant_info(filepath):
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
                        pass
            
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