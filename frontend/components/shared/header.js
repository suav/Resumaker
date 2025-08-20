/**
 * Header Component
 */

class HeaderComponent {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.subscribeToState();
    }

    bindEvents() {
        // Header-specific event handlers can go here
        console.log('Header component initialized');
    }

    subscribeToState() {
        // Listen for global state changes if needed
        stateManager.subscribe('loading', (loading) => {
            this.updateLoadingIndicator(loading);
        });
    }

    updateLoadingIndicator(loading) {
        const indicator = document.getElementById('loading-indicator');
        if (indicator) {
            indicator.style.display = loading ? 'inline' : 'none';
        }
    }
}

// Initialize header when loaded
window.headerComponent = new HeaderComponent();
console.log('✅ Header component loaded');