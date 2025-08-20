/**
 * Sidebar Navigation Component
 */

class SidebarComponent {
    constructor() {
        this.currentTab = 'variants';
        this.init();
    }

    init() {
        this.bindEvents();
        this.subscribeToState();
    }

    bindEvents() {
        // Tab switching
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-tab]')) {
                const tab = e.target.dataset.tab;
                this.switchTab(tab);
            }
        });

        // View toggle within tabs
        document.addEventListener('click', (e) => {
            if (e.target.matches('.view-toggle')) {
                const view = e.target.dataset.view;
                this.switchView(view);
            }
        });
    }

    subscribeToState() {
        // Listen for tab changes
        stateManager.subscribe('currentTab', (newTab) => {
            this.updateActiveTab(newTab);
        });

        // Listen for loading states
        stateManager.subscribe('loading', (loading) => {
            this.toggleLoadingState(loading);
        });
    }

    async switchTab(tabName) {
        if (this.currentTab === tabName) return;

        try {
            // Set loading state
            stateManager.setLoading(true);

            // Load components for the new tab
            await componentLoader.loadForTab(tabName);

            // Update state
            stateManager.setCurrentTab(tabName);
            this.currentTab = tabName;

            // Show the new tab content
            this.showTabContent(tabName);

            // Trigger tab-specific initialization
            this.initializeTab(tabName);

        } catch (error) {
            console.error(`Failed to switch to tab: ${tabName}`, error);
        } finally {
            stateManager.setLoading(false);
        }
    }

    updateActiveTab(tabName) {
        // Update sidebar button states
        document.querySelectorAll('[data-tab]').forEach(btn => {
            btn.classList.remove('active');
        });

        const activeBtn = document.querySelector(`[data-tab="${tabName}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }
    }

    showTabContent(tabName) {
        // Hide all tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });

        // Show the selected tab content
        const tabContent = document.getElementById(`${tabName}-tab`);
        if (tabContent) {
            tabContent.classList.add('active');
        }
    }

    toggleLoadingState(loading) {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            if (loading) {
                sidebar.classList.add('component-loading');
            } else {
                sidebar.classList.remove('component-loading');
                sidebar.classList.add('component-loaded');
            }
        }
    }

    switchView(view) {
        // Update view toggle buttons
        document.querySelectorAll('.view-toggle').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const activeBtn = document.querySelector(`[data-view="${view}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }

        // Update view content
        document.querySelectorAll('.view-content').forEach(content => {
            content.classList.remove('active');
        });

        const viewContent = document.getElementById(`${view}-view`);
        if (viewContent) {
            viewContent.classList.add('active');
        }

        // Trigger view-specific initialization
        if (view === 'tree') {
            // Load genealogy tree components if switching to tree view
            if (window.treeViewerComponent) {
                treeViewerComponent.loadGenealogyTree();
            }
        } else if (view === 'dashboard') {
            // Refresh dashboard if switching to dashboard view
            if (window.variantsDashboardComponent) {
                variantsDashboardComponent.loadData();
            }
        }
    }

    initializeTab(tabName) {
        // Trigger initialization for specific tabs
        const initEvent = new CustomEvent(`tab:${tabName}:init`);
        document.dispatchEvent(initEvent);
    }
}

// Initialize sidebar when loaded
window.sidebarComponent = new SidebarComponent();
console.log('✅ Sidebar component loaded');