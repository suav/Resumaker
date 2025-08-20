#!/usr/bin/env python3
"""
Fix Resume Genealogy System
Recalculates proper generation numbers based on actual parent relationships
Prevents cycles and ensures accurate tree structure
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional, Tuple

class GenealogyFixer:
    """Fixes resume variant genealogy and generation assignments"""
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = Path(workspace_dir)
        self.variants_dir = self.workspace_dir / 'variants'
        self.templates_dir = self.workspace_dir / 'templates'
        
        # Track the genealogy data
        self.variants = {}
        self.generations = {}
        self.parent_map = {}
        
    def analyze_current_state(self):
        """Analyze current genealogy state and identify issues"""
        print("🔍 Analyzing Current Genealogy State")
        print("=" * 60)
        
        # Load all variants and extract parent relationships
        for variant_file in self.variants_dir.glob('*.html'):
            variant_info = self._extract_variant_metadata(variant_file)
            self.variants[variant_file.name] = variant_info
        
        # Include base templates
        for template_file in self.templates_dir.glob('*.html'):
            template_info = {
                'filename': template_file.name,
                'parents': [],
                'generation': 0,
                'is_template': True,
                'conflicts': []
            }
            self.variants[template_file.name] = template_info
        
        # Analyze each variant
        issues_found = []
        
        for filename, info in self.variants.items():
            # Check for multiple parent declarations
            if len(info['conflicts']) > 1:
                issues_found.append(f"❌ {filename}: Multiple parent declarations")
                for conflict in info['conflicts']:
                    print(f"     {conflict}")
            
            # Check for invalid parents
            for parent in info['parents']:
                if parent not in self.variants:
                    issues_found.append(f"❌ {filename}: References non-existent parent '{parent}'")
        
        print(f"\n📊 Analysis Results:")
        print(f"   📄 Total variants: {len([f for f in self.variants if not self.variants[f].get('is_template')])}")
        print(f"   📄 Base templates: {len([f for f in self.variants if self.variants[f].get('is_template')])}")
        print(f"   ❌ Issues found: {len(issues_found)}")
        
        if issues_found:
            print("\n🔍 Issues Found:")
            for issue in issues_found[:10]:  # Show first 10
                print(f"   {issue}")
            if len(issues_found) > 10:
                print(f"   ... and {len(issues_found) - 10} more")
        
        return issues_found
    
    def _extract_variant_metadata(self, variant_file: Path) -> Dict:
        """Extract parent relationships and generation info from a variant file"""
        try:
            with open(variant_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all parent declarations and track conflicts
            parent_patterns = [
                r'<!-- PARENT:\s*(.+?)\s*-->',
                r'<!-- PARENTS:\s*(.+?)\s*-->'
            ]
            
            all_parent_matches = []
            conflicts = []
            
            for pattern in parent_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    all_parent_matches.append(match)
                    conflicts.append(f"Found: {match}")
            
            # Parse parent relationships
            parents = []
            for match in all_parent_matches:
                if ',' in match:
                    # Multiple parents (hybrid)
                    parent_list = [p.strip() for p in match.split(',')]
                    parents.extend(parent_list)
                else:
                    # Single parent
                    parents.append(match.strip())
            
            # Remove duplicates while preserving order
            seen = set()
            unique_parents = []
            for parent in parents:
                if parent not in seen:
                    seen.add(parent)
                    unique_parents.append(parent)
            
            # Extract generation info
            gen_matches = re.findall(r'<!-- GENERATION:\s*(\d+)\s*-->', content)
            current_generation = int(gen_matches[0]) if gen_matches else None
            
            return {
                'filename': variant_file.name,
                'parents': unique_parents,
                'generation': current_generation,
                'conflicts': conflicts,
                'is_template': False
            }
            
        except Exception as e:
            print(f"❌ Error reading {variant_file.name}: {e}")
            return {
                'filename': variant_file.name,
                'parents': [],
                'generation': None,
                'conflicts': [f"Error reading file: {e}"],
                'is_template': False
            }
    
    def calculate_proper_generations(self) -> Dict[str, int]:
        """Calculate proper generation numbers based on parent relationships"""
        print("\n🧮 Calculating Proper Generation Numbers")
        print("=" * 60)
        
        generations = {}
        visiting = set()  # For cycle detection
        visited = set()
        
        def calculate_generation(filename: str, path: List[str] = None) -> int:
            """Recursively calculate generation with cycle detection"""
            if path is None:
                path = []
            
            # Cycle detection
            if filename in visiting:
                cycle_path = ' → '.join(path + [filename])
                print(f"⚠️  Cycle detected: {cycle_path}")
                return len(path)  # Return current depth to break cycle
            
            if filename in visited:
                return generations[filename]
            
            visiting.add(filename)
            
            variant_info = self.variants.get(filename)
            if not variant_info:
                print(f"❌ Unknown variant: {filename}")
                visiting.remove(filename)
                return 0
            
            # Base templates are generation 0
            if variant_info.get('is_template'):
                generation = 0
            elif not variant_info['parents']:
                # No parents - treat as generation 1 from unknown base
                generation = 1
            else:
                # Calculate as max parent generation + 1
                max_parent_gen = 0
                for parent in variant_info['parents']:
                    parent_gen = calculate_generation(parent, path + [filename])
                    max_parent_gen = max(max_parent_gen, parent_gen)
                generation = max_parent_gen + 1
            
            visiting.remove(filename)
            visited.add(filename)
            generations[filename] = generation
            
            return generation
        
        # Calculate generations for all variants
        for filename in self.variants:
            if filename not in visited:
                calculate_generation(filename)
        
        return generations
    
    def display_corrected_tree(self, generations: Dict[str, int]):
        """Display the corrected genealogy tree"""
        print("\n🌳 Corrected Genealogy Tree")
        print("=" * 60)
        
        # Group by generation
        by_generation = {}
        for filename, generation in generations.items():
            if generation not in by_generation:
                by_generation[generation] = []
            by_generation[generation].append(filename)
        
        # Display tree by generation
        for gen in sorted(by_generation.keys()):
            variants_in_gen = by_generation[gen]
            print(f"\n🔢 Generation {gen} ({len(variants_in_gen)} variants):")
            print("-" * 40)
            
            for filename in sorted(variants_in_gen):
                variant_info = self.variants[filename]
                
                # Show icon based on type
                if variant_info.get('is_template'):
                    icon = "🌱"
                elif len(variant_info['parents']) > 1:
                    icon = "🔀"  # Hybrid
                else:
                    icon = "📄"
                
                # Show parent relationships
                if variant_info['parents']:
                    parent_info = f" ← {', '.join(variant_info['parents'])}"
                else:
                    parent_info = ""
                
                # Show generation correction if needed
                old_gen = variant_info.get('generation')
                if old_gen is not None and old_gen != gen:
                    correction = f" (was Gen {old_gen})"
                else:
                    correction = ""
                
                print(f"   {icon} {filename}{parent_info}{correction}")
    
    def fix_variant_metadata(self, generations: Dict[str, int]):
        """Fix the metadata in variant files with correct generations"""
        print("\n🔧 Fixing Variant Metadata")
        print("=" * 60)
        
        fixed_count = 0
        
        for filename, correct_generation in generations.items():
            variant_info = self.variants[filename]
            
            # Skip templates
            if variant_info.get('is_template'):
                continue
            
            # Only fix if generation is wrong or there are conflicts
            needs_fix = (
                variant_info.get('generation') != correct_generation or
                len(variant_info.get('conflicts', [])) > 1
            )
            
            if needs_fix:
                variant_path = self.variants_dir / filename
                
                if self._fix_single_variant(variant_path, variant_info, correct_generation):
                    fixed_count += 1
                    print(f"   ✅ Fixed {filename}: Gen {variant_info.get('generation')} → Gen {correct_generation}")
                else:
                    print(f"   ❌ Failed to fix {filename}")
        
        print(f"\n🎉 Fixed {fixed_count} variant files")
    
    def _fix_single_variant(self, variant_path: Path, variant_info: Dict, correct_generation: int) -> bool:
        """Fix metadata in a single variant file"""
        try:
            with open(variant_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove all existing parent/generation metadata
            content = re.sub(r'<!-- PARENT:.*?-->\n?', '', content)
            content = re.sub(r'<!-- PARENTS:.*?-->\n?', '', content)
            content = re.sub(r'<!-- GENERATION:.*?-->\n?', '', content)
            
            # Create clean metadata
            parents = variant_info['parents']
            
            if len(parents) == 0:
                # No parents - unusual but handle it
                metadata = f"    <!-- GENERATION: {correct_generation} -->\n"
            elif len(parents) == 1:
                # Single parent
                metadata = f"    <!-- PARENT: {parents[0]} -->\n    <!-- GENERATION: {correct_generation} -->\n"
            else:
                # Multiple parents (hybrid)
                parents_str = ', '.join(parents)
                metadata = f"    <!-- PARENTS: {parents_str} -->\n    <!-- GENERATION: {correct_generation} -->\n"
            
            # Insert clean metadata after <head>
            head_pos = content.find('<head>') + 6
            if head_pos > 5:  # Found <head>
                updated_content = content[:head_pos] + '\n' + metadata + content[head_pos:]
                
                with open(variant_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                return True
            else:
                print(f"   ⚠️  No <head> tag found in {variant_path.name}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error fixing {variant_path.name}: {e}")
            return False
    
    def run_full_fix(self):
        """Run the complete genealogy fix process"""
        print("🔧 Resume Genealogy Fix Tool")
        print("=" * 60)
        
        # Step 1: Analyze current state
        issues = self.analyze_current_state()
        
        if not issues:
            print("\n✅ No genealogy issues found!")
            return
        
        # Step 2: Calculate proper generations
        correct_generations = self.calculate_proper_generations()
        
        # Step 3: Display corrected tree
        self.display_corrected_tree(correct_generations)
        
        # Step 4: Fix the variant files
        self.fix_variant_metadata(correct_generations)
        
        print("\n🎉 Genealogy fix complete!")
        print("   Tree structure now accurately reflects parent-child relationships")
        print("   Generation numbers are based on actual depth from root templates")


def main():
    """Main function"""
    workspace_dir = Path(__file__).parent.parent
    fixer = GenealogyFixer(workspace_dir)
    fixer.run_full_fix()


if __name__ == "__main__":
    main()