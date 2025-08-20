/**
 * Centralized API client for Resume Workshop
 */

class APIClient {
    constructor() {
        this.baseURL = '';
    }

    async makeRequest(endpoint, options = {}) {
        try {
            const url = `${this.baseURL}/api${endpoint}`;
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    }

    // Variant API methods
    async getVariants() {
        return this.makeRequest('/variants');
    }

    async deleteVariant(filename) {
        return this.makeRequest('/delete-variant', {
            method: 'POST',
            body: JSON.stringify({ filename })
        });
    }

    async createVariant(data) {
        return this.makeRequest('/create-variant', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async getVariantStatus() {
        return this.makeRequest('/variant-status');
    }

    // Job description API methods
    async getJobDescriptions() {
        return this.makeRequest('/job-descriptions');
    }

    async saveJobDescription(data) {
        return this.makeRequest('/save-job-description', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async deleteJobDescription(filename) {
        return this.makeRequest('/delete-job-description', {
            method: 'POST',
            body: JSON.stringify({ filename })
        });
    }

    // LinkedIn API methods
    async fetchLinkedInJob(url) {
        return this.makeRequest(`/fetch-linkedin?url=${encodeURIComponent(url)}`);
    }
}

// Export global instance
window.apiClient = new APIClient();