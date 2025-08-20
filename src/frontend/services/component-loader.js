/**
 * Component Loader - Handles lazy loading of frontend components
 */

class ComponentLoader {
    constructor() {
        this.loadedComponents = new Set();
        this.loadingPromises = new Map();
    }

    async loadComponent(componentPath) {
        // Avoid loading the same component multiple times
        if (this.loadedComponents.has(componentPath)) {
            return;
        }

        // If already loading, return the existing promise
        if (this.loadingPromises.has(componentPath)) {
            return this.loadingPromises.get(componentPath);
        }

        const loadPromise = this._loadScript(componentPath);
        this.loadingPromises.set(componentPath, loadPromise);

        try {
            await loadPromise;
            this.loadedComponents.add(componentPath);
            this.loadingPromises.delete(componentPath);
            console.log(`✅ Loaded component: ${componentPath}`);
        } catch (error) {
            this.loadingPromises.delete(componentPath);
            console.warn(`⚠️ Optional component not loaded: ${componentPath}`, error);
            // Don't throw for missing optional components
        }
    }

    async loadMultipleComponents(componentPaths) {
        // Load components in smaller batches to reduce perceived loading time
        const batchSize = 2;
        for (let i = 0; i < componentPaths.length; i += batchSize) {
            const batch = componentPaths.slice(i, i + batchSize);
            const loadPromises = batch.map(path => this.loadComponent(path));
            await Promise.all(loadPromises);
            
            // Small delay between batches for smoother loading
            if (i + batchSize < componentPaths.length) {
                await new Promise(resolve => setTimeout(resolve, 50));
            }
        }
    }

    _loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = `/frontend/components/${src}`;
            script.onload = resolve;
            script.onerror = (error) => {
                console.warn(`Component not found: ${src} - This is normal for optional components`);
                resolve(); // Resolve instead of reject for missing optional components
            };
            document.head.appendChild(script);
        });
    }

    // Load components based on current tab/view
    async loadForTab(tabName) {
        const componentMap = {
            'variants': [
                'job-management/linkedin-fetcher.js',  // Load LinkedIn component first
                'variant-management/variants-dashboard.js',
                'genealogy/tree-viewer.js',
                'genealogy/tree-minimap.js',
                'genealogy/tree-utils.js'
            ],
            'create': [
                'job-management/linkedin-fetcher.js',  // Load LinkedIn component first
                'variant-management/variant-creator.js',
                'variant-management/parent-selector.js',
                'workflow/workflow-manager.js'
            ],
            'jobs': [
                'job-management/job-selector.js',
                'job-management/linkedin-fetcher.js'
            ],
            'preview': [
                'preview/preview-pane.js',
                'preview/pdf-generator.js',
                'preview/quality-rater.js'
            ],
            'genealogy': [
                'genealogy/tree-viewer.js',
                'genealogy/tree-minimap.js',
                'genealogy/tree-utils.js'
            ],
            'workflow': [
                'workflow/workflow-manager.js',
                'workflow/progress-tracker.js'
            ]
        };

        const components = componentMap[tabName] || [];
        if (components.length > 0) {
            console.log(`🔧 Loading components for tab: ${tabName}`);
            await this.loadMultipleComponents(components);
        }
    }

    // Preload critical components
    async preloadCritical() {
        const criticalComponents = [
            'shared/header.js',
            'shared/sidebar.js', 
            'shared/modal.js',
            'job-management/linkedin-fetcher.js'  // LinkedIn component is used across multiple tabs
        ];
        
        console.log('🚀 Preloading critical components...');
        await this.loadMultipleComponents(criticalComponents);
    }
}

// Export global instance
window.componentLoader = new ComponentLoader();