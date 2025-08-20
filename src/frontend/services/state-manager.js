/**
 * State Manager - Centralized application state management
 */

class StateManager {
    constructor() {
        this.state = {
            currentTab: 'variants',
            variants: [],
            jobDescriptions: [],
            selectedParents: [],
            currentVariant: null,
            loading: false,
            backgroundJobs: []
        };
        this.listeners = new Map();
    }

    // Subscribe to state changes
    subscribe(key, callback) {
        if (!this.listeners.has(key)) {
            this.listeners.set(key, []);
        }
        this.listeners.get(key).push(callback);

        // Return unsubscribe function
        return () => {
            const callbacks = this.listeners.get(key);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        };
    }

    // Update state and notify listeners
    setState(key, value) {
        const oldValue = this.state[key];
        this.state[key] = value;

        // Notify listeners if value changed
        if (oldValue !== value && this.listeners.has(key)) {
            this.listeners.get(key).forEach(callback => callback(value, oldValue));
        }
    }

    // Get current state value
    getState(key) {
        return this.state[key];
    }

    // Get all state
    getAllState() {
        return { ...this.state };
    }

    // Convenience methods for common operations
    setCurrentTab(tab) {
        this.setState('currentTab', tab);
    }

    setVariants(variants) {
        this.setState('variants', variants);
    }

    addVariant(variant) {
        const variants = [...this.state.variants, variant];
        this.setState('variants', variants);
    }

    removeVariant(filename) {
        const variants = this.state.variants.filter(v => v.filename !== filename);
        this.setState('variants', variants);
    }

    setLoading(loading) {
        this.setState('loading', loading);
    }

    updateBackgroundJobs(jobs) {
        this.setState('backgroundJobs', jobs);
    }

    addSelectedParent(parent) {
        const selectedParents = [...this.state.selectedParents];
        if (!selectedParents.includes(parent)) {
            selectedParents.push(parent);
            this.setState('selectedParents', selectedParents);
        }
    }

    removeSelectedParent(parent) {
        const selectedParents = this.state.selectedParents.filter(p => p !== parent);
        this.setState('selectedParents', selectedParents);
    }

    clearSelectedParents() {
        this.setState('selectedParents', []);
    }
}

// Export global instance
window.stateManager = new StateManager();