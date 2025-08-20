/**
 * Variant List Component - Handles variant display and management
 */

class VariantListComponent {
    constructor() {
        this.variants = [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.subscribeToState();
        this.loadVariants();
    }

    bindEvents() {
        // Listen for tab initialization
        document.addEventListener('tab:variants:init', () => {
            this.loadVariants();
        });

        // Delete variant buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.delete-variant-btn')) {
                const filename = e.target.dataset.filename;
                this.deleteVariant(filename);
            }
        });

        // Refresh button
        document.addEventListener('click', (e) => {
            if (e.target.matches('.refresh-variants-btn')) {
                this.loadVariants();
            }
        });
    }

    subscribeToState() {
        // Listen for variants updates
        stateManager.subscribe('variants', (variants) => {
            this.variants = variants;
            this.renderVariants();
        });
    }

    async loadVariants() {
        try {
            stateManager.setLoading(true);
            const variants = await apiClient.getVariants();
            stateManager.setVariants(variants);
        } catch (error) {
            console.error('Failed to load variants:', error);
            this.showError('Failed to load variants');
        } finally {
            stateManager.setLoading(false);
        }
    }

    async deleteVariant(filename) {
        if (!confirm(`Delete variant "${filename}"?`)) return;

        try {
            await apiClient.deleteVariant(filename);
            stateManager.removeVariant(filename);
            this.showSuccess(`Variant "${filename}" deleted successfully`);
        } catch (error) {
            console.error('Failed to delete variant:', error);
            this.showError('Failed to delete variant');
        }
    }

    renderVariants() {
        const container = document.getElementById('variants-list');
        if (!container) return;

        if (this.variants.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>No variants found</p>
                    <button class="btn btn-primary" data-tab="workflow">Create Your First Variant</button>
                </div>
            `;
            return;
        }

        const variantsHTML = this.variants.map(variant => this.renderVariantCard(variant)).join('');
        
        container.innerHTML = `
            <div class="variants-header">
                <h3>Resume Variants (${this.variants.length})</h3>
                <button class="btn btn-secondary refresh-variants-btn">🔄 Refresh</button>
            </div>
            <div class="variants-grid">
                ${variantsHTML}
            </div>
        `;
    }

    renderVariantCard(variant) {
        const createdDate = new Date(variant.created).toLocaleDateString();
        const isHybrid = variant.is_hybrid ? '🧬' : '';
        
        return `
            <div class="variant-card" data-filename="${variant.filename}">
                <div class="variant-header">
                    <h4>${isHybrid} ${variant.name}</h4>
                    <div class="variant-actions">
                        <button class="btn btn-sm btn-outline preview-btn" 
                                data-filename="${variant.filename}">👁️</button>
                        <button class="btn btn-sm btn-danger delete-variant-btn" 
                                data-filename="${variant.filename}">🗑️</button>
                    </div>
                </div>
                <div class="variant-info">
                    <p class="variant-type">${variant.type}</p>
                    <p class="variant-description">${variant.description}</p>
                    <p class="variant-date">Created: ${createdDate}</p>
                    ${variant.job_title ? `<p class="job-info">📋 ${variant.job_title} at ${variant.job_company || 'N/A'}</p>` : ''}
                    ${variant.is_hybrid ? `<p class="hybrid-info">👥 Parents: ${variant.parents.join(', ')}</p>` : ''}
                </div>
            </div>
        `;
    }

    showError(message) {
        // Simple error display - could be enhanced with a toast system
        console.error(message);
    }

    showSuccess(message) {
        // Simple success display - could be enhanced with a toast system
        console.log(message);
    }
}

// Initialize when loaded
window.variantListComponent = new VariantListComponent();
console.log('✅ Variant List component loaded');