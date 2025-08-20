/**
 * Variant Creator Component - Mirrors the original workshop create interface
 */

class VariantCreatorComponent {
    constructor() {
        this.selectedParents = [];
        this.availableVariants = [];
        this.savedJobs = [];
        this.selectedJobDescription = null;
        this.currentStep = 'parent-selection';
        this.init();
    }

    init() {
        this.bindEvents();
        this.subscribeToState();
    }

    bindEvents() {
        // Listen for create tab initialization
        document.addEventListener('tab:create:init', () => {
            this.loadCreateInterface();
        });

        // Parent selection
        document.addEventListener('click', (e) => {
            if (e.target.matches('.parent-card-select')) {
                const filename = e.target.dataset.filename;
                this.toggleParentSelection(filename);
            }
        });

        // LinkedIn URL fetching
        document.addEventListener('click', (e) => {
            if (e.target.matches('#fetch-linkedin-btn')) {
                this.fetchLinkedInJob();
            }
        });

        // Saved jobs loading and selection
        document.addEventListener('click', (e) => {
            if (e.target.matches('#load-saved-jobs-btn')) {
                this.loadSavedJobs();
            } else if (e.target.matches('.saved-job-card')) {
                const filename = e.target.dataset.filename;
                this.selectSavedJob(filename);
            }
        });

        // Step navigation
        document.addEventListener('click', (e) => {
            if (e.target.matches('.step-nav-btn')) {
                const step = e.target.dataset.step;
                this.goToStep(step);
            }
        });

        // Create variant
        document.addEventListener('click', (e) => {
            if (e.target.matches('#create-variant-btn')) {
                this.createVariant();
            }
        });

        // Clear selections
        document.addEventListener('click', (e) => {
            if (e.target.matches('#clear-parents-btn')) {
                this.clearParentSelections();
            }
        });
    }

    subscribeToState() {
        // Listen for pre-selected parent (from clone action)
        stateManager.subscribe('selectedParent', (parent) => {
            if (parent && !this.selectedParents.includes(parent)) {
                this.selectedParents = [parent];
                this.updateParentDisplay();
            }
        });

        stateManager.subscribe('variants', (variants) => {
            this.availableVariants = variants;
        });

        // Listen for pre-selected job description (from jobs tab)
        stateManager.subscribe('selectedJobDescription', (jobDesc) => {
            if (jobDesc) {
                this.selectedJobDescription = jobDesc;
                this.populateJobFields(jobDesc);
            }
        });
    }

    async loadCreateInterface() {
        const container = document.getElementById('create-content');
        if (!container) return;

        try {
            // Load variants for parent selection and saved jobs
            this.availableVariants = await apiClient.getVariants();
            await this.loadSavedJobs();
            this.renderCreateInterface(container);
        } catch (error) {
            console.error('Failed to load create interface:', error);
            container.innerHTML = `
                <div class="error-state">
                    <h3>⚠️ Failed to Load</h3>
                    <p>Could not load the variant creation interface.</p>
                    <button class="btn btn-primary" onclick="location.reload()">Reload Page</button>
                </div>
            `;
        }
    }

    renderCreateInterface(container) {
        container.innerHTML = `
            <div class="create-workflow">
                <!-- Progress Steps -->
                <div class="workflow-steps">
                    <div class="step ${this.currentStep === 'parent-selection' ? 'active' : ''}" data-step="parent-selection">
                        <span class="step-number">1</span>
                        <span class="step-title">Select Parent</span>
                    </div>
                    <div class="step ${this.currentStep === 'job-input' ? 'active' : ''}" data-step="job-input">
                        <span class="step-number">2</span>
                        <span class="step-title">Job Description</span>
                    </div>
                    <div class="step ${this.currentStep === 'customization' ? 'active' : ''}" data-step="customization">
                        <span class="step-number">3</span>
                        <span class="step-title">Customize</span>
                    </div>
                    <div class="step ${this.currentStep === 'review' ? 'active' : ''}" data-step="review">
                        <span class="step-number">4</span>
                        <span class="step-title">Review & Create</span>
                    </div>
                </div>

                <!-- Step Content -->
                <div class="step-content">
                    ${this.renderStepContent()}
                </div>

                <!-- Navigation -->
                <div class="step-navigation">
                    ${this.renderStepNavigation()}
                </div>
            </div>
        `;

        this.addCreateStyles();
    }

    renderStepContent() {
        switch (this.currentStep) {
            case 'parent-selection':
                return this.renderParentSelection();
            case 'job-input':
                return this.renderJobInput();
            case 'customization':
                return this.renderCustomization();
            case 'review':
                return this.renderReview();
            default:
                return '<p>Unknown step</p>';
        }
    }

    renderParentSelection() {
        // Organize variants like the original selector
        const organizedVariants = this.organizeVariantsForSelection();
        
        return `
            <div class="parent-selection-step">
                <h3>Select Parent Template(s)</h3>
                <p>Choose one or more parent templates to base your new variant on:</p>
                
                <div class="selection-controls">
                    <div class="selected-parents-display">
                        <strong>Selected (${this.selectedParents.length}):</strong>
                        ${this.selectedParents.length > 0 ? 
                            this.selectedParents.map(p => `<span class="selected-tag">${this.getShortName(p)} <button class="remove-parent" data-filename="${p}">×</button></span>`).join('') :
                            '<span class="no-selection">None selected</span>'
                        }
                        <button id="clear-parents-btn" class="btn btn-sm btn-outline" ${this.selectedParents.length === 0 ? 'disabled' : ''}>Clear All</button>
                    </div>
                </div>

                <div class="parents-grid">
                    ${Object.entries(organizedVariants).map(([category, variants]) => `
                        <div class="parent-category">
                            <h4>${category}</h4>
                            <div class="parent-cards">
                                ${variants.map(variant => this.renderParentCard(variant)).join('')}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    organizeVariantsForSelection() {
        const organized = {
            'Base Templates': [],
            'Recent Variants': [],
            'Generation 1': [],
            'Generation 2+': [],
            'Hybrid Variants': []
        };

        this.availableVariants.forEach(variant => {
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

        // Remove empty categories
        Object.keys(organized).forEach(key => {
            if (organized[key].length === 0) {
                delete organized[key];
            }
        });

        return organized;
    }

    renderParentCard(variant) {
        const isSelected = this.selectedParents.includes(variant.filename);
        const generationClass = `gen-${variant.generation || 0}`;
        
        return `
            <div class="parent-card ${generationClass} ${isSelected ? 'selected' : ''}" data-filename="${variant.filename}">
                <div class="parent-card-header">
                    <div class="parent-icon">
                        ${variant.is_hybrid ? '🧬' : this.getGenerationIcon(variant.generation || 0)}
                    </div>
                    <div class="parent-title">${this.truncateTitle(variant.name)}</div>
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

    renderJobInput() {
        return `
            <div class="job-input-step">
                <h3>Job Description</h3>
                <p>Choose from saved jobs or provide a new job description:</p>
                
                <!-- Saved Jobs Section -->
                <div class="saved-jobs-section">
                    <div class="section-header">
                        <label>📋 Use Saved Job Description:</label>
                        <button id="load-saved-jobs-btn" class="btn btn-sm btn-outline">🔄 Refresh</button>
                    </div>
                    <div id="saved-jobs-selector" class="saved-jobs-grid">
                        <div class="loading-jobs">Loading saved jobs...</div>
                    </div>
                </div>

                <!-- OR Divider -->
                <div class="input-divider">
                    <span>OR</span>
                </div>
                
                <!-- LinkedIn Fetch Section -->
                <div class="linkedin-fetch-section linkedin-fetch-container">
                    <label>🔗 Fetch from LinkedIn:</label>
                    <div class="linkedin-input-group">
                        <input type="url" id="linkedin-url-input" class="linkedin-url-input" 
                               placeholder="https://linkedin.com/jobs/view/..." />
                        <button id="fetch-linkedin-btn" class="linkedin-fetch-btn btn btn-secondary">🔗 Fetch</button>
                    </div>
                </div>

                <!-- OR Divider -->
                <div class="input-divider">
                    <span>OR</span>
                </div>

                <!-- Manual Input Section -->
                <div class="manual-input-section">
                    <label>✏️ Enter Manually:</label>
                    
                    <div class="job-quick-info">
                        <div class="input-group">
                            <label>Job Title:</label>
                            <input type="text" id="job-title-input" class="linkedin-target-title" 
                                   placeholder="e.g., Senior Software Engineer" />
                        </div>
                        <div class="input-group">
                            <label>Company Name:</label>
                            <input type="text" id="company-name-input" class="linkedin-target-company" 
                                   placeholder="e.g., TechCorp" />
                        </div>
                    </div>

                    <div class="job-description-section">
                        <label>Job Description:</label>
                        <textarea id="job-description-textarea" class="linkedin-target-textarea"
                                  placeholder="Paste the complete job description here..."
                                  rows="8"></textarea>
                    </div>
                </div>

                <!-- Save New Job Option -->
                <div class="save-job-section">
                    <label>
                        <input type="checkbox" id="save-new-job-checkbox"> 
                        💾 Save this job description for future use
                    </label>
                </div>
            </div>
        `;
    }

    renderCustomization() {
        return `
            <div class="customization-step">
                <h3>Customize Your Variant</h3>
                <p>Configure the optimization settings:</p>

                <div class="customization-form">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Variant Name:</label>
                            <input type="text" id="variant-name-input" placeholder="Auto-generated from job info" />
                            <small>Leave blank to auto-generate from job title and company</small>
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label>Focus Type:</label>
                            <select id="focus-type-select">
                                <option value="">Auto-detect from job description</option>
                                <option value="technical">Technical Focus</option>
                                <option value="leadership">Leadership Focus</option>
                                <option value="backend">Backend Development</option>
                                <option value="frontend">Frontend Development</option>
                                <option value="fullstack">Full Stack Development</option>
                                <option value="devops">DevOps/Infrastructure</option>
                                <option value="product">Product Management</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label>Generation Notes:</label>
                            <textarea id="generation-notes-textarea" 
                                      placeholder="Any specific instructions for the AI generator..."
                                      rows="3"></textarea>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderReview() {
        const jobTitle = document.getElementById('job-title-input')?.value || 'Target Position';
        const companyName = document.getElementById('company-name-input')?.value || 'Target Company';
        const variantName = document.getElementById('variant-name-input')?.value || 'Auto-generated';
        
        return `
            <div class="review-step">
                <h3>Review & Create</h3>
                <p>Review your settings before creating the variant:</p>

                <div class="review-summary">
                    <div class="summary-section">
                        <h4>Parent Template(s):</h4>
                        <ul class="parents-list">
                            ${this.selectedParents.map(parent => `<li>${this.getShortName(parent)}</li>`).join('')}
                        </ul>
                    </div>

                    <div class="summary-section">
                        <h4>Target Position:</h4>
                        <p><strong>${jobTitle}</strong> at <strong>${companyName}</strong></p>
                    </div>

                    <div class="summary-section">
                        <h4>Variant Name:</h4>
                        <p>${variantName}</p>
                    </div>

                    <div class="summary-section">
                        <h4>Job Description:</h4>
                        <div class="job-preview">
                            ${(document.getElementById('job-description-textarea')?.value || 'No job description provided').substring(0, 200)}...
                        </div>
                    </div>
                </div>

                <div class="create-action">
                    <button id="create-variant-btn" class="btn btn-primary btn-large">
                        🚀 Create Resume Variant
                    </button>
                </div>

                <div id="creation-progress" class="creation-progress" style="display: none;">
                    <p>⏳ Creating your optimized resume variant...</p>
                    <div class="progress-bar">
                        <div class="progress-fill"></div>
                    </div>
                    <div class="progress-status">Initializing AI generation...</div>
                </div>
            </div>
        `;
    }

    renderStepNavigation() {
        const steps = ['parent-selection', 'job-input', 'customization', 'review'];
        const currentIndex = steps.indexOf(this.currentStep);
        
        return `
            <button class="step-nav-btn btn btn-secondary" 
                    data-step="${steps[currentIndex - 1]}" 
                    ${currentIndex === 0 ? 'disabled' : ''}>
                ← Previous
            </button>
            
            <button class="step-nav-btn btn btn-primary" 
                    data-step="${steps[currentIndex + 1]}" 
                    ${currentIndex === steps.length - 1 ? 'disabled' : ''}>
                Next →
            </button>
        `;
    }

    toggleParentSelection(filename) {
        const index = this.selectedParents.indexOf(filename);
        if (index > -1) {
            this.selectedParents.splice(index, 1);
        } else {
            this.selectedParents.push(filename);
        }
        this.updateParentDisplay();
    }

    updateParentDisplay() {
        // Re-render the current step to show updated selections
        const container = document.querySelector('.step-content');
        if (container) {
            container.innerHTML = this.renderStepContent();
        }
    }

    async fetchLinkedInJob() {
        const urlInput = document.getElementById('linkedin-url-input');
        const url = urlInput?.value;
        
        if (!url) {
            alert('Please enter a LinkedIn job URL');
            return;
        }

        try {
            const result = await apiClient.fetchLinkedInJob(url);
            
            if (result.success) {
                // Populate form fields
                if (result.title) document.getElementById('job-title-input').value = result.title;
                if (result.company) document.getElementById('company-name-input').value = result.company;
                if (result.content) document.getElementById('job-description-textarea').value = result.content;
                
                alert('LinkedIn job data fetched successfully!');
            } else {
                alert('Failed to fetch LinkedIn data: ' + result.message);
            }
        } catch (error) {
            console.error('LinkedIn fetch error:', error);
            alert('Error fetching LinkedIn data');
        }
    }

    goToStep(step) {
        if (!step) return;
        
        this.currentStep = step;
        this.renderCreateInterface(document.getElementById('create-content'));
    }

    async createVariant() {
        const progressDiv = document.getElementById('creation-progress');
        const button = document.getElementById('create-variant-btn');
        
        try {
            // Show progress
            progressDiv.style.display = 'block';
            button.disabled = true;
            
            // Gather form data
            const jobTitle = document.getElementById('job-title-input')?.value || '';
            const companyName = document.getElementById('company-name-input')?.value || '';
            const jobDescription = document.getElementById('job-description-textarea')?.value || '';
            const shouldSaveJob = document.getElementById('save-new-job-checkbox')?.checked || false;
            
            // Save job description if requested and it's new content
            if (shouldSaveJob && jobDescription.trim() && jobTitle.trim()) {
                try {
                    await this.saveJobDescription(jobTitle, companyName, jobDescription);
                } catch (error) {
                    console.warn('Failed to save job description:', error);
                    // Don't fail variant creation if job save fails
                }
            }
            
            const variantData = {
                parent: this.selectedParents[0] || 'base_resume_v2.html',
                job_description: jobDescription,
                job_title: jobTitle,
                company_name: companyName,
                focus_type: document.getElementById('focus-type-select')?.value || '',
                variant_name: document.getElementById('variant-name-input')?.value || '',
                generation_notes: document.getElementById('generation-notes-textarea')?.value || ''
            };

            // Create variant
            const result = await apiClient.createVariant(variantData);
            
            if (result.success) {
                alert('Variant creation started! Check the dashboard for progress.');
                sidebarComponent.switchTab('variants');
            } else {
                throw new Error(result.message || 'Creation failed');
            }
            
        } catch (error) {
            console.error('Variant creation error:', error);
            alert('Failed to create variant: ' + error.message);
        } finally {
            progressDiv.style.display = 'none';
            button.disabled = false;
        }
    }

    async saveJobDescription(title, company, content) {
        // Auto-generate filename
        const safeTitle = title.toLowerCase().replace(/[^a-z0-9]/g, '_');
        const safeCompany = company.toLowerCase().replace(/[^a-z0-9]/g, '_');
        const filename = `${safeCompany}_${safeTitle}.txt`;
        
        // Construct full content with metadata
        let fullContent = '';
        if (title) fullContent += `Title: ${title}\n`;
        if (company) fullContent += `Company: ${company}\n\n`;
        fullContent += content;
        
        return await apiClient.saveJobDescription({
            name: filename,
            content: fullContent,
            is_main: false
        });
    }

    clearParentSelections() {
        this.selectedParents = [];
        this.updateParentDisplay();
    }

    async loadSavedJobs() {
        try {
            this.savedJobs = await apiClient.getJobDescriptions();
            this.renderSavedJobsSelector();
        } catch (error) {
            console.error('Failed to load saved jobs:', error);
            // Don't fail the whole interface, just show error in jobs section
            this.renderSavedJobsError();
        }
    }

    renderSavedJobsSelector() {
        const container = document.getElementById('saved-jobs-selector');
        if (!container) return;

        if (this.savedJobs.length === 0) {
            container.innerHTML = `
                <div class="no-saved-jobs">
                    <p>📄 No saved jobs yet</p>
                    <small>Create some in the Jobs tab first</small>
                </div>
            `;
            return;
        }

        container.innerHTML = this.savedJobs.map(job => this.renderSavedJobCard(job)).join('');
    }

    renderSavedJobCard(job) {
        const isSelected = this.selectedJobDescription && 
                          this.selectedJobDescription.filename === job.filename;
        const isActive = job.active || false;
        
        return `
            <div class="saved-job-card ${isSelected ? 'selected' : ''} ${isActive ? 'active' : ''}" 
                 data-filename="${job.filename}">
                <div class="job-card-header">
                    <div class="job-icon">${isActive ? '🎯' : '📋'}</div>
                    <div class="job-info">
                        <div class="job-title">${job.title}</div>
                        <div class="job-company">${job.company}</div>
                    </div>
                    ${isActive ? '<div class="active-badge">Active</div>' : ''}
                </div>
                <div class="job-preview">${job.preview}</div>
                <div class="job-select-btn">
                    ${isSelected ? '✓ Selected' : 'Select'}
                </div>
            </div>
        `;
    }

    renderSavedJobsError() {
        const container = document.getElementById('saved-jobs-selector');
        if (!container) return;

        container.innerHTML = `
            <div class="jobs-error">
                <p>⚠️ Failed to load saved jobs</p>
                <button id="load-saved-jobs-btn" class="btn btn-sm btn-outline">🔄 Retry</button>
            </div>
        `;
    }

    selectSavedJob(filename) {
        const job = this.savedJobs.find(j => j.filename === filename);
        if (!job) return;

        this.selectedJobDescription = job;
        
        // Populate form fields
        this.populateJobFields({
            title: job.title,
            company: job.company,
            content: this.getJobContent(job)
        });

        // Update UI
        this.renderSavedJobsSelector();
    }

    populateJobFields(jobData) {
        // Populate job fields if the current step has them visible
        const titleInput = document.getElementById('job-title-input');
        const companyInput = document.getElementById('company-name-input');
        const descTextarea = document.getElementById('job-description-textarea');

        if (titleInput && jobData.title) {
            titleInput.value = jobData.title;
        }
        if (companyInput && jobData.company) {
            companyInput.value = jobData.company;
        }
        if (descTextarea && jobData.content) {
            descTextarea.value = jobData.content;
        }
    }

    getJobContent(job) {
        if (!job) return '';
        
        // If job has content property, use it directly
        if (job.content) return job.content;
        
        // Otherwise construct from available data
        let content = '';
        if (job.title && job.title !== 'Unknown Position') {
            content += `Title: ${job.title}\n`;
        }
        if (job.company && job.company !== 'Unknown Company') {
            content += `Company: ${job.company}\n\n`;
        }
        
        // Add preview content if available (removing the "..." if present)
        if (job.preview) {
            const preview = job.preview.replace(/\.\.\.+$/, '');
            content += preview;
        }
        
        return content;
    }

    getGenerationIcon(generation) {
        const icons = ['🟢', '🔵', '🟡', '🟠', '🔴', '🟣'];
        return icons[generation] || '📈';
    }

    getShortName(filename) {
        return filename.replace('.html', '').replace(/_/g, ' ');
    }

    truncateTitle(title) {
        if (!title) return 'Untitled';
        return title.length > 25 ? title.substring(0, 22) + '...' : title;
    }

    addCreateStyles() {
        // Add styles for the create interface (similar to dashboard styles)
        const styles = `
            <style id="create-styles">
                .create-workflow {
                    max-width: 900px;
                    margin: 0 auto;
                }

                .workflow-steps {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 30px;
                    padding: 0 20px;
                    position: relative;
                }

                .workflow-steps::before {
                    content: '';
                    position: absolute;
                    top: 20px;
                    left: 50px;
                    right: 50px;
                    height: 2px;
                    background: #e0e0e0;
                    z-index: 0;
                }

                .step {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    position: relative;
                    cursor: pointer;
                    z-index: 1;
                }

                .step-number {
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    background: #e0e0e0;
                    color: #666;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    margin-bottom: 8px;
                }

                .step.active .step-number {
                    background: #667eea;
                    color: white;
                }

                .step-title {
                    font-size: 12px;
                    color: #666;
                    text-align: center;
                }

                .step.active .step-title {
                    color: #667eea;
                    font-weight: bold;
                }

                .step-content {
                    background: #f8f9fa;
                    border-radius: 12px;
                    padding: 30px;
                    margin-bottom: 20px;
                    min-height: 400px;
                }

                .parents-grid {
                    margin-top: 20px;
                }

                .parent-category {
                    margin-bottom: 25px;
                }

                .parent-category h4 {
                    margin: 0 0 15px 0;
                    color: #667eea;
                    border-bottom: 1px solid #e0e0e0;
                    padding-bottom: 5px;
                }

                .parent-cards {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                    gap: 15px;
                }

                .parent-card {
                    background: white;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 15px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                }

                .parent-card:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }

                .parent-card.selected {
                    border-color: #667eea;
                    background: #f8fbff;
                    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
                }

                .parent-card-header {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    margin-bottom: 10px;
                }

                .parent-icon {
                    font-size: 18px;
                }

                .parent-title {
                    font-weight: bold;
                    color: #333;
                    font-size: 14px;
                }

                .parent-card-body {
                    margin-bottom: 15px;
                }

                .parent-type {
                    background: #e9ecef;
                    color: #495057;
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 11px;
                    display: inline-block;
                    margin-bottom: 8px;
                }

                .parent-job, .parent-date {
                    font-size: 12px;
                    color: #666;
                    margin: 3px 0;
                }

                .btn-selected {
                    background: #667eea;
                    color: white;
                    border-color: #667eea;
                }

                .selected-parents-display {
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    border: 1px solid #e0e0e0;
                }

                .selected-tag {
                    background: #667eea;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-size: 12px;
                    margin-right: 8px;
                    display: inline-block;
                }

                .remove-parent {
                    background: none;
                    border: none;
                    color: white;
                    margin-left: 5px;
                    cursor: pointer;
                    font-weight: bold;
                }

                .linkedin-input-group {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 20px;
                }

                .linkedin-input-group input {
                    flex: 1;
                }

                .form-group {
                    margin-bottom: 20px;
                }

                .form-group label {
                    display: block;
                    margin-bottom: 5px;
                    font-weight: bold;
                    color: #333;
                }

                .form-group input,
                .form-group select,
                .form-group textarea {
                    width: 100%;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 14px;
                }

                .step-navigation {
                    display: flex;
                    justify-content: space-between;
                    padding: 0 20px;
                }

                .btn-large {
                    padding: 15px 30px;
                    font-size: 16px;
                }

                .creation-progress {
                    text-align: center;
                    margin-top: 20px;
                    padding: 20px;
                    background: #fff;
                    border-radius: 8px;
                    border: 1px solid #e0e0e0;
                }

                .progress-bar {
                    width: 100%;
                    height: 8px;
                    background: #e0e0e0;
                    border-radius: 4px;
                    overflow: hidden;
                    margin: 15px 0;
                }

                .progress-fill {
                    height: 100%;
                    background: #667eea;
                    animation: indeterminate 2s infinite linear;
                }

                @keyframes indeterminate {
                    0% { margin-left: -100%; width: 100%; }
                    50% { margin-left: 0%; width: 100%; }
                    100% { margin-left: 100%; width: 100%; }
                }

                /* Job Input Step Styles */
                .saved-jobs-section {
                    margin-bottom: 25px;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    background: #f8f9fa;
                    padding: 15px;
                }

                .section-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 15px;
                }

                .section-header label {
                    font-weight: 600;
                    color: #2d3748;
                    margin: 0;
                }

                .saved-jobs-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                    gap: 12px;
                }

                .saved-job-card {
                    background: white;
                    border: 2px solid #e2e8f0;
                    border-radius: 6px;
                    padding: 12px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    position: relative;
                }

                .saved-job-card:hover {
                    border-color: #3182ce;
                    transform: translateY(-1px);
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }

                .saved-job-card.selected {
                    border-color: #3182ce;
                    background: #ebf8ff;
                    box-shadow: 0 0 0 2px rgba(49, 130, 206, 0.2);
                }

                .saved-job-card.active {
                    border-color: #38a169;
                    background: #f0fff4;
                }

                .job-card-header {
                    display: flex;
                    align-items: flex-start;
                    gap: 10px;
                    margin-bottom: 8px;
                }

                .job-icon {
                    font-size: 16px;
                    margin-top: 2px;
                }

                .job-info {
                    flex: 1;
                }

                .job-info .job-title {
                    font-weight: 600;
                    color: #2d3748;
                    font-size: 13px;
                    margin-bottom: 2px;
                    line-height: 1.3;
                }

                .job-info .job-company {
                    color: #4a5568;
                    font-size: 12px;
                }

                .active-badge {
                    background: #38a169;
                    color: white;
                    padding: 2px 6px;
                    border-radius: 10px;
                    font-size: 9px;
                    font-weight: 500;
                }

                .saved-job-card .job-preview {
                    color: #718096;
                    font-size: 11px;
                    line-height: 1.3;
                    margin-bottom: 8px;
                    max-height: 32px;
                    overflow: hidden;
                    display: -webkit-box;
                    -webkit-line-clamp: 2;
                    -webkit-box-orient: vertical;
                }

                .job-select-btn {
                    background: #f7fafc;
                    color: #4a5568;
                    text-align: center;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: 500;
                    border: 1px solid #e2e8f0;
                }

                .saved-job-card.selected .job-select-btn {
                    background: #3182ce;
                    color: white;
                    border-color: #3182ce;
                }

                .no-saved-jobs, .jobs-error, .loading-jobs {
                    text-align: center;
                    padding: 30px 20px;
                    color: #718096;
                    grid-column: 1 / -1;
                }

                .input-divider {
                    text-align: center;
                    margin: 20px 0;
                    position: relative;
                }

                .input-divider::before {
                    content: '';
                    position: absolute;
                    top: 50%;
                    left: 0;
                    right: 0;
                    height: 1px;
                    background: #e2e8f0;
                }

                .input-divider span {
                    background: #f8f9fa;
                    padding: 0 15px;
                    color: #718096;
                    font-size: 12px;
                    font-weight: 500;
                }

                .linkedin-fetch-section {
                    margin-bottom: 25px;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    background: #f8f9fa;
                    padding: 15px;
                }

                .linkedin-fetch-section label {
                    font-weight: 600;
                    color: #2d3748;
                    margin-bottom: 10px;
                    display: block;
                }

                .linkedin-input-group {
                    display: flex;
                    gap: 10px;
                }

                .linkedin-input-group input {
                    flex: 1;
                    padding: 8px 12px;
                    border: 1px solid #e2e8f0;
                    border-radius: 4px;
                    font-size: 13px;
                }

                .manual-input-section {
                    margin-bottom: 25px;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    background: #f8f9fa;
                    padding: 15px;
                }

                .manual-input-section > label {
                    font-weight: 600;
                    color: #2d3748;
                    margin-bottom: 15px;
                    display: block;
                }

                .save-job-section {
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 6px;
                    padding: 12px;
                    margin-top: 20px;
                }

                .save-job-section label {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    font-size: 13px;
                    color: #856404;
                    cursor: pointer;
                    margin: 0;
                }

                .save-job-section input[type="checkbox"] {
                    margin: 0;
                }
            </style>
        `;
        
        if (!document.getElementById('create-styles')) {
            document.head.insertAdjacentHTML('beforeend', styles);
        }
    }
}

// Initialize when loaded
window.variantCreatorComponent = new VariantCreatorComponent();
console.log('✅ Variant Creator component loaded');