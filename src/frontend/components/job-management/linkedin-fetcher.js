/**
 * LinkedIn Fetcher Component - Handles fetching job data from LinkedIn URLs
 */

class LinkedInFetcherComponent {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
    }

    bindEvents() {
        // Global LinkedIn fetch functionality for any component that needs it
        document.addEventListener('linkedin:fetch', (e) => {
            this.fetchLinkedInJob(e.detail.url, e.detail.callback);
        });
        
        // Direct button handlers with debugging
        document.addEventListener('click', (e) => {
            if (e.target.matches('.linkedin-fetch-btn')) {
                console.log('🔗 LinkedIn fetch button clicked:', e.target);
                this.handleFetchButton(e.target);
            }
        });
        
        console.log('🔗 LinkedIn fetcher event handlers bound');
    }

    async handleFetchButton(button) {
        console.log('🔗 LinkedIn fetch button handler called:', button);
        
        const container = button.closest('.linkedin-fetch-container') || 
                          button.closest('.linkedin-mini-section') ||
                          button.closest('.linkedin-section');
        
        console.log('🔗 Found container:', container);
        
        if (!container) {
            console.warn('🔗 No LinkedIn container found for button');
            return;
        }

        // Find URL input with multiple selectors
        const urlInput = container.querySelector('.linkedin-url-input') ||
                         container.querySelector('#branch-linkedin-url') ||
                         container.querySelector('#linkedin-url-input') ||
                         container.querySelector('input[type="url"]');
        
        console.log('🔗 Found URL input:', urlInput);
        
        if (!urlInput) {
            console.warn('🔗 No URL input found in container');
            this.showError('LinkedIn URL input not found');
            return;
        }

        const url = urlInput.value.trim();
        console.log('🔗 URL value:', url);
        
        if (!url) {
            this.showError('Please enter a LinkedIn job URL');
            return;
        }

        // Find target fields with multiple selectors
        const targetTextarea = container.querySelector('.linkedin-target-textarea') ||
                               document.querySelector('#job-description') ||
                               document.querySelector('#job-description-textarea') ||
                               document.querySelector('#job-content-textarea');
        
        const titleInput = container.querySelector('.linkedin-target-title') ||
                          document.querySelector('#job-title-input');
        
        const companyInput = container.querySelector('.linkedin-target-company') ||
                            document.querySelector('#job-company-input') ||
                            document.querySelector('#company-name-input');

        console.log('🔗 Target fields found:', { targetTextarea, titleInput, companyInput });

        await this.fetchLinkedInJob(url, (result) => {
            console.log('🔗 LinkedIn fetch result:', result);
            
            if (result.success) {
                // Populate target fields
                if (targetTextarea && result.content) {
                    targetTextarea.value = result.content;
                    targetTextarea.dispatchEvent(new Event('input', { bubbles: true }));
                }
                if (titleInput && result.title) {
                    titleInput.value = result.title;
                    titleInput.dispatchEvent(new Event('input', { bubbles: true }));
                }
                if (companyInput && result.company) {
                    companyInput.value = result.company;
                    companyInput.dispatchEvent(new Event('input', { bubbles: true }));
                }
                
                // Clear the URL input
                urlInput.value = '';
                
                this.showSuccess('LinkedIn job data fetched successfully!');
            } else {
                this.showError('Failed to fetch LinkedIn data: ' + (result.message || result.error));
            }
        });
    }

    async fetchLinkedInJob(url, callback) {
        if (!this.isValidLinkedInUrl(url)) {
            const error = { success: false, message: 'Please enter a valid LinkedIn job URL' };
            if (callback) callback(error);
            return error;
        }

        try {
            this.setFetchingState(true, url);
            
            const result = await apiClient.fetchLinkedInJob(url);
            
            if (callback) callback(result);
            return result;
            
        } catch (error) {
            console.error('LinkedIn fetch error:', error);
            const errorResult = { 
                success: false, 
                message: 'Network error while fetching LinkedIn data' 
            };
            if (callback) callback(errorResult);
            return errorResult;
        } finally {
            this.setFetchingState(false);
        }
    }

    isValidLinkedInUrl(url) {
        try {
            const urlObj = new URL(url);
            return urlObj.hostname.includes('linkedin.com') && 
                   urlObj.pathname.includes('/jobs/');
        } catch {
            return false;
        }
    }

    setFetchingState(fetching, url = '') {
        // Update all LinkedIn fetch buttons
        document.querySelectorAll('.linkedin-fetch-btn').forEach(btn => {
            if (fetching) {
                btn.disabled = true;
                btn.textContent = '⏳ Fetching...';
                btn.classList.add('fetching');
            } else {
                btn.disabled = false;
                btn.textContent = '🔗 Fetch';
                btn.classList.remove('fetching');
            }
        });

        // Show global status if needed
        if (fetching && url) {
            this.showFetchingProgress(url);
        }
    }

    showFetchingProgress(url) {
        // Could show a progress indicator
        console.log(`Fetching LinkedIn job from: ${url}`);
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `linkedin-notification ${type}`;
        notification.textContent = message;
        
        // Style based on type
        const isError = type === 'error';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${isError ? '#fed7d7' : '#d4edda'};
            color: ${isError ? '#9b2c2c' : '#155724'};
            border: 1px solid ${isError ? '#feb2b2' : '#c3e6cb'};
            border-radius: 4px;
            padding: 12px 16px;
            z-index: 1000;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-width: 400px;
            word-wrap: break-word;
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
        
        // Click to dismiss
        notification.addEventListener('click', () => {
            notification.remove();
        });
    }

    // Utility function to create LinkedIn fetch UI components
    static createFetchWidget(options = {}) {
        const {
            urlInputId = 'linkedin-url',
            targetTextareaId = '',
            targetTitleId = '',
            targetCompanyId = '',
            placeholder = 'https://linkedin.com/jobs/view/...',
            buttonText = '🔗 Fetch'
        } = options;

        return `
            <div class="linkedin-fetch-container">
                <div class="linkedin-fetch-group">
                    <label>LinkedIn Job URL:</label>
                    <div class="linkedin-input-group">
                        <input type="url" 
                               class="linkedin-url-input" 
                               id="${urlInputId}"
                               placeholder="${placeholder}" />
                        <button type="button" 
                                class="linkedin-fetch-btn btn btn-secondary"
                                ${targetTextareaId ? `data-target-textarea="${targetTextareaId}"` : ''}
                                ${targetTitleId ? `data-target-title="${targetTitleId}"` : ''}
                                ${targetCompanyId ? `data-target-company="${targetCompanyId}"` : ''}>
                            ${buttonText}
                        </button>
                    </div>
                    <small class="linkedin-help">
                        Enter a LinkedIn job posting URL to automatically extract job details
                    </small>
                </div>
            </div>
        `;
    }

    // Method to enhance existing forms with LinkedIn functionality
    static enhanceForm(formSelector, options = {}) {
        const form = document.querySelector(formSelector);
        if (!form) return;

        const {
            urlInputSelector = '[name="linkedin_url"]',
            jobDescriptionSelector = '[name="job_description"]',
            jobTitleSelector = '[name="job_title"]',
            companyNameSelector = '[name="company_name"]'
        } = options;

        // Add LinkedIn fetch capability to the form
        const urlInput = form.querySelector(urlInputSelector);
        const jobDescTextarea = form.querySelector(jobDescriptionSelector);
        const jobTitleInput = form.querySelector(jobTitleSelector);
        const companyInput = form.querySelector(companyNameSelector);

        if (urlInput && jobDescTextarea) {
            // Add classes for the fetcher to work
            urlInput.classList.add('linkedin-url-input');
            jobDescTextarea.classList.add('linkedin-target-textarea');
            
            if (jobTitleInput) jobTitleInput.classList.add('linkedin-target-title');
            if (companyInput) companyInput.classList.add('linkedin-target-company');

            // Make the container detectable
            const container = urlInput.closest('div') || urlInput.parentElement;
            container.classList.add('linkedin-fetch-container');
        }
    }
}

// Initialize when loaded
window.linkedInFetcherComponent = new LinkedInFetcherComponent();
console.log('✅ LinkedIn Fetcher component loaded');