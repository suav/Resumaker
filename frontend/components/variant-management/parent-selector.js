/**
 * Parent Selector Component - Standalone parent selection utility
 */

class ParentSelectorComponent {
    constructor() {
        this.selectedParents = [];
        this.availableVariants = [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.subscribeToState();
    }

    bindEvents() {
        // This component is used within the variant creator
        // Events are handled by the parent component
    }

    subscribeToState() {
        stateManager.subscribe('variants', (variants) => {
            this.availableVariants = variants;
        });
    }

    // Utility methods for parent selection
    static organizeVariantsByCategory(variants) {
        const organized = {
            'Base Templates': [],
            'Recent Variants': [],
            'Generation 1': [],
            'Generation 2+': [],
            'Hybrid Variants': []
        };

        variants.forEach(variant => {
            const generation = variant.generation || 0;
            const isRecent = (Date.now() - new Date(variant.created)) < (7 * 24 * 60 * 60 * 1000);
            
            if (generation === 0) {
                organized['Base Templates'].push(variant);
            } else if (variant.is_hybrid) {
                organized['Hybrid Variants'].push(variant);
            } else if (isRecent) {
                organized['Recent Variants'].push(variant);
            } else if (generation === 1) {
                organized['Generation 1'].push(variant);
            } else {
                organized['Generation 2+'].push(variant);
            }
        });

        return organized;
    }

    static renderParentCard(variant, isSelected = false) {
        const generationClass = `gen-${variant.generation || 0}`;
        
        return `
            <div class="parent-card ${generationClass} ${isSelected ? 'selected' : ''}" data-filename="${variant.filename}">
                <div class="parent-card-header">
                    <div class="parent-icon">
                        ${variant.is_hybrid ? '🧬' : ParentSelectorComponent.getGenerationIcon(variant.generation || 0)}
                    </div>
                    <div class="parent-title">${ParentSelectorComponent.truncateTitle(variant.name)}</div>
                </div>
                <div class="parent-card-body">
                    <div class="parent-type">${variant.type}</div>
                    ${variant.job_title ? `<div class="parent-job">📋 ${variant.job_title}</div>` : ''}
                    <div class="parent-date">${new Date(variant.created).toLocaleDateString()}</div>
                </div>
                <div class="parent-card-footer">
                    <button class="parent-card-select btn btn-sm ${isSelected ? 'btn-selected' : 'btn-outline'}" 
                            data-filename="${variant.filename}">
                        ${isSelected ? '✓ Selected' : 'Select'}
                    </button>
                </div>
            </div>
        `;
    }

    static getGenerationIcon(generation) {
        const icons = ['🟢', '🔵', '🟡', '🟠', '🔴', '🟣'];
        return icons[generation] || '📈';
    }

    static truncateTitle(title) {
        if (!title) return 'Untitled';
        return title.length > 25 ? title.substring(0, 22) + '...' : title;
    }
}

// Initialize when loaded
window.parentSelectorComponent = new ParentSelectorComponent();
console.log('✅ Parent Selector component loaded');