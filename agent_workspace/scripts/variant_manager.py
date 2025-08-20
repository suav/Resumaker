#!/usr/bin/env python3
"""
Resume Variant Manager
Creates better naming and selection process for resume variants
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

class VariantManager:
    def __init__(self, workshop_dir):
        self.workshop_dir = Path(workshop_dir)
        
        # Check if workshop_dir points to agent_workspace or main workshop
        if (self.workshop_dir / 'variants').exists():
            # workshop_dir is agent_workspace
            self.variants_dir = self.workshop_dir / 'variants'
            self.templates_dir = self.workshop_dir / 'templates'
            self.job_file = self.workshop_dir.parent / 'job_description.txt'
        else:
            # workshop_dir is main workshop, variants are in agent_workspace
            self.variants_dir = self.workshop_dir / 'agent_workspace' / 'variants'
            self.templates_dir = self.workshop_dir / 'agent_workspace' / 'templates'
            self.job_file = self.workshop_dir / 'job_description.txt'
        
    def create_variant_name(self, job_title="", company="", focus_type="", parent_variant="", generation=None):
        """Create descriptive variant filename based on job details and genealogy"""
        
        # Read job description if no details provided
        if not job_title or not company:
            job_info = self.extract_job_info()
            job_title = job_info.get('title', job_title)
            company = job_info.get('company', company)
        
        # Clean and format components
        company_clean = re.sub(r'[^a-zA-Z0-9]', '', company.lower())[:15]
        title_clean = re.sub(r'[^a-zA-Z0-9]', '', job_title.lower().replace('engineer', 'eng').replace('software', 'sw').replace('senior', 'sr'))[:20]
        
        # Determine generation
        if generation is None:
            generation = self.get_next_generation(parent_variant)
        
        # Add focus type if specified
        focus_suffix = f"_{focus_type}" if focus_type else ""
        
        # Create timestamp for uniqueness
        timestamp = datetime.now().strftime("%m%d_%H%M")
        
        # Get parent info for clearer naming
        parent_info = ""
        if parent_variant:
            parent_name = parent_variant.replace('.html', '').replace('base_', '')
            parent_short = re.sub(r'[^a-zA-Z0-9]', '', parent_name)[:10]
            parent_info = f"_{parent_short}" if parent_short else ""
        
        # Generate filename with clearer hierarchy indication
        if company_clean and title_clean:
            # Full job-targeted name: gen2_parentname_company_title_focus_timestamp
            return f"gen{generation}{parent_info}_{company_clean}_{title_clean}{focus_suffix}_{timestamp}.html"
        elif title_clean:
            # Title-only name
            return f"gen{generation}{parent_info}_{title_clean}{focus_suffix}_{timestamp}.html"
        elif company_clean:
            # Company-only name
            return f"gen{generation}{parent_info}_{company_clean}{focus_suffix}_{timestamp}.html"
        else:
            # Generic name with focus
            return f"gen{generation}{parent_info}{focus_suffix}_{timestamp}.html"
    
    def get_next_generation(self, parent_variant=""):
        """Determine the next generation number based on parent"""
        if not parent_variant:
            return 1
            
        # Get parent generation
        parent_gen = self.get_variant_generation(parent_variant)
        return parent_gen + 1
    
    def get_variant_generation(self, variant_name):
        """Extract generation number from variant name or metadata"""
        # First, try to read from file metadata
        try:
            # Check if it's a template file
            if variant_name in ['base_resume.html', 'base_resume_v2.html']:
                return 0  # Base templates are generation 0
            
            # Read variant file to get generation from metadata
            variant_path = self.variants_dir / variant_name
            if variant_path.exists():
                with open(variant_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for generation metadata
                gen_match = re.search(r'<!-- GENERATION:\s*(\d+)\s*-->', content)
                if gen_match:
                    return int(gen_match.group(1))
        except Exception:
            pass
        
        # Fallback: Try to extract from filename
        gen_match = re.search(r'gen(\d+)', variant_name)
        if gen_match:
            return int(gen_match.group(1))
            
        # Final fallback for unknown variants
        return 1
    
    def extract_job_info(self):
        """Extract company and title from job description file"""
        info = {'company': '', 'title': '', 'location': ''}
        
        try:
            with open(self.job_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for common patterns
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('Company:'):
                    info['company'] = line.replace('Company:', '').strip()
                elif line.startswith('Role:') or line.startswith('Title:'):
                    info['title'] = line.split(':', 1)[1].strip()
                elif line.startswith('Location:'):
                    info['location'] = line.replace('Location:', '').strip()
                elif 'software engineer' in line.lower() and not info['title']:
                    info['title'] = 'Software Engineer'
                elif any(company in line.lower() for company in ['inc', 'corp', 'llc', 'ltd', 'co.']):
                    if not info['company'] and len(line.split()) <= 4:
                        info['company'] = line
                        
        except Exception as e:
            print(f"Could not read job description: {e}")
            
        return info
    
    def list_variants_with_details(self):
        """List all variants with preview links and descriptions"""
        variants = []
        
        if not self.variants_dir.exists():
            return variants
            
        for variant_file in self.variants_dir.glob('*.html'):
            info = self.get_variant_info(variant_file)
            variants.append(info)
            
        # Sort by creation time (newest first)
        variants.sort(key=lambda x: x['created'], reverse=True)
        return variants
    
    def get_variant_info(self, variant_path):
        """Extract information about a variant - supports hybrid metadata"""
        variant_path = Path(variant_path)
        
        info = {
            'filename': variant_path.name,
            'name': variant_path.stem.replace('_', ' ').title(),
            'preview_url': f"http://localhost:8081/agent_workspace/variants/{variant_path.name}",
            'size_kb': round(variant_path.stat().st_size / 1024, 1),
            'created': datetime.fromtimestamp(variant_path.stat().st_ctime),
            'description': 'Resume variant',
            'focus_type': 'general',
            'pdf_status': 'unknown',
            'is_hybrid': False,
            'parents': [],
            'hybrid_features': ''
        }
        
        try:
            with open(variant_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract metadata from comments
            if '<!-- VARIANT_TYPE:' in content:
                type_match = re.search(r'<!-- VARIANT_TYPE:\s*(.+?)\s*-->', content)
                if type_match:
                    info['focus_type'] = type_match.group(1).strip()
                    
            if '<!-- VARIANT_DESC:' in content:
                desc_match = re.search(r'<!-- VARIANT_DESC:\s*(.+?)\s*-->', content)
                if desc_match:
                    info['description'] = desc_match.group(1).strip()
                    
            # Extract hybrid-specific metadata
            if '<!-- PARENTS:' in content:
                parents_match = re.search(r'<!-- PARENTS:\s*(.+?)\s*-->', content)
                if parents_match:
                    parents_str = parents_match.group(1).strip()
                    info['parents'] = [p.strip() for p in parents_str.split(',')]
                    info['is_hybrid'] = True
                    
            if '<!-- HYBRID_FEATURES:' in content:
                features_match = re.search(r'<!-- HYBRID_FEATURES:\s*(.+?)\s*-->', content)
                if features_match:
                    info['hybrid_features'] = features_match.group(1).strip()
            
            # Extract job description metadata
            if '<!-- JOB_TITLE:' in content:
                job_title_match = re.search(r'<!-- JOB_TITLE:\s*(.+?)\s*-->', content)
                if job_title_match:
                    info['job_title'] = job_title_match.group(1).strip()
                    
            if '<!-- JOB_COMPANY:' in content:
                job_company_match = re.search(r'<!-- JOB_COMPANY:\s*(.+?)\s*-->', content)
                if job_company_match:
                    info['job_company'] = job_company_match.group(1).strip()
                    
            # Extract title for better naming
            title_match = re.search(r'<title>([^<]+)</title>', content)
            if title_match:
                title = title_match.group(1).strip()
                if title != "Enrico Patarini - Resume":
                    info['name'] = title.replace(' - Resume', '').replace('Enrico Patarini - ', '')
                    
        except Exception as e:
            print(f"Could not read variant {variant_path}: {e}")
            
        return info
    
    def check_pdf_layouts(self):
        """Check which variants have PDF layout issues"""
        results = []
        
        for variant_file in self.variants_dir.glob('*.html'):
            info = self.get_variant_info(variant_file)
            
            # Estimate content density (rough heuristic)
            try:
                with open(variant_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Count content indicators
                bullet_count = content.count('<li>')
                skill_rows = content.count('skill-row')
                text_length = len(re.sub(r'<[^>]+>', '', content))
                
                # Estimate if likely to overflow (very rough)
                estimated_overflow = (
                    bullet_count > 12 or 
                    skill_rows > 8 or 
                    text_length > 4000
                )
                
                info['estimated_overflow'] = estimated_overflow
                info['content_metrics'] = {
                    'bullets': bullet_count,
                    'skill_rows': skill_rows,
                    'text_length': text_length
                }
                
            except Exception as e:
                info['estimated_overflow'] = True
                info['content_metrics'] = {'error': str(e)}
                
            results.append(info)
            
        return results
    
    def create_selection_summary(self):
        """Create a summary for variant selection"""
        variants = self.list_variants_with_details()
        layout_issues = self.check_pdf_layouts()
        
        summary = {
            'total_variants': len(variants),
            'variants': variants,
            'layout_analysis': layout_issues,
            'recommendations': []
        }
        
        # Add recommendations
        for variant in variants:
            rec = {
                'filename': variant['filename'],
                'preview_url': variant['preview_url'],
                'focus': variant['focus_type'],
                'description': variant['description']
            }
            
            # Find matching layout analysis
            for layout in layout_issues:
                if layout['filename'] == variant['filename']:
                    rec['pdf_warning'] = layout['estimated_overflow']
                    rec['content_metrics'] = layout.get('content_metrics', {})
                    break
                    
            summary['recommendations'].append(rec)
            
        return summary
    
    def create_genealogy_tree(self):
        """Create a family tree of resume variants with hybrid support"""
        variants = self.list_variants_with_details()
        
        # Build parent-child relationships
        tree = {
            'base_resume.html': {
                'info': {
                    'name': 'Original Base Template',
                    'generation': 0,
                    'type': 'Base Template',
                    'created': 'Initial',
                    'description': 'Original ATS-optimized template',
                    'is_hybrid': False,
                    'parents': []
                },
                'children': []
            },
            'base_resume_v2.html': {
                'info': {
                    'name': 'Enhanced Base Template',
                    'generation': 0,  # Base template, generation 0
                    'type': 'Base Template',
                    'created': 'Dec 2024',
                    'description': 'Enhanced base template',
                    'is_hybrid': False,
                    'parents': []
                },
                'children': []
            }
        }
        
        # First pass: Add all variants to tree
        variant_data = {}
        for variant in variants:
            filename = variant['filename']
            generation = self.get_variant_generation(filename)
            parents = self.determine_parent_variant(variant)
            is_hybrid = isinstance(parents, list)
            
            variant_info = {
                'info': {
                    'name': variant['name'],
                    'generation': generation,
                    'type': variant['focus_type'],
                    'created': variant['created'].strftime('%b %d, %Y %H:%M'),
                    'description': variant['description'],
                    'filename': filename,
                    'preview_url': variant['preview_url'],
                    'is_hybrid': is_hybrid,
                    'parents': parents if is_hybrid else ([parents] if parents else []),
                    'hybrid_features': variant.get('hybrid_features', '')
                },
                'children': []
            }
            
            tree[filename] = variant_info
            variant_data[filename] = {'parents': parents, 'is_hybrid': is_hybrid}
        
        # Second pass: Build parent-child relationships
        for filename, data in variant_data.items():
            parents = data['parents']
            is_hybrid = data['is_hybrid']
            
            if is_hybrid:
                # Multi-parent hybrid - add to all parents
                for parent in parents:
                    if parent in tree:
                        tree[parent]['children'].append(filename)
            else:
                # Single parent
                if parents and isinstance(parents, str) and parents in tree:
                    tree[parents]['children'].append(filename)
        
        return tree
    
    def determine_parent_variant(self, variant):
        """Determine the parent variant(s) based on content analysis - supports multi-parent hybrids"""
        filename = variant['filename']
        generation = self.get_variant_generation(filename)
        
        # Read variant content to find parent hints
        variant_path = self.variants_dir / filename
        try:
            with open(variant_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for multi-parent hybrid metadata first
            parents_match = re.search(r'<!-- PARENTS:\s*(.+?)\s*-->', content)
            if parents_match:
                parents_str = parents_match.group(1).strip()
                return [p.strip() for p in parents_str.split(',')]
                
            # Look for single parent hints in metadata
            parent_match = re.search(r'<!-- PARENT:\s*(.+?)\s*-->', content)
            if parent_match:
                return parent_match.group(1).strip()
                
        except Exception:
            pass
        
        # Default parent assignment based on generation and name
        if generation <= 1:
            return 'base_resume.html'
        elif 'optimal' in filename:
            return 'base_resume_v2.html'
        else:
            return 'base_resume.html'
    
    def add_parent_metadata(self, variant_file, parent_variant, job_title=None, job_company=None):
        """Add parent metadata to a variant file - supports hybrid parents"""
        try:
            with open(variant_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determine if this is a hybrid (multiple parents)
            if isinstance(parent_variant, list):
                # Multi-parent hybrid
                parents_str = ', '.join(parent_variant)
                parent_comment = f'<!-- PARENTS: {parents_str} -->\n<!-- GENERATION: {self.get_next_generation(parent_variant[0])} -->\n<!-- VARIANT_TYPE: Multi-Parent Hybrid -->\n'
            else:
                # Single parent
                parent_comment = f'<!-- PARENT: {parent_variant} -->\n<!-- GENERATION: {self.get_next_generation(parent_variant)} -->\n'
            
            # Add job description metadata if provided
            if job_title or job_company:
                job_metadata = ''
                if job_title:
                    job_metadata += f'<!-- JOB_TITLE: {job_title} -->\n'
                if job_company:
                    job_metadata += f'<!-- JOB_COMPANY: {job_company} -->\n'
                parent_comment += job_metadata
            
            head_pos = content.find('<head>') + 6
            updated_content = content[:head_pos] + '\n    ' + parent_comment + content[head_pos:]
            
            with open(variant_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
                
        except Exception as e:
            print(f"Could not add parent metadata to {variant_file}: {e}")
    
    def get_variant_lineage(self, variant_name):
        """Get the full lineage of a variant back to the root - supports hybrid lineages"""
        lineage = [{'name': variant_name, 'parents': [], 'is_hybrid': False}]
        current = variant_name
        processed = set([variant_name])
        
        # Trace back to root
        while current:
            parent_info = self.determine_parent_variant({'filename': current})
            
            if isinstance(parent_info, list):
                # Multi-parent hybrid
                lineage[-1]['parents'] = parent_info
                lineage[-1]['is_hybrid'] = True
                # For lineage display, take the first parent to continue the chain
                next_current = parent_info[0] if parent_info and parent_info[0] not in processed else None
            else:
                # Single parent
                if parent_info and parent_info != current and parent_info not in processed:
                    lineage.append({'name': parent_info, 'parents': [], 'is_hybrid': False})
                    next_current = parent_info
                else:
                    next_current = None
            
            if next_current:
                processed.add(next_current)
                current = next_current
            else:
                break
                
        lineage.reverse()  # Root first
        return lineage
    
    def create_hybrid_variant(self, parent_variants, target_name, feature_descriptions=None):
        """Create a hybrid variant from multiple parent variants"""
        if len(parent_variants) < 2:
            raise ValueError("Hybrid variants require at least 2 parent variants")
        
        # Read all parent variants
        parent_contents = {}
        for parent in parent_variants:
            parent_path = self.variants_dir / parent if not parent.startswith('base_') else self.templates_dir / parent
            try:
                with open(parent_path, 'r', encoding='utf-8') as f:
                    parent_contents[parent] = f.read()
            except Exception as e:
                print(f"Could not read parent variant {parent}: {e}")
                return None
        
        # For now, use the first parent as the base structure
        # In a real implementation, this would intelligently merge features
        base_content = list(parent_contents.values())[0]
        
        # Create hybrid metadata
        parents_str = ', '.join(parent_variants)
        features_str = feature_descriptions or f"Combined features from {len(parent_variants)} parent variants"
        
        # Replace title and add hybrid metadata
        title_pattern = r'<title>([^<]+)</title>'
        new_title = f'<title>{target_name} - Hybrid Resume</title>'
        
        hybrid_metadata = f'''    <!-- PARENTS: {parents_str} -->
    <!-- GENERATION: {self.get_next_generation(parent_variants[0])} -->
    <!-- VARIANT_TYPE: Multi-Parent Hybrid -->
    <!-- VARIANT_DESC: HYBRID - {features_str} -->
    <!-- HYBRID_FEATURES: {features_str} -->
    <!-- GENERATED: {datetime.now().strftime('%Y-%m-%d')} -->'''
        
        # Update content with hybrid metadata
        hybrid_content = re.sub(title_pattern, new_title, base_content)
        
        # Add metadata after title
        title_end = hybrid_content.find('</title>') + 8
        hybrid_content = hybrid_content[:title_end] + '\n' + hybrid_metadata + hybrid_content[title_end:]
        
        # Write hybrid variant
        hybrid_path = self.variants_dir / f"{target_name}.html"
        try:
            with open(hybrid_path, 'w', encoding='utf-8') as f:
                f.write(hybrid_content)
            print(f"✅ Created hybrid variant: {hybrid_path}")
            return hybrid_path
        except Exception as e:
            print(f"❌ Could not create hybrid variant: {e}")
            return None

def main():
    """CLI interface for variant management"""
    import sys
    
    workshop_dir = Path(__file__).parent  # This is agent_workspace
    manager = VariantManager(workshop_dir)
    
    if len(sys.argv) < 2:
        print("Usage: python variant_manager.py [command]")
        print("Commands:")
        print("  list - List all variants with details")
        print("  check-layouts - Check PDF layout issues")
        print("  suggest-name [focus_type] - Suggest variant name")
        print("  summary - Full selection summary")
        print("  tree - Show genealogy tree")
        print("  lineage [variant_name] - Show lineage for specific variant")
        print("  add-parent [variant_file] [parent_name] - Add parent metadata")
        print("  create-hybrid [parent1] [parent2] [target_name] - Create hybrid variant from multiple parents")
        print("  show-hybrids - Show all hybrid variants with their parent relationships")
        return
        
    command = sys.argv[1]
    
    if command == 'list':
        variants = manager.list_variants_with_details()
        print(f"\n📋 Available Resume Variants ({len(variants)} total):")
        print("=" * 60)
        
        for variant in variants:
            print(f"📄 {variant['filename']}")
            print(f"   📝 {variant['description']}")
            print(f"   🎯 Focus: {variant['focus_type']}")
            print(f"   🔗 Preview: {variant['preview_url']}")
            print(f"   📊 Size: {variant['size_kb']}KB | Created: {variant['created'].strftime('%m/%d %H:%M')}")
            print()
            
    elif command == 'check-layouts':
        layouts = manager.check_pdf_layouts()
        print(f"\n📐 PDF Layout Analysis:")
        print("=" * 50)
        
        for layout in layouts:
            status = "⚠️  LIKELY OVERFLOW" if layout['estimated_overflow'] else "✅ SINGLE PAGE"
            print(f"{status} - {layout['filename']}")
            metrics = layout['content_metrics']
            if 'error' not in metrics:
                print(f"         Bullets: {metrics['bullets']} | Skills: {metrics['skill_rows']} | Text: {metrics['text_length']} chars")
            print()
            
    elif command == 'suggest-name':
        focus_type = sys.argv[2] if len(sys.argv) > 2 else ""
        suggested = manager.create_variant_name(focus_type=focus_type)
        print(f"Suggested filename: {suggested}")
        
    elif command == 'summary':
        summary = manager.create_selection_summary()
        print(f"\n🎯 Resume Variant Selection Summary")
        print("=" * 50)
        print(f"Total Variants: {summary['total_variants']}")
        print()
        
        for rec in summary['recommendations']:
            warning = " ⚠️ " if rec.get('pdf_warning') else " ✅ "
            print(f"{warning}{rec['filename']}")
            print(f"      🎯 {rec['focus']} - {rec['description']}")
            print(f"      🔗 {rec['preview_url']}")
            print()
    
    elif command == 'tree':
        tree = manager.create_genealogy_tree()
        print(f"\n🧬 Resume Genealogy Tree")
        print("=" * 60)
        
        def print_tree_node(node_name, node_data, depth=0):
            indent = "  " * depth
            info = node_data['info']
            
            # Select icon based on type
            if depth == 0:
                icon = "🌱"
            elif info.get('is_hybrid', False):
                icon = "🔀"  # Hybrid/merge icon
            else:
                icon = "📄"
            
            # Format name with hybrid indicator
            name_display = info['name']
            if info.get('is_hybrid', False):
                name_display += " 🧬"
            
            print(f"{indent}{icon} {name_display} (Gen {info['generation']})")
            print(f"{indent}   Type: {info['type']} | Created: {info['created']}")
            
            # Show parent relationships for hybrids
            if info.get('is_hybrid', False) and info.get('parents'):
                parent_names = ', '.join(info['parents'])
                print(f"{indent}   🔀 Parents: {parent_names}")
                if info.get('hybrid_features'):
                    print(f"{indent}   ✨ Features: {info['hybrid_features']}")
            
            if 'preview_url' in info:
                print(f"{indent}   🔗 {info['preview_url']}")
            print(f"{indent}   📝 {info['description']}")
            
            # Print children
            for child_name in node_data['children']:
                if child_name in tree:
                    print_tree_node(child_name, tree[child_name], depth + 1)
            print()
        
        # Print base templates first
        for base in ['base_resume.html', 'base_resume_v2.html']:
            if base in tree:
                print_tree_node(base, tree[base])
        
        # Print orphaned variants (those with parents not in tree, like hybrids)
        print("📊 Additional Variants:")
        print("-" * 40)
        for filename, node_data in tree.items():
            if filename not in ['base_resume.html', 'base_resume_v2.html']:
                # Check if this variant was already printed as a child
                already_printed = False
                for base in ['base_resume.html', 'base_resume_v2.html']:
                    if base in tree and filename in tree[base]['children']:
                        already_printed = True
                        break
                
                if not already_printed:
                    print_tree_node(filename, node_data)
    
    elif command == 'lineage':
        variant_name = sys.argv[2] if len(sys.argv) > 2 else 'happydoc_optimal_1217.html'
        lineage = manager.get_variant_lineage(variant_name)
        print(f"\n🧬 Lineage for {variant_name}")
        print("=" * 50)
        
        for i, variant_info in enumerate(lineage):
            arrow = " → " if i > 0 else ""
            variant_name = variant_info['name'] if isinstance(variant_info, dict) else variant_info
            generation = manager.get_variant_generation(variant_name)
            
            if isinstance(variant_info, dict) and variant_info.get('is_hybrid'):
                parent_info = f" (Hybrid from: {', '.join(variant_info['parents'])})"
            else:
                parent_info = ""
            
            print(f"{arrow}Gen {generation}: {variant_name}{parent_info}")
    
    elif command == 'add-parent':
        if len(sys.argv) < 4:
            print("Usage: add-parent [variant_file] [parent_name]")
            return
        variant_file = sys.argv[2]
        parent_name = sys.argv[3]
        
        variant_path = manager.variants_dir / variant_file
        if not variant_path.exists():
            print(f"Variant file not found: {variant_file}")
            return
            
        manager.add_parent_metadata(variant_path, parent_name)
        print(f"Added parent metadata: {variant_file} ← {parent_name}")
    
    elif command == 'create-hybrid':
        if len(sys.argv) < 5:
            print("Usage: create-hybrid [parent1] [parent2] [target_name] [optional: feature_description]")
            print("Example: create-hybrid appeal_optimized.html skills_matched.html combined_optimal 'Professional summary + bold tech matching'")
            return
        
        parent1 = sys.argv[2]
        parent2 = sys.argv[3]
        target_name = sys.argv[4]
        feature_desc = sys.argv[5] if len(sys.argv) > 5 else None
        
        result = manager.create_hybrid_variant([parent1, parent2], target_name, feature_desc)
        if result:
            print(f"🧬 Hybrid variant created successfully!")
            print(f"   Name: {target_name}.html")
            print(f"   Parents: {parent1}, {parent2}")
            print(f"   Preview: http://localhost:8081/agent_workspace/variants/{target_name}.html")
        else:
            print("❌ Failed to create hybrid variant")
    
    elif command == 'show-hybrids':
        variants = manager.list_variants_with_details()
        hybrids = [v for v in variants if v.get('is_hybrid', False)]
        
        print(f"\n🧬 Hybrid Variants ({len(hybrids)} found):")
        print("=" * 60)
        
        if not hybrids:
            print("No hybrid variants found.")
        else:
            for hybrid in hybrids:
                print(f"🔀 {hybrid['filename']}")
                print(f"   📝 {hybrid['description']}")
                print(f"   👨‍👩‍👧 Parents: {', '.join(hybrid.get('parents', []))}")
                if hybrid.get('hybrid_features'):
                    print(f"   ✨ Features: {hybrid['hybrid_features']}")
                print(f"   🔗 Preview: {hybrid['preview_url']}")
                print()
            
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()