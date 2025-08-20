/**
 * Job Selector Component - Manages saved job descriptions
 */

class JobSelectorComponent {
    constructor() {
        this.savedJobs = [];
        this.selectedJob = null;
        this.editingJob = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadSavedJobs();
    }

    bindEvents() {
        // Listen for jobs tab initialization
        document.addEventListener('tab:jobs:init', () => {
            this.loadJobsInterface();
        });

        // Job selection events
        document.addEventListener('click', (e) => {
            if (e.target.matches('.job-card')) {
                const filename = e.target.dataset.filename;
                this.selectJob(filename);
            }
        });

        // Action buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('#new-job-btn')) {
                this.createNewJob();
            } else if (e.target.matches('#edit-job-btn')) {
                this.editSelectedJob();
            } else if (e.target.matches('#delete-job-btn')) {
                this.deleteSelectedJob();
            } else if (e.target.matches('#save-job-btn')) {
                this.saveCurrentJob();
            } else if (e.target.matches('#cancel-edit-btn')) {
                this.cancelEdit();
            } else if (e.target.matches('#use-job-btn')) {
                this.useSelectedJob();
            }
        });

        // Auto-save on content change
        document.addEventListener('input', (e) => {
            if (e.target.matches('#job-content-textarea')) {
                this.handleContentChange();
            }
        });

        // LinkedIn fetch functionality - delegate to LinkedIn component
        document.addEventListener('click', (e) => {
            if (e.target.matches('.linkedin-fetch-btn') && e.target.closest('.jobs-manager')) {
                this.handleLinkedInFetch(e.target);
            }
        });
    }

    async loadSavedJobs() {
        try {
            this.savedJobs = await apiClient.getJobDescriptions();
            this.renderJobsList();
        } catch (error) {
            console.error('Failed to load saved jobs:', error);
            this.showError('Failed to load saved jobs');
        }
    }

    async loadJobsInterface() {
        const container = document.getElementById('jobs-content');
        if (!container) return;

        try {
            await this.loadSavedJobs();
            this.renderJobsInterface(container);
        } catch (error) {
            console.error('Failed to load jobs interface:', error);
            container.innerHTML = `
                <div class="error-state">
                    <h3>⚠️ Failed to Load</h3>
                    <p>Could not load the job management interface.</p>
                    <button class="btn btn-primary" onclick="location.reload()">Reload Page</button>
                </div>
            `;
        }
    }

    renderJobsInterface(container) {
        container.innerHTML = `
            <div class="jobs-manager">
                <!-- Jobs List Section -->
                <div class="jobs-list-section">
                    <div class="jobs-header">
                        <h3>📋 Saved Job Descriptions</h3>
                        <div class="jobs-actions">
                            <button id="new-job-btn" class="btn btn-primary">
                                ➕ New Job
                            </button>
                        </div>
                    </div>
                    
                    <div id="jobs-list" class="jobs-list">
                        ${this.renderJobsList()}
                    </div>
                </div>

                <!-- Job Editor Section -->
                <div class="job-editor-section">
                    <div class="editor-header">
                        <h3 id="editor-title">Job Description Editor</h3>
                        <div class="editor-actions">
                            <button id="edit-job-btn" class="btn btn-secondary" disabled>
                                ✏️ Edit
                            </button>
                            <button id="delete-job-btn" class="btn btn-danger" disabled>
                                🗑️ Delete
                            </button>
                            <button id="use-job-btn" class="btn btn-success" disabled>
                                🚀 Use for Variant
                            </button>
                        </div>
                    </div>

                    <div class="job-editor">
                        ${this.renderJobEditor()}
                    </div>
                </div>
            </div>
        `;

        this.addJobsStyles();
    }

    renderJobsList() {
        if (this.savedJobs.length === 0) {
            return `
                <div class="empty-jobs-state">
                    <p>📄 No saved job descriptions yet</p>
                    <p>Create your first job description to get started</p>
                </div>
            `;
        }

        return this.savedJobs.map(job => this.renderJobCard(job)).join('');
    }

    renderJobCard(job) {
        const isSelected = this.selectedJob && this.selectedJob.filename === job.filename;
        const isActive = job.active || false;
        
        return `
            <div class="job-card ${isSelected ? 'selected' : ''} ${isActive ? 'active' : ''}" 
                 data-filename="${job.filename}">
                <div class="job-card-header">
                    <div class="job-icon">
                        ${isActive ? '🎯' : '📋'}
                    </div>
                    <div class="job-title-area">
                        <div class="job-title">${job.title}</div>
                        <div class="job-company">${job.company}</div>
                    </div>
                    ${isActive ? '<div class="active-badge">Active</div>' : ''}
                </div>
                <div class="job-card-body">
                    <div class="job-preview">${job.preview}</div>
                    <div class="job-meta">
                        <span class="job-date">Created ${new Date(job.created).toLocaleDateString()}</span>
                        <span class="job-filename">${job.filename}</span>
                    </div>
                </div>
            </div>
        `;
    }

    renderJobEditor() {
        const job = this.selectedJob;
        const isEditing = this.editingJob !== null;

        if (!job && !isEditing) {
            return `
                <div class="no-job-selected">
                    <p>👈 Select a job description from the list to view or edit</p>
                    <p>Or create a new job description to get started</p>
                </div>
            `;
        }

        const currentJob = isEditing ? this.editingJob : job;
        const isReadOnly = !isEditing;

        return `
            <div class="job-form">
                <div class="job-metadata">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Job Title:</label>
                            <input type="text" id="job-title-input" 
                                   value="${currentJob?.title || ''}" 
                                   ${isReadOnly ? 'readonly' : ''} 
                                   placeholder="e.g., Senior Software Engineer">
                        </div>
                        <div class="form-group">
                            <label>Company:</label>
                            <input type="text" id="job-company-input" 
                                   value="${currentJob?.company || ''}" 
                                   ${isReadOnly ? 'readonly' : ''} 
                                   placeholder="e.g., TechCorp Inc.">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Filename:</label>
                            <input type="text" id="job-filename-input" 
                                   value="${currentJob?.filename || ''}" 
                                   ${isReadOnly ? 'readonly' : ''} 
                                   placeholder="job_description.txt">
                        </div>
                    </div>
                </div>

                ${isEditing ? this.renderLinkedInSection() : ''}

                <div class="job-content-area">
                    <label>Job Description Content:</label>
                    <textarea id="job-content-textarea" 
                              ${isReadOnly ? 'readonly' : ''} 
                              placeholder="Paste the complete job description here..."
                              rows="15">${this.getJobContent(currentJob)}</textarea>
                </div>

                ${isEditing ? this.renderEditActions() : ''}
            </div>
        `;
    }

    renderEditActions() {
        return `
            <div class="edit-actions">
                <button id="save-job-btn" class="btn btn-primary">
                    💾 Save Changes
                </button>
                <button id="cancel-edit-btn" class="btn btn-secondary">
                    ❌ Cancel
                </button>
            </div>
        `;
    }

    renderLinkedInSection() {
        return `
            <div class="linkedin-section">
                <h4>🔗 Import from LinkedIn</h4>
                <div class="linkedin-fetch-container">
                    <div class="linkedin-input-group">
                        <input type="url" 
                               class="linkedin-url-input" 
                               id="job-linkedin-url"
                               placeholder="https://linkedin.com/jobs/view/..." />
                        <button type="button" 
                                class="linkedin-fetch-btn btn btn-secondary">
                            🔗 Fetch Job Data
                        </button>
                    </div>
                    <small class="linkedin-help">
                        Enter a LinkedIn job posting URL to automatically extract job details
                    </small>
                </div>
            </div>
        `;
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
        
        // Add preview content if available
        if (job.preview) {
            const preview = job.preview.replace('...', '');
            content += preview;
        }
        
        return content;
    }

    selectJob(filename) {
        this.selectedJob = this.savedJobs.find(job => job.filename === filename);
        this.editingJob = null;
        
        // Update UI
        this.updateJobSelection();
        this.updateJobEditor();
        this.updateActionButtons();
    }

    updateJobSelection() {
        // Update selected state in job cards
        document.querySelectorAll('.job-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        if (this.selectedJob) {
            const selectedCard = document.querySelector(`[data-filename="${this.selectedJob.filename}"]`);
            if (selectedCard) {
                selectedCard.classList.add('selected');
            }
        }
    }

    updateJobEditor() {
        const editorContainer = document.querySelector('.job-editor');
        if (editorContainer) {
            editorContainer.innerHTML = this.renderJobEditor();
        }
    }

    updateActionButtons() {
        const hasSelection = this.selectedJob !== null;
        const isEditing = this.editingJob !== null;
        
        // Update button states
        const editBtn = document.getElementById('edit-job-btn');
        const deleteBtn = document.getElementById('delete-job-btn');
        const useBtn = document.getElementById('use-job-btn');
        
        if (editBtn) editBtn.disabled = !hasSelection || isEditing;
        if (deleteBtn) deleteBtn.disabled = !hasSelection || isEditing;
        if (useBtn) useBtn.disabled = !hasSelection || isEditing;
    }

    createNewJob() {
        this.editingJob = {
            filename: '',
            title: '',
            company: '',
            content: '',
            isNew: true
        };
        this.selectedJob = null;
        
        this.updateJobSelection();
        this.updateJobEditor();
        this.updateActionButtons();
        
        // Focus on title input
        setTimeout(() => {
            const titleInput = document.getElementById('job-title-input');
            if (titleInput) titleInput.focus();
        }, 100);
    }

    editSelectedJob() {
        if (!this.selectedJob) return;
        
        // Create editable copy
        this.editingJob = {
            ...this.selectedJob,
            content: this.getJobContent(this.selectedJob),
            isNew: false
        };
        
        this.updateJobEditor();
        this.updateActionButtons();
    }

    async saveCurrentJob() {
        if (!this.editingJob) return;
        
        try {
            // Get form data
            const title = document.getElementById('job-title-input')?.value || '';
            const company = document.getElementById('job-company-input')?.value || '';
            const filename = document.getElementById('job-filename-input')?.value || '';
            const content = document.getElementById('job-content-textarea')?.value || '';
            
            // Validate required fields
            if (!title.trim()) {
                alert('Please enter a job title');
                return;
            }
            
            if (!content.trim()) {
                alert('Please enter job description content');
                return;
            }
            
            // Auto-generate filename if not provided
            let finalFilename = filename.trim();
            if (!finalFilename) {
                const safeTitle = title.toLowerCase().replace(/[^a-z0-9]/g, '_');
                const safeCompany = company.toLowerCase().replace(/[^a-z0-9]/g, '_');
                finalFilename = `${safeCompany}_${safeTitle}.txt`;
            }
            
            // Ensure .txt extension
            if (!finalFilename.endsWith('.txt')) {
                finalFilename += '.txt';
            }
            
            // Construct full content with metadata
            let fullContent = '';
            if (title) fullContent += `Title: ${title}\n`;
            if (company) fullContent += `Company: ${company}\n\n`;
            fullContent += content;
            
            // Save via API
            const result = await apiClient.saveJobDescription({
                name: finalFilename,
                content: fullContent,
                is_main: false
            });
            
            if (result.success) {
                // Reload saved jobs
                await this.loadSavedJobs();
                
                // Select the saved job
                this.selectedJob = this.savedJobs.find(job => job.filename === result.filename);
                this.editingJob = null;
                
                this.updateJobSelection();
                this.updateJobEditor();
                this.updateActionButtons();
                
                this.showSuccess('Job description saved successfully!');
            } else {
                throw new Error(result.message || 'Save failed');
            }
            
        } catch (error) {
            console.error('Failed to save job:', error);
            alert('Failed to save job description: ' + error.message);
        }
    }

    cancelEdit() {
        this.editingJob = null;
        this.updateJobEditor();
        this.updateActionButtons();
    }

    async deleteSelectedJob() {
        if (!this.selectedJob) return;
        
        const confirmDelete = confirm(`Are you sure you want to delete "${this.selectedJob.title}"?`);
        if (!confirmDelete) return;
        
        try {
            const result = await apiClient.deleteJobDescription(this.selectedJob.filename);
            
            if (result.success) {
                // Remove from local list
                this.savedJobs = this.savedJobs.filter(job => job.filename !== this.selectedJob.filename);
                this.selectedJob = null;
                this.editingJob = null;
                
                // Update UI
                this.renderJobsList();
                this.updateJobEditor();
                this.updateActionButtons();
                
                // Refresh jobs list
                const jobsList = document.getElementById('jobs-list');
                if (jobsList) {
                    jobsList.innerHTML = this.renderJobsList();
                }
                
                this.showSuccess('Job description deleted successfully!');
            } else {
                throw new Error(result.message || 'Delete failed');
            }
            
        } catch (error) {
            console.error('Failed to delete job:', error);
            alert('Failed to delete job description: ' + error.message);
        }
    }

    useSelectedJob() {
        if (!this.selectedJob) return;
        
        // Store selected job in state manager for use in variant creation
        stateManager.setState('selectedJobDescription', {
            title: this.selectedJob.title,
            company: this.selectedJob.company,
            content: this.getJobContent(this.selectedJob)
        });
        
        // Switch to create tab and pre-fill job data
        sidebarComponent.switchTab('create');
        
        this.showSuccess('Job description ready for variant creation!');
    }

    async handleLinkedInFetch(button) {
        const urlInput = document.getElementById('job-linkedin-url');
        if (!urlInput) return;

        const url = urlInput.value.trim();
        if (!url) {
            this.showError('Please enter a LinkedIn job URL');
            return;
        }

        try {
            // Show loading state
            button.disabled = true;
            button.textContent = '⏳ Fetching...';

            const result = await apiClient.fetchLinkedInJob(url);

            if (result.success) {
                // Populate the form fields
                const titleInput = document.getElementById('job-title-input');
                const companyInput = document.getElementById('job-company-input');
                const contentTextarea = document.getElementById('job-content-textarea');

                if (titleInput && result.title) {
                    titleInput.value = result.title;
                }
                if (companyInput && result.company) {
                    companyInput.value = result.company;
                }
                if (contentTextarea && result.content) {
                    contentTextarea.value = result.content;
                }

                // Clear the URL input
                urlInput.value = '';

                this.showSuccess('LinkedIn job data fetched successfully!');
            } else {
                this.showError('Failed to fetch LinkedIn data: ' + (result.message || result.error));
            }
        } catch (error) {
            console.error('LinkedIn fetch error:', error);
            this.showError('Error fetching LinkedIn data: ' + error.message);
        } finally {
            // Restore button state
            button.disabled = false;
            button.textContent = '🔗 Fetch Job Data';
        }
    }

    handleContentChange() {
        // Could implement auto-save or dirty state tracking here
    }

    showSuccess(message) {
        // Simple success notification - could be enhanced
        const notification = document.createElement('div');
        notification.className = 'job-success-notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            border-radius: 4px;
            padding: 12px 16px;
            z-index: 1000;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }

    showError(message) {
        console.error(message);
        alert(message); // Could be enhanced with proper error UI
    }

    addJobsStyles() {
        const styles = `
            <style id="jobs-styles">
                .jobs-manager {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    height: 600px;
                }

                .jobs-list-section {
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    overflow: hidden;
                    background: white;
                }

                .jobs-header {
                    background: #f8f9fa;
                    border-bottom: 1px solid #e2e8f0;
                    padding: 16px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }

                .jobs-header h3 {
                    margin: 0;
                    color: #2d3748;
                    font-size: 16px;
                }

                .jobs-list {
                    height: 520px;
                    overflow-y: auto;
                    padding: 10px;
                }

                .job-card {
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                    padding: 12px;
                    margin-bottom: 10px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    background: white;
                }

                .job-card:hover {
                    border-color: #3182ce;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }

                .job-card.selected {
                    border-color: #3182ce;
                    background: #ebf8ff;
                    box-shadow: 0 0 0 2px rgba(49, 130, 206, 0.2);
                }

                .job-card.active {
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
                    font-size: 18px;
                    margin-top: 2px;
                }

                .job-title-area {
                    flex: 1;
                }

                .job-title {
                    font-weight: 600;
                    color: #2d3748;
                    font-size: 14px;
                    margin-bottom: 2px;
                }

                .job-company {
                    color: #4a5568;
                    font-size: 13px;
                }

                .active-badge {
                    background: #38a169;
                    color: white;
                    padding: 2px 6px;
                    border-radius: 10px;
                    font-size: 10px;
                    font-weight: 500;
                }

                .job-preview {
                    color: #718096;
                    font-size: 12px;
                    line-height: 1.4;
                    margin-bottom: 8px;
                    max-height: 40px;
                    overflow: hidden;
                }

                .job-meta {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    font-size: 11px;
                    color: #a0aec0;
                }

                .job-editor-section {
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    overflow: hidden;
                    background: white;
                }

                .editor-header {
                    background: #f8f9fa;
                    border-bottom: 1px solid #e2e8f0;
                    padding: 16px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }

                .editor-header h3 {
                    margin: 0;
                    color: #2d3748;
                    font-size: 16px;
                }

                .editor-actions {
                    display: flex;
                    gap: 8px;
                }

                .job-editor {
                    padding: 20px;
                    height: 520px;
                    overflow-y: auto;
                }

                .no-job-selected {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100%;
                    color: #718096;
                    text-align: center;
                }

                .job-form {
                    height: 100%;
                    display: flex;
                    flex-direction: column;
                }

                .job-metadata {
                    margin-bottom: 20px;
                }

                .form-row {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 15px;
                    margin-bottom: 15px;
                }

                .form-row:last-child {
                    grid-template-columns: 1fr;
                }

                .form-group {
                    display: flex;
                    flex-direction: column;
                }

                .form-group label {
                    margin-bottom: 4px;
                    font-weight: 500;
                    color: #4a5568;
                    font-size: 13px;
                }

                .form-group input {
                    padding: 8px 10px;
                    border: 1px solid #e2e8f0;
                    border-radius: 4px;
                    font-size: 13px;
                    color: #2d3748;
                }

                .form-group input:focus {
                    outline: none;
                    border-color: #3182ce;
                    box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
                }

                .form-group input[readonly] {
                    background: #f7fafc;
                    color: #718096;
                }

                .job-content-area {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                }

                .job-content-area label {
                    margin-bottom: 8px;
                    font-weight: 500;
                    color: #4a5568;
                    font-size: 13px;
                }

                #job-content-textarea {
                    flex: 1;
                    padding: 10px;
                    border: 1px solid #e2e8f0;
                    border-radius: 4px;
                    font-size: 13px;
                    font-family: monospace;
                    line-height: 1.4;
                    resize: none;
                }

                #job-content-textarea:focus {
                    outline: none;
                    border-color: #3182ce;
                    box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
                }

                #job-content-textarea[readonly] {
                    background: #f7fafc;
                    color: #718096;
                }

                .edit-actions {
                    margin-top: 15px;
                    display: flex;
                    gap: 10px;
                    padding-top: 15px;
                    border-top: 1px solid #e2e8f0;
                }

                .empty-jobs-state {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 200px;
                    color: #718096;
                    text-align: center;
                }

                .empty-jobs-state p {
                    margin: 5px 0;
                }

                /* LinkedIn Integration Styles */
                .linkedin-section {
                    margin-bottom: 20px;
                    padding: 15px;
                    border: 1px solid #e0e7ff;
                    border-radius: 8px;
                    background: #f8faff;
                }

                .linkedin-section h4 {
                    margin: 0 0 15px 0;
                    color: #3b4790;
                    font-size: 14px;
                    font-weight: 600;
                }

                .linkedin-input-group {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 8px;
                }

                .linkedin-url-input {
                    flex: 1;
                    padding: 8px 12px;
                    border: 1px solid #d1d5db;
                    border-radius: 4px;
                    font-size: 13px;
                }

                .linkedin-url-input:focus {
                    outline: none;
                    border-color: #3b82f6;
                    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
                }

                .linkedin-fetch-btn {
                    white-space: nowrap;
                    min-width: 120px;
                }

                .linkedin-help {
                    color: #6b7280;
                    font-size: 12px;
                    font-style: italic;
                }
            </style>
        `;
        
        if (!document.getElementById('jobs-styles')) {
            document.head.insertAdjacentHTML('beforeend', styles);
        }
    }
}

// Initialize when loaded
window.jobSelectorComponent = new JobSelectorComponent();
console.log('✅ Job Selector component loaded');