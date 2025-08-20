#!/bin/bash

# Resume Workshop PDF Converter
# Converts HTML variants to PDF with consistent formatting

WORKSHOP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="$WORKSHOP_DIR/agent_workspace/output"
VARIANTS_DIR="$WORKSHOP_DIR/agent_workspace/variants"
TEMPLATES_DIR="$WORKSHOP_DIR/agent_workspace/templates"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Function to convert HTML to PDF
convert_html_to_pdf() {
    local html_file="$1"
    local output_name="$2"
    local pdf_output="$OUTPUT_DIR/${output_name}.pdf"
    
    echo "Converting $html_file to PDF..."
    
    # Get absolute path for Chrome
    local absolute_html_path="$(realpath "$html_file")"
    
    # Chrome/Chromium conversion
    local chrome_cmd=""
    if command -v google-chrome &> /dev/null; then
        chrome_cmd="google-chrome"
    elif command -v chromium-browser &> /dev/null; then
        chrome_cmd="chromium-browser"
    elif command -v chromium &> /dev/null; then
        chrome_cmd="chromium"
    fi
    
    if [ -n "$chrome_cmd" ]; then
        echo "Using $chrome_cmd for conversion..."
        
        # Chrome PDF generation with optimized settings for resume
        $chrome_cmd --headless --disable-gpu \
            --print-to-pdf="$pdf_output" \
            --no-margins \
            --print-to-pdf-no-header \
            --disable-print-preview \
            --run-all-compositor-stages-before-draw \
            --virtual-time-budget=2000 \
            --no-pdf-header-footer \
            --disable-default-apps \
            --disable-extensions \
            "file://$absolute_html_path" 2>/dev/null
        
        if [ -f "$pdf_output" ]; then
            echo "✓ Successfully created: $pdf_output"
            echo "  Size: $(ls -lh "$pdf_output" | awk '{print $5}')"
            return 0
        else
            echo "✗ Failed to create PDF"
            return 1
        fi
    else
        echo "Error: Chrome/Chromium not found!"
        echo "Please install Chrome or Chromium"
        return 1
    fi
}

# Function to convert a specific variant
convert_variant() {
    local variant_file="$1"
    local base_name=$(basename "$variant_file" .html)
    
    if [ ! -f "$variant_file" ]; then
        echo "Error: Variant file not found: $variant_file"
        return 1
    fi
    
    convert_html_to_pdf "$variant_file" "$base_name"
}

# Function to convert all variants
convert_all_variants() {
    echo "Converting all variants to PDF..."
    echo "================================="
    
    local converted=0
    local failed=0
    
    # Convert base template
    if [ -f "$TEMPLATES_DIR/base_resume.html" ]; then
        echo "Converting base template..."
        if convert_html_to_pdf "$TEMPLATES_DIR/base_resume.html" "base_resume"; then
            ((converted++))
        else
            ((failed++))
        fi
        echo ""
    fi
    
    # Convert all variants
    if [ -d "$VARIANTS_DIR" ] && [ "$(ls -A "$VARIANTS_DIR"/*.html 2>/dev/null)" ]; then
        for variant in "$VARIANTS_DIR"/*.html; do
            echo "Converting $(basename "$variant")..."
            if convert_variant "$variant"; then
                ((converted++))
            else
                ((failed++))
            fi
            echo ""
        done
    else
        echo "No variants found in $VARIANTS_DIR"
    fi
    
    echo "================================="
    echo "Conversion Summary:"
    echo "  ✓ Successful: $converted"
    echo "  ✗ Failed: $failed"
    echo "  📁 Output directory: $OUTPUT_DIR"
    
    # List generated PDFs
    if [ $converted -gt 0 ]; then
        echo ""
        echo "Generated PDFs:"
        ls -la "$OUTPUT_DIR"/*.pdf 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
    fi
}

# Function to show usage
show_usage() {
    echo "Resume Workshop PDF Converter"
    echo "Usage: $0 [options] [variant_name]"
    echo ""
    echo "Options:"
    echo "  -a, --all           Convert all variants to PDF"
    echo "  -l, --list          List available variants"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --all                    # Convert all variants"
    echo "  $0 tech_focused             # Convert specific variant"
    echo "  $0 base_resume              # Convert base template"
    echo ""
    echo "Files:"
    echo "  Base template: $TEMPLATES_DIR/base_resume.html"
    echo "  Variants: $VARIANTS_DIR/*.html"
    echo "  Output: $OUTPUT_DIR/*.pdf"
}

# Function to list variants
list_variants() {
    echo "Available Resume Variants:"
    echo "=========================="
    
    # List base template
    if [ -f "$TEMPLATES_DIR/base_resume.html" ]; then
        echo "📄 base_resume (base template)"
    fi
    
    # List variants
    if [ -d "$VARIANTS_DIR" ] && [ "$(ls -A "$VARIANTS_DIR"/*.html 2>/dev/null)" ]; then
        for variant in "$VARIANTS_DIR"/*.html; do
            local name=$(basename "$variant" .html)
            local size=$(stat -c%s "$variant" 2>/dev/null || echo "0")
            local date=$(stat -c%y "$variant" 2>/dev/null | cut -d' ' -f1)
            echo "📝 $name ($(($size/1024))KB, created $date)"
        done
    else
        echo "No variants found in $VARIANTS_DIR"
    fi
    
    echo ""
    echo "To convert:"
    echo "  ./pdf_converter.sh --all              # All variants"
    echo "  ./pdf_converter.sh variant_name       # Specific variant"
}

# Main script logic
case "$1" in
    -a|--all)
        convert_all_variants
        ;;
    -l|--list)
        list_variants
        ;;
    -h|--help)
        show_usage
        ;;
    "")
        show_usage
        ;;
    *)
        # Convert specific variant
        variant_name="$1"
        
        # Try variants directory first
        if [ -f "$VARIANTS_DIR/${variant_name}.html" ]; then
            convert_variant "$VARIANTS_DIR/${variant_name}.html"
        # Try templates directory
        elif [ -f "$TEMPLATES_DIR/${variant_name}.html" ]; then
            convert_html_to_pdf "$TEMPLATES_DIR/${variant_name}.html" "$variant_name"
        # Try as full path
        elif [ -f "$variant_name" ]; then
            local base_name=$(basename "$variant_name" .html)
            convert_html_to_pdf "$variant_name" "$base_name"
        else
            echo "Error: Variant '$variant_name' not found!"
            echo ""
            echo "Available variants:"
            list_variants
            exit 1
        fi
        ;;
esac