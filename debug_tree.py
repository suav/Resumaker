#!/usr/bin/env python3
"""
Debug the tree building process
"""

import sys
import os
from pathlib import Path

# Add agent workspace scripts to path
WORKSHOP_DIR = Path(__file__).parent
AGENT_WORKSPACE = WORKSHOP_DIR / 'agent_workspace'
SCRIPTS_DIR = AGENT_WORKSPACE / 'scripts'
sys.path.append(str(SCRIPTS_DIR))

from variant_manager import VariantManager

def debug_tree():
    """Debug the tree building process step by step"""
    
    print("🔍 Debugging Tree Building Process")
    print("=" * 60)
    
    manager = VariantManager(WORKSHOP_DIR)
    
    # Step 1: List variants
    variants = manager.list_variants_with_details()
    print(f"📊 Found {len(variants)} variants:")
    for variant in variants:
        filename = variant['filename']
        generation = manager.get_variant_generation(filename)
        parents = manager.determine_parent_variant(variant)
        is_hybrid = isinstance(parents, list)
        
        print(f"   📄 {filename}")
        print(f"      Generation: {generation}")
        print(f"      Parents: {parents} (hybrid: {is_hybrid})")
        print(f"      Type: {variant['focus_type']}")
        print()
    
    # Step 2: Test tree building manually
    print("\n🌳 Manual Tree Building Test")
    print("-" * 40)
    
    tree = {
        'base_resume.html': {'info': {'name': 'Base Resume', 'generation': 0}, 'children': []},
        'base_resume_v2.html': {'info': {'name': 'Base Resume V2', 'generation': 0}, 'children': []}
    }
    
    for variant in variants:
        filename = variant['filename']
        parents = manager.determine_parent_variant(variant)
        is_hybrid = isinstance(parents, list)
        
        print(f"Processing {filename}:")
        print(f"   Parents: {parents} (type: {type(parents)})")
        print(f"   Is hybrid: {is_hybrid}")
        
        # Add to tree
        tree[filename] = {'info': {'name': filename}, 'children': []}
        
        # Add to parent's children
        if is_hybrid:
            for parent in parents:
                if parent in tree:
                    tree[parent]['children'].append(filename)
                    print(f"   ✅ Added {filename} as child of {parent}")
                else:
                    print(f"   ❌ Parent {parent} not found in tree")
        else:
            if parents and isinstance(parents, str) and parents in tree:
                tree[parents]['children'].append(filename)
                print(f"   ✅ Added {filename} as child of {parents}")
            else:
                print(f"   ❌ Parent {parents} not found or invalid")
        print()
    
    # Step 3: Show final tree structure
    print("\n🌲 Final Tree Structure")
    print("-" * 40)
    
    def print_tree_level(node_name, node_data, level=0):
        indent = "  " * level
        children_count = len(node_data['children'])
        print(f"{indent}📄 {node_name} ({children_count} children)")
        for child in node_data['children']:
            if child in tree:
                print_tree_level(child, tree[child], level + 1)
    
    for root in ['base_resume.html', 'base_resume_v2.html']:
        if root in tree:
            print_tree_level(root, tree[root])

if __name__ == "__main__":
    debug_tree()