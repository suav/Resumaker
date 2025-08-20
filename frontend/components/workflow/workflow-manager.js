/**
 * Workflow Manager Component - Handles step-by-step variant creation
 */

class WorkflowManagerComponent {
    constructor() {
        this.currentStep = 0;
        this.steps = [
            { id: 'parent', title: 'Select Parent Template', component: 'parent-selector' },
            { id: 'job', title: 'Job Description', component: 'job-input' },
            { id: 'customize', title: 'Customize', component: 'variant-options' },
            { id: 'generate', title: 'Generate', component: 'variant-generator' }
        ];
        this.init();
    }

    init() {
        this.bindEvents();
        this.subscribeToState();
        this.renderWorkflow();
    }

    bindEvents() {
        // Listen for workflow tab initialization
        document.addEventListener('tab:workflow:init', () => {
            this.renderWorkflow();
        });

        // Step navigation
        document.addEventListener('click', (e) => {
            if (e.target.matches('.workflow-next')) {
                this.nextStep();
            } else if (e.target.matches('.workflow-prev')) {
                this.prevStep();
            } else if (e.target.matches('.workflow-step-btn')) {
                const step = parseInt(e.target.dataset.step);
                this.goToStep(step);
            }
        });
    }

    subscribeToState() {
        // Listen for state changes that affect workflow
        stateManager.subscribe('selectedParents', (parents) => {
            this.updateStepState('parent', parents.length > 0);
        });
    }

    renderWorkflow() {
        const container = document.getElementById('workflow-content');
        if (!container) return;

        container.innerHTML = `
            <div class="workflow-container">
                <div class="workflow-steps">
                    ${this.steps.map((step, index) => this.renderStepIndicator(step, index)).join('')}
                </div>
                
                <div class="workflow-content">
                    <div class="workflow-step-content">
                        ${this.renderCurrentStep()}
                    </div>
                    
                    <div class="workflow-navigation">
                        <button class="btn btn-secondary workflow-prev" 
                                ${this.currentStep === 0 ? 'disabled' : ''}>
                            ← Previous
                        </button>
                        <button class="btn btn-primary workflow-next" 
                                ${this.currentStep === this.steps.length - 1 ? 'disabled' : ''}>
                            Next →
                        </button>
                    </div>
                </div>
            </div>
        `;

        this.addWorkflowStyles();
    }

    renderStepIndicator(step, index) {
        const isActive = index === this.currentStep;
        const isCompleted = index < this.currentStep;
        const statusClass = isCompleted ? 'completed' : (isActive ? 'active' : 'pending');

        return `
            <div class="workflow-step ${statusClass}" data-step="${index}">
                <div class="step-indicator">
                    <span class="step-number">${index + 1}</span>
                    ${isCompleted ? '<span class="step-check">✓</span>' : ''}
                </div>
                <div class="step-title">${step.title}</div>
            </div>
        `;
    }

    renderCurrentStep() {
        const currentStepData = this.steps[this.currentStep];
        
        switch (currentStepData.id) {
            case 'parent':
                return this.renderParentSelection();
            case 'job':
                return this.renderJobInput();
            case 'customize':
                return this.renderCustomization();
            case 'generate':
                return this.renderGeneration();
            default:
                return '<p>Unknown step</p>';
        }
    }

    renderParentSelection() {
        return `
            <div class="step-content">
                <h3>Select Parent Template</h3>
                <p>Choose a base template to start with:</p>
                
                <div class="parent-templates">
                    <div class="template-card" data-template="base_resume_v2.html">
                        <h4>📄 Base Resume v2</h4>
                        <p>Modern, clean template with good structure</p>
                        <button class="btn btn-primary select-template">Select</button>
                    </div>
                    
                    <div class="template-card" data-template="base_resume.html">
                        <h4>📄 Base Resume v1</h4>
                        <p>Original template, proven design</p>
                        <button class="btn btn-primary select-template">Select</button>
                    </div>
                </div>
                
                <div class="selected-template" style="display: none;">
                    <p>✅ Selected: <span class="selected-name"></span></p>
                </div>
            </div>
        `;
    }

    renderJobInput() {
        return `
            <div class="step-content">
                <h3>Job Description</h3>
                <p>Provide the job description to optimize your resume:</p>
                
                <div class="job-input-area">
                    <textarea id="job-description-input" 
                              placeholder="Paste the job description here..."
                              rows="10" 
                              style="width: 100%; margin-bottom: 15px;"></textarea>
                    
                    <div class="job-quick-actions">
                        <input type="text" id="linkedin-url" placeholder="LinkedIn job URL (optional)" 
                               style="width: 70%; margin-right: 10px;">
                        <button class="btn btn-secondary" id="fetch-linkedin">Fetch from LinkedIn</button>
                    </div>
                </div>
            </div>
        `;
    }

    renderCustomization() {
        return `
            <div class="step-content">
                <h3>Customize Variant</h3>
                <p>Configure the optimization settings:</p>
                
                <div class="customization-form">
                    <div class="form-group">
                        <label>Variant Name:</label>
                        <input type="text" id="variant-name" placeholder="e.g., senior-engineer-techcorp">
                    </div>
                    
                    <div class="form-group">
                        <label>Focus Type:</label>
                        <select id="focus-type">
                            <option value="">Auto-detect</option>
                            <option value="technical">Technical Focus</option>
                            <option value="leadership">Leadership Focus</option>
                            <option value="backend">Backend Development</option>
                            <option value="frontend">Frontend Development</option>
                            <option value="fullstack">Full Stack</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Job Title:</label>
                        <input type="text" id="job-title" placeholder="e.g., Senior Software Engineer">
                    </div>
                    
                    <div class="form-group">
                        <label>Company Name:</label>
                        <input type="text" id="company-name" placeholder="e.g., TechCorp">
                    </div>
                </div>
            </div>
        `;
    }

    renderGeneration() {
        return `
            <div class="step-content">
                <h3>Generate Variant</h3>
                <p>Ready to create your optimized resume variant!</p>
                
                <div class="generation-summary">
                    <h4>Summary:</h4>
                    <div id="generation-summary-content">
                        <!-- Will be populated with summary -->
                    </div>
                </div>
                
                <div class="generation-actions">
                    <button class="btn btn-primary btn-large" id="start-generation">
                        🚀 Generate Resume Variant
                    </button>
                </div>
                
                <div class="generation-progress" style="display: none;">
                    <p>⏳ Generating your optimized resume...</p>
                    <div class="progress-bar">
                        <div class="progress-fill"></div>
                    </div>
                </div>
            </div>
        `;
    }

    addWorkflowStyles() {
        const styles = `
            <style>
                .workflow-container {
                    max-width: 800px;
                    margin: 0 auto;
                }
                
                .workflow-steps {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 30px;
                    padding: 0 20px;
                }
                
                .workflow-step {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    flex: 1;
                    position: relative;
                }
                
                .workflow-step:not(:last-child)::after {
                    content: '';
                    position: absolute;
                    top: 20px;
                    right: -50%;
                    width: 100%;
                    height: 2px;
                    background: #e0e0e0;
                    z-index: -1;
                }
                
                .workflow-step.completed::after {
                    background: #28a745;
                }
                
                .step-indicator {
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    background: #e0e0e0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-bottom: 10px;
                    position: relative;
                }
                
                .workflow-step.active .step-indicator {
                    background: #667eea;
                    color: white;
                }
                
                .workflow-step.completed .step-indicator {
                    background: #28a745;
                    color: white;
                }
                
                .step-title {
                    font-size: 0.9em;
                    text-align: center;
                    color: #666;
                }
                
                .workflow-step.active .step-title {
                    color: #667eea;
                    font-weight: bold;
                }
                
                .workflow-content {
                    background: #f8f9fa;
                    border-radius: 8px;
                    padding: 30px;
                    min-height: 400px;
                }
                
                .workflow-navigation {
                    display: flex;
                    justify-content: space-between;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e0e0e0;
                }
                
                .template-card {
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 15px;
                    background: white;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .template-card h4 {
                    margin: 0 0 5px 0;
                    color: #333;
                }
                
                .template-card p {
                    margin: 0;
                    color: #666;
                    font-size: 0.9em;
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
                
                .btn-large {
                    padding: 15px 30px;
                    font-size: 16px;
                }
                
                .progress-bar {
                    width: 100%;
                    height: 10px;
                    background: #e0e0e0;
                    border-radius: 5px;
                    overflow: hidden;
                    margin-top: 10px;
                }
                
                .progress-fill {
                    height: 100%;
                    background: #667eea;
                    width: 0%;
                    transition: width 0.3s ease;
                    animation: indeterminate 1.5s infinite linear;
                }
                
                @keyframes indeterminate {
                    0% { margin-left: -100%; }
                    100% { margin-left: 100%; }
                }
            </style>
        `;
        
        if (!document.getElementById('workflow-styles')) {
            const styleEl = document.createElement('div');
            styleEl.id = 'workflow-styles';
            styleEl.innerHTML = styles;
            document.head.appendChild(styleEl);
        }
    }

    nextStep() {
        if (this.currentStep < this.steps.length - 1) {
            this.currentStep++;
            this.renderWorkflow();
        }
    }

    prevStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.renderWorkflow();
        }
    }

    goToStep(stepIndex) {
        if (stepIndex >= 0 && stepIndex < this.steps.length) {
            this.currentStep = stepIndex;
            this.renderWorkflow();
        }
    }

    updateStepState(stepId, isValid) {
        // Update step completion state based on validation
        const stepIndex = this.steps.findIndex(s => s.id === stepId);
        if (stepIndex !== -1) {
            // Could store validation state and update UI accordingly
        }
    }
}

// Initialize when loaded
window.workflowManagerComponent = new WorkflowManagerComponent();
console.log('✅ Workflow Manager component loaded');