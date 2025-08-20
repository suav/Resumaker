#!/usr/bin/env python3
"""
Cleanup utility for removing problematic resume variants
Fixes files with malformed names, duplicates, and corrupted content
"""

import os
import re
from pathlib import Path

def main():
    """Clean up problematic variants in the agent workspace"""
    
    workshop_dir = Path(__file__).parent
    variants_dir = workshop_dir / 'agent_workspace' / 'variants'
    
    if not variants_dir.exists():
        print(f"❌ Variants directory not found: {variants_dir}")
        return
    
    print("🧹 Resume Variants Cleanup Utility")
    print("=" * 50)
    print(f"📁 Scanning: {variants_dir}")
    print()
    
    # Get all files in variants directory
    all_files = list(variants_dir.iterdir())
    
    # Categorize files
    valid_files = []
    problematic_files = []
    malformed_names = []
    
    for file_path in all_files:
        if file_path.is_file():
            filename = file_path.name
            
            # Check for problematic patterns
            if not filename.endswith('.html'):
                malformed_names.append(file_path)
            elif any(char in filename for char in [' ', '\t', '\n']):
                malformed_names.append(file_path)
            elif filename.startswith('__') and filename.count('_') > 4:
                problematic_files.append(file_path)
            else:
                valid_files.append(file_path)
    
    print(f"📊 Found {len(all_files)} total files:")
    print(f"   ✅ Valid files: {len(valid_files)}")
    print(f"   ⚠️  Problematic files: {len(problematic_files)}")
    print(f"   ❌ Malformed names: {len(malformed_names)}")
    print()
    
    # Show malformed names
    if malformed_names:
        print("❌ Files with malformed names:")
        for file_path in malformed_names:
            size = file_path.stat().st_size
            print(f"   📄 '{file_path.name}' ({size} bytes)")
        print()
    
    # Show problematic files
    if problematic_files:
        print("⚠️  Problematic files (auto-generated with complex names):")
        for file_path in problematic_files:
            size = file_path.stat().st_size
            print(f"   📄 '{file_path.name}' ({size} bytes)")
        print()
    
    # Offer cleanup options
    if malformed_names or problematic_files:
        print("🔧 Cleanup Options:")
        print("1. Fix malformed names (rename to proper .html format)")
        print("2. Delete problematic auto-generated files")
        print("3. Delete all malformed name files")
        print("4. Show file contents before deciding")
        print("5. Exit without changes")
        print()
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '1':
            fix_malformed_names(malformed_names)
        elif choice == '2':
            delete_problematic_files(problematic_files)
        elif choice == '3':
            delete_malformed_files(malformed_names)
        elif choice == '4':
            show_file_contents(malformed_names + problematic_files)
        elif choice == '5':
            print("👋 Exiting without changes")
        else:
            print("❌ Invalid choice")
    else:
        print("✅ No cleanup needed - all files look good!")


def fix_malformed_names(malformed_files):
    """Fix files with malformed names"""
    print("\n🔧 Fixing malformed file names...")
    
    fixed_count = 0
    for file_path in malformed_files:
        old_name = file_path.name
        
        # Generate a clean name
        clean_name = generate_clean_name(old_name, file_path)
        
        if clean_name and clean_name != old_name:
            new_path = file_path.parent / clean_name
            
            # Avoid conflicts
            counter = 1
            while new_path.exists():
                name_part = clean_name.replace('.html', '')
                new_clean_name = f"{name_part}_{counter}.html"
                new_path = file_path.parent / new_clean_name
                counter += 1
            
            try:
                file_path.rename(new_path)
                print(f"   ✅ '{old_name}' → '{new_path.name}'")
                fixed_count += 1
            except Exception as e:
                print(f"   ❌ Failed to rename '{old_name}': {e}")
    
    print(f"\n🎉 Fixed {fixed_count} file names")


def delete_problematic_files(problematic_files):
    """Delete problematic auto-generated files"""
    print("\n🗑️  Deleting problematic files...")
    
    deleted_count = 0
    for file_path in problematic_files:
        try:
            file_path.unlink()
            print(f"   ✅ Deleted '{file_path.name}'")
            deleted_count += 1
        except Exception as e:
            print(f"   ❌ Failed to delete '{file_path.name}': {e}")
    
    print(f"\n🎉 Deleted {deleted_count} problematic files")


def delete_malformed_files(malformed_files):
    """Delete files with malformed names"""
    print("\n🗑️  Deleting malformed files...")
    
    print("⚠️  This will permanently delete the following files:")
    for file_path in malformed_files:
        print(f"   📄 '{file_path.name}'")
    
    confirm = input("\nAre you sure? (yes/no): ").strip().lower()
    
    if confirm in ['yes', 'y']:
        deleted_count = 0
        for file_path in malformed_files:
            try:
                file_path.unlink()
                print(f"   ✅ Deleted '{file_path.name}'")
                deleted_count += 1
            except Exception as e:
                print(f"   ❌ Failed to delete '{file_path.name}': {e}")
        
        print(f"\n🎉 Deleted {deleted_count} malformed files")
    else:
        print("👋 Cancelled deletion")


def show_file_contents(files):
    """Show contents of files to help decide what to do"""
    print("\n📖 File Contents Preview:")
    
    for file_path in files:
        print(f"\n📄 File: '{file_path.name}' ({file_path.stat().st_size} bytes)")
        print("-" * 60)
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(500)  # First 500 chars
                print(content)
                if len(content) == 500:
                    print("\n... (truncated)")
        except Exception as e:
            print(f"❌ Could not read file: {e}")
        
        print("-" * 60)


def generate_clean_name(old_name, file_path):
    """Generate a clean filename for a malformed file"""
    
    # Try to extract meaningful info from content
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(1000)  # First 1000 chars
        
        # Look for metadata in HTML comments
        title_match = re.search(r'<!-- JOB_TITLE:\s*(.+?)\s*-->', content)
        company_match = re.search(r'<!-- JOB_COMPANY:\s*(.+?)\s*-->', content)
        variant_type_match = re.search(r'<!-- VARIANT_TYPE:\s*(.+?)\s*-->', content)
        
        name_parts = []
        
        if company_match:
            company = re.sub(r'[^a-zA-Z0-9]', '', company_match.group(1).lower())
            if company:
                name_parts.append(company[:10])
        
        if title_match:
            title = re.sub(r'[^a-zA-Z0-9]', '', title_match.group(1).lower())
            if title:
                name_parts.append(title[:15])
        
        if variant_type_match:
            variant_type = re.sub(r'[^a-zA-Z0-9]', '', variant_type_match.group(1).lower())
            if variant_type:
                name_parts.append(variant_type[:10])
        
        if name_parts:
            clean_name = '_'.join(name_parts) + '.html'
        else:
            # Fallback to timestamp-based name
            import time
            timestamp = int(time.time())
            clean_name = f"variant_{timestamp}.html"
        
        return clean_name
        
    except Exception:
        # Fallback to generic name
        import time
        timestamp = int(time.time())
        return f"variant_{timestamp}.html"


if __name__ == "__main__":
    main()