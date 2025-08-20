/**
 * Variants Dashboard Component - Organized blocky tree layout like original workshop
 */

class VariantsDashboardComponent {
    constructor() {
        this.variants = [];
        this.treeData = null;
        this.currentView = 'dashboard';
        this.init();
    }

    init() {
        this.bindEvents();
        this.subscribeToState();
        this.loadData();
    }

    bindEvents() {
        // Listen for tab initialization
        document.addEventListener('tab:variants:init', () => {
            this.loadData();
        });

        // View toggle buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.view-toggle')) {
                const view = e.target.dataset.view;
                this.switchView(view);
            }
        });

        // Variant actions
        document.addEventListener('click', (e) => {
            if (e.target.matches('.variant-card-action')) {
                const action = e.target.dataset.action;
                const filename = e.target.dataset.filename;
                this.handleVariantAction(action, filename);
            }
        });

        // Refresh button
        document.addEventListener('click', (e) => {
            if (e.target.matches('.refresh-dashboard-btn')) {
                this.loadData();
            }
        });
    }

    subscribeToState() {
        // Listen for variants updates
        stateManager.subscribe('variants', (variants) => {
            this.variants = variants;
            if (this.currentView === 'dashboard') {
                this.renderDashboard();
            }
        });
    }

    async loadData() {
        try {
            stateManager.setLoading(true);
            
            // Load both variants and genealogy data
            const [variants, genealogy] = await Promise.all([
                apiClient.getVariants(),
                apiClient.makeRequest('/genealogy').catch(() => ({}))
            ]);
            
            this.variants = variants;
            this.treeData = genealogy;
            stateManager.setVariants(variants);
            
            if (this.currentView === 'dashboard') {
                this.renderDashboard();
            } else {
                this.renderTreeView();
            }
            
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            
            // Clear loading state even on error
            const container = document.getElementById('variants-dashboard');
            if (container) {
                container.classList.remove('loading');
                container.classList.add('loaded');
                container.innerHTML = `
                    <div class="error-dashboard">
                        <div class="error-icon">⚠️</div>
                        <h3>Failed to Load Dashboard</h3>
                        <p>Could not load variants data. Please try refreshing.</p>
                        <button class="btn btn-secondary refresh-dashboard-btn">🔄 Try Again</button>
                    </div>
                `;
            }
            
            this.showError('Failed to load dashboard data');
        } finally {
            stateManager.setLoading(false);
        }
    }

    switchView(view) {
        this.currentView = view;
        
        // Update toggle buttons
        document.querySelectorAll('.view-toggle').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-view="${view}"]`).classList.add('active');
        
        // Update view content
        document.querySelectorAll('.view-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${view}-view`).classList.add('active');
        
        // Load appropriate content
        if (view === 'dashboard') {
            this.renderDashboard();
        } else if (view === 'tree') {
            this.renderTreeView();
        }
    }

    renderDashboard() {
        const container = document.getElementById('variants-dashboard');
        if (!container) return;

        // Clear loading state
        container.classList.remove('loading');
        container.classList.add('loaded');

        if (this.variants.length === 0) {
            this.renderEmptyDashboard(container);
            return;
        }

        // Organize variants by generation and parent
        const organized = this.organizeVariantsByGeneration();
        
        container.innerHTML = `
            <div class="dashboard-wrapper">
                <div class="generations-inline-layout">
                    ${this.renderGenerationsInline(organized)}
                </div>
                
                <div class="dashboard-controls">
                    <div class="dashboard-stats">
                        <span class="stat">📊 ${this.variants.length} Total Variants</span>
                        <span class="stat">🌱 ${organized.generations.size} Generations</span>
                        <span class="stat">🧬 ${this.variants.filter(v => v.is_hybrid).length} Hybrid</span>
                    </div>
                    <button class="btn btn-secondary refresh-dashboard-btn">🔄 Refresh</button>
                </div>
            </div>
        `;

        this.addDashboardStyles();
    }

    organizeVariantsByGeneration() {
        const generations = new Map();
        const parentChildMap = new Map();
        
        // First pass: organize by generation
        this.variants.forEach(variant => {
            const generation = variant.generation || 0;
            if (!generations.has(generation)) {
                generations.set(generation, []);
            }
            generations.get(generation).push(variant);
            
            // Track parent-child relationships
            if (variant.parents && variant.parents.length > 0) {
                variant.parents.forEach(parent => {
                    if (!parentChildMap.has(parent)) {
                        parentChildMap.set(parent, []);
                    }
                    parentChildMap.get(parent).push(variant.filename);
                });
            }
        });
        
        // Sort generations
        const sortedGenerations = new Map([...generations.entries()].sort());
        
        return {
            generations: sortedGenerations,
            parentChildMap,
            maxGeneration: Math.max(...generations.keys())
        };
    }

    renderGenerationsInline(organized) {
        let html = '';
        
        // Sort generations in proper order (0, 1, 2, 3, etc.)
        const sortedGenerations = Array.from(organized.generations.entries()).sort((a, b) => a[0] - b[0]);
        
        for (const [generation, variants] of sortedGenerations) {
            // Sort variants by creation date (newest first)
            const sortedVariants = variants.sort((a, b) => 
                new Date(b.created) - new Date(a.created)
            );
            
            html += `
                <div class="generation-column" data-generation="${generation}">
                    <div class="generation-header">
                        <h3>${this.getGenerationTitle(generation)}</h3>
                        <span class="generation-count">${variants.length}</span>
                    </div>
                    <div class="generation-scroll-area">
                        <div class="generation-variants">
                            ${sortedVariants.map(variant => this.renderVariantBlock(variant)).join('')}
                        </div>
                    </div>
                </div>
            `;
        }
        
        return html;
    }

    getGenerationTitle(generation) {
        switch (generation) {
            case 0: return '🌱 Base Templates';
            case 1: return '🔵 Generation 1';
            case 2: return '🟡 Generation 2';
            case 3: return '🟠 Generation 3';
            case 4: return '🔴 Generation 4';
            case 5: return '🟣 Generation 5';
            default: return `📈 Generation ${generation}`;
        }
    }

    renderVariantBlock(variant) {
        const createdDate = new Date(variant.created).toLocaleDateString();
        const isRecent = (Date.now() - new Date(variant.created)) < (7 * 24 * 60 * 60 * 1000); // 7 days
        const generationClass = `gen-${variant.generation || 0}`;
        const hybridClass = variant.is_hybrid ? 'hybrid' : '';
        const recentClass = isRecent ? 'recent' : '';
        
        return `
            <div class="variant-block ${generationClass} ${hybridClass} ${recentClass}" 
                 data-filename="${variant.filename}">
                <div class="variant-block-header">
                    <div class="variant-icon">
                        ${variant.is_hybrid ? '🧬' : this.getGenerationIcon(variant.generation || 0)}
                    </div>
                    <div class="variant-title">${this.truncateTitle(variant.name)}</div>
                </div>
                
                <div class="variant-block-body">
                    <div class="variant-meta">
                        <span class="variant-type">${variant.type}</span>
                        ${variant.job_title ? `<span class="job-info">📋 ${variant.job_title}</span>` : ''}
                        ${variant.job_company ? `<span class="company-info">🏢 ${variant.job_company}</span>` : ''}
                    </div>
                    
                    <div class="variant-date">${createdDate}</div>
                    
                    ${variant.parents && variant.parents.length > 0 ? 
                        `<div class="variant-parents">
                            <small>Parents: ${variant.parents.slice(0, 2).join(', ')}${variant.parents.length > 2 ? '...' : ''}</small>
                        </div>` : ''
                    }
                </div>
                
                <div class="variant-block-actions">
                    <button class="variant-card-action btn-icon" data-action="preview" data-filename="${variant.filename}" title="Preview">👁️</button>
                    <button class="variant-card-action btn-icon" data-action="download" data-filename="${variant.filename}" title="Download PDF">📄</button>
                    <button class="variant-card-action btn-icon" data-action="clone" data-filename="${variant.filename}" title="Clone">📋</button>
                    <button class="variant-card-action btn-icon danger" data-action="delete" data-filename="${variant.filename}" title="Delete">🗑️</button>
                </div>
            </div>
        `;
    }

    getGenerationIcon(generation) {
        const icons = ['🟢', '🔵', '🟡', '🟠', '🔴', '🟣'];
        return icons[generation] || '📈';
    }

    truncateTitle(title) {
        if (!title) return 'Untitled';
        return title.length > 22 ? title.substring(0, 19) + '...' : title;
    }

    async handleVariantAction(action, filename) {
        switch (action) {
            case 'preview':
                this.showPreviewModal(filename);
                break;
            case 'download':
                this.downloadPDF(filename);
                break;
            case 'clone':
                this.cloneVariant(filename);
                break;
            case 'delete':
                await this.deleteVariant(filename);
                break;
        }
    }

    async deleteVariant(filename) {
        // Use native confirm if modal component isn't available
        const confirmed = window.modalComponent 
            ? await modalComponent.confirm(`Delete variant "${filename}"?`)
            : confirm(`Delete variant "${filename}"?`);
            
        if (!confirmed) return;
        
        try {
            await apiClient.deleteVariant(filename);
            stateManager.removeVariant(filename);
            this.showSuccess(`Variant "${filename}" deleted successfully`);
            // Reload the dashboard to reflect changes
            this.loadData();
        } catch (error) {
            console.error('Failed to delete variant:', error);
            this.showError('Failed to delete variant');
        }
    }

    downloadPDF(filename) {
        const pdfName = filename.replace('.html', '.pdf');
        window.open(`/agent_workspace/output/${pdfName}`, '_blank');
    }

    cloneVariant(filename) {
        // Switch to create tab with this variant pre-selected as parent
        stateManager.setState('selectedParent', filename);
        sidebarComponent.switchTab('create');
    }

    showPreviewModal(filename) {
        // Create modal overlay
        const modal = document.createElement('div');
        modal.className = 'preview-modal-overlay';
        modal.innerHTML = `
            <div class="preview-modal">
                <div class="preview-modal-header">
                    <h3>📄 Preview: ${filename}</h3>
                    <button class="preview-modal-close">&times;</button>
                </div>
                <div class="preview-modal-body">
                    <iframe src="/agent_workspace/variants/${filename}" 
                            class="preview-iframe"
                            title="Resume Preview">
                    </iframe>
                </div>
                <div class="preview-modal-footer">
                    <button class="btn btn-secondary preview-modal-close">Close</button>
                    <button class="btn btn-primary" onclick="window.open('/agent_workspace/output/${filename.replace('.html', '.pdf')}', '_blank')">
                        📄 Download PDF
                    </button>
                </div>
            </div>
        `;

        // Add to document
        document.body.appendChild(modal);

        // Add event listeners
        modal.addEventListener('click', (e) => {
            if (e.target.classList.contains('preview-modal-overlay') || 
                e.target.classList.contains('preview-modal-close')) {
                this.closePreviewModal(modal);
            }
        });

        // Add escape key listener
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                this.closePreviewModal(modal);
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);

        // Store escape handler for cleanup
        modal._escapeHandler = escapeHandler;
    }

    closePreviewModal(modal) {
        if (modal._escapeHandler) {
            document.removeEventListener('keydown', modal._escapeHandler);
        }
        modal.remove();
    }

    renderTreeView() {
        // Delegate to tree viewer component
        if (window.treeViewerComponent) {
            treeViewerComponent.loadGenealogyTree();
        }
    }

    renderEmptyDashboard(container) {
        // Clear loading state
        container.classList.remove('loading');
        container.classList.add('loaded');
        
        container.innerHTML = `
            <div class="empty-dashboard">
                <div class="empty-icon">📊</div>
                <h3>No Variants Yet</h3>
                <p>Create your first resume variant to get started with the dashboard.</p>
                <button class="btn btn-primary" data-tab="create">⚡ Create First Variant</button>
            </div>
        `;
    }

    addDashboardStyles() {
        const styles = `
            <style id="dashboard-styles">
                #variants-dashboard {
                    width: 100%;
                    max-width: 100%;
                    overflow: hidden;
                    display: flex;
                    justify-content: center;
                    height: auto;
                }
                
                #variants-dashboard.loading {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 40px;
                    color: #666;
                }
                
                #variants-dashboard.loaded {
                    display: flex;
                    justify-content: center;
                }
                
                .dashboard-wrapper {
                    width: 1100px;
                    height: 500px;
                    display: flex;
                    flex-direction: column;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    background: #f8f9fa;
                    overflow: hidden;
                }
                
                .dashboard-controls {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 15px 20px;
                    background: #f8f9fa;
                    border-radius: 0 0 8px 8px;
                    border-top: 1px solid #e2e8f0;
                    flex-shrink: 0;
                    width: 100%;
                    box-sizing: border-box;
                }

                .dashboard-stats {
                    display: flex;
                    gap: 20px;
                }

                .stat {
                    font-size: 14px;
                    color: #666;
                    font-weight: 500;
                }

                .generations-inline-layout {
                    display: flex;
                    gap: 15px;
                    overflow-x: auto;
                    overflow-y: hidden;
                    padding: 15px;
                    flex: 1;
                    width: 100%;
                    box-sizing: border-box;
                    background: white;
                    border-radius: 8px 8px 0 0;
                }

                .generation-column {
                    flex: 0 0 250px;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    background: white;
                    display: flex;
                    flex-direction: column;
                    height: 410px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                }

                .generation-header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 12px 16px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    flex-shrink: 0;
                    border-radius: 11px 11px 0 0;
                }

                .generation-header h3 {
                    margin: 0;
                    font-size: 16px;
                    font-weight: 600;
                }

                .generation-count {
                    background: rgba(255, 255, 255, 0.2);
                    padding: 3px 10px;
                    border-radius: 10px;
                    font-size: 11px;
                    font-weight: 500;
                }

                .generation-scroll-area {
                    flex: 1;
                    overflow-y: auto;
                    padding: 0;
                }

                .generation-variants {
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                    padding: 15px;
                }

                .variant-block {
                    background: #f8f9fa;
                    border: 2px solid #e0e0e0;
                    border-radius: 6px;
                    padding: 10px;
                    transition: all 0.2s ease;
                    cursor: pointer;
                    position: relative;
                    min-height: 100px;
                    display: flex;
                    flex-direction: column;
                    width: 100%;
                }

                .variant-block:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }

                .variant-block.gen-0 {
                    border-color: #28a745;
                    background: linear-gradient(135deg, #f8fff9 0%, #f0fff4 100%);
                }

                .variant-block.gen-1 {
                    border-color: #007bff;
                    background: linear-gradient(135deg, #f8fbff 0%, #e3f2fd 100%);
                }

                .variant-block.gen-2 {
                    border-color: #ffc107;
                    background: linear-gradient(135deg, #fffef8 0%, #fff8e1 100%);
                }

                .variant-block.gen-3 {
                    border-color: #fd7e14;
                    background: linear-gradient(135deg, #fff8f0 0%, #ffe0cc 100%);
                }

                .variant-block.gen-4, .variant-block.gen-5 {
                    border-color: #dc3545;
                    background: linear-gradient(135deg, #fff5f5 0%, #ffebee 100%);
                }

                .variant-block.hybrid {
                    border-color: #6f42c1;
                    background: linear-gradient(135deg, #faf9ff 0%, #f3e5f5 100%);
                    border-style: dashed;
                }

                .variant-block.recent::after {
                    content: '✨ NEW';
                    position: absolute;
                    top: -1px;
                    right: -1px;
                    background: #28a745;
                    color: white;
                    font-size: 10px;
                    padding: 2px 8px;
                    border-radius: 0 6px 0 6px;
                    font-weight: bold;
                }

                .variant-block-header {
                    display: flex;
                    align-items: flex-start;
                    gap: 10px;
                    margin-bottom: 10px;
                }

                .variant-icon {
                    font-size: 20px;
                    flex-shrink: 0;
                }

                .variant-title {
                    font-weight: bold;
                    font-size: 13px;
                    color: #333;
                    line-height: 1.2;
                }

                .variant-block-body {
                    flex: 1;
                    margin-bottom: 10px;
                }

                .variant-meta {
                    margin-bottom: 8px;
                }

                .variant-type {
                    background: #e9ecef;
                    color: #495057;
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 11px;
                    font-weight: 500;
                    display: inline-block;
                    margin-bottom: 4px;
                }

                .job-info, .company-info {
                    display: block;
                    font-size: 11px;
                    color: #666;
                    margin: 2px 0;
                }

                .variant-date {
                    font-size: 11px;
                    color: #999;
                    margin-bottom: 8px;
                }

                .variant-parents {
                    font-size: 10px;
                    color: #6f42c1;
                    font-style: italic;
                }

                .variant-block-actions {
                    display: flex;
                    gap: 5px;
                    justify-content: flex-end;
                }

                .btn-icon {
                    background: none;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 4px 6px;
                    cursor: pointer;
                    font-size: 12px;
                    transition: all 0.2s ease;
                }

                .btn-icon:hover {
                    background: #f8f9fa;
                    border-color: #adb5bd;
                }

                .btn-icon.danger:hover {
                    background: #fff5f5;
                    border-color: #dc3545;
                    color: #dc3545;
                }

                .empty-dashboard, .error-dashboard {
                    text-align: center;
                    padding: 80px 20px;
                    color: #666;
                }

                .empty-icon, .error-icon {
                    font-size: 64px;
                    margin-bottom: 20px;
                    opacity: 0.5;
                }

                /* Preview Modal Styles */
                .preview-modal-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.8);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 1000;
                    animation: fadeIn 0.2s ease;
                }

                .preview-modal {
                    background: white;
                    border-radius: 12px;
                    width: 90%;
                    max-width: 1200px;
                    height: 90%;
                    max-height: 800px;
                    display: flex;
                    flex-direction: column;
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
                    animation: slideIn 0.3s ease;
                }

                .preview-modal-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 20px;
                    border-bottom: 1px solid #e2e8f0;
                    border-radius: 12px 12px 0 0;
                    background: #f8f9fa;
                }

                .preview-modal-header h3 {
                    margin: 0;
                    color: #333;
                    font-size: 18px;
                }

                .preview-modal-close {
                    background: none;
                    border: none;
                    font-size: 24px;
                    cursor: pointer;
                    color: #666;
                    padding: 0;
                    width: 30px;
                    height: 30px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 50%;
                    transition: all 0.2s ease;
                }

                .preview-modal-close:hover {
                    background: #e2e8f0;
                    color: #333;
                }

                .preview-modal-body {
                    flex: 1;
                    padding: 0;
                    overflow: hidden;
                }

                .preview-iframe {
                    width: 100%;
                    height: 100%;
                    border: none;
                    background: white;
                }

                .preview-modal-footer {
                    display: flex;
                    justify-content: flex-end;
                    gap: 10px;
                    padding: 20px;
                    border-top: 1px solid #e2e8f0;
                    background: #f8f9fa;
                    border-radius: 0 0 12px 12px;
                }

                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }

                @keyframes slideIn {
                    from { 
                        opacity: 0;
                        transform: scale(0.9) translateY(-20px);
                    }
                    to { 
                        opacity: 1;
                        transform: scale(1) translateY(0);
                    }
                }
            </style>
        `;
        
        if (!document.getElementById('dashboard-styles')) {
            document.head.insertAdjacentHTML('beforeend', styles);
        }
    }

    showError(message) {
        console.error(message);
    }

    showSuccess(message) {
        console.log(message);
    }
}

// Initialize when loaded
window.variantsDashboardComponent = new VariantsDashboardComponent();
console.log('✅ Variants Dashboard component loaded');