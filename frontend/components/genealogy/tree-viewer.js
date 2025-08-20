/**
 * Tree Viewer Component - Handles genealogy tree visualization
 */

class TreeViewerComponent {
    constructor() {
        this.treeData = null;
        this.selectedNode = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.subscribeToState();
    }

    bindEvents() {
        // Listen for genealogy tab initialization
        document.addEventListener('tab:genealogy:init', () => {
            this.loadGenealogyTree();
        });

        // Refresh button
        document.addEventListener('click', (e) => {
            if (e.target.matches('.refresh-tree-btn')) {
                this.loadGenealogyTree();
            }
        });

        // Node selection
        document.addEventListener('click', (e) => {
            if (e.target.matches('.tree-node')) {
                const nodeId = e.target.dataset.nodeId;
                this.selectNode(nodeId);
            }
        });
    }

    subscribeToState() {
        // Listen for state changes
        stateManager.subscribe('loading', (loading) => {
            this.updateLoadingState(loading);
        });
    }

    async loadGenealogyTree() {
        try {
            stateManager.setLoading(true);
            
            // Call the genealogy API
            const response = await apiClient.makeRequest('/genealogy');
            this.treeData = response;
            
            this.renderTree();
            
        } catch (error) {
            console.error('Failed to load genealogy tree:', error);
            this.renderError('Failed to load genealogy tree. This feature requires the variant_manager.py script.');
        } finally {
            stateManager.setLoading(false);
        }
    }

    renderTree() {
        const container = document.getElementById('genealogy-content');
        if (!container) return;

        if (!this.treeData || Object.keys(this.treeData).length === 0) {
            this.renderEmptyState(container);
            return;
        }

        // Use the original workshop tree structure
        container.innerHTML = `
            <div class="tree-container">
                <div class="tree-minimap" id="tree-minimap">
                    <div class="minimap-header">
                        <h4>Genealogy Overview</h4>
                        <div class="minimap-controls">
                            <button class="minimap-btn" id="focus-recent">📍 Recent</button>
                            <button class="minimap-btn" id="reset-tree">🏠 Reset</button>
                            <button class="btn btn-secondary refresh-tree-btn" style="margin-left: 10px;">🔄</button>
                        </div>
                    </div>
                    <div class="minimap-content">
                        <div class="minimap-viewport" id="minimap-viewport"></div>
                        <svg class="minimap-svg" id="minimap-svg"></svg>
                    </div>
                </div>
                <div class="tree-main-view" id="tree-main">
                    <div class="tree-canvas" id="tree-canvas"></div>
                </div>
            </div>
        `;

        this.addOriginalTreeStyles();
        this.renderOriginalTree();
    }

    renderTreeNodes() {
        if (!this.treeData) return '';

        // Simple tree layout - could be enhanced with D3.js for complex visualizations
        let nodesHTML = '';
        
        // Process each node in the tree data
        for (const [filename, nodeData] of Object.entries(this.treeData)) {
            const generation = nodeData.generation || 0;
            const isHybrid = nodeData.is_hybrid || false;
            const nodeClass = this.getNodeClass(generation, isHybrid);
            
            nodesHTML += `
                <div class="tree-node ${nodeClass}" data-node-id="${filename}">
                    <div class="node-header">
                        <span class="node-icon">${this.getNodeIcon(generation, isHybrid)}</span>
                        <span class="node-name">${nodeData.name || filename}</span>
                    </div>
                    <div class="node-details">
                        <small>Gen ${generation} | ${nodeData.type || 'Unknown'}</small>
                    </div>
                    ${nodeData.parents && nodeData.parents.length > 0 ? 
                        `<div class="node-parents">Parents: ${nodeData.parents.join(', ')}</div>` : ''}
                </div>
            `;
        }

        return nodesHTML || '<p>No tree structure found</p>';
    }

    getNodeClass(generation, isHybrid) {
        if (isHybrid) return 'node-hybrid';
        if (generation === 0) return 'node-base';
        if (generation === 1) return 'node-gen1';
        return 'node-gen2plus';
    }

    getNodeIcon(generation, isHybrid) {
        if (isHybrid) return '🧬';
        if (generation === 0) return '🟢';
        if (generation === 1) return '🔵';
        return '🟡';
    }

    renderEmptyState(container) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>No Genealogy Data</h3>
                <p>No variant genealogy information found.</p>
                <p>Create some variants first, then return here to see their relationships.</p>
                <button class="btn btn-primary" data-tab="workflow">Create Variants</button>
            </div>
        `;
    }

    renderError(message) {
        const container = document.getElementById('genealogy-content');
        if (!container) return;

        container.innerHTML = `
            <div class="error-state">
                <h3>⚠️ Genealogy Tree Error</h3>
                <p>${message}</p>
                <div class="error-actions">
                    <button class="btn btn-secondary refresh-tree-btn">🔄 Try Again</button>
                    <button class="btn btn-primary" data-tab="variants">View Variants List</button>
                </div>
            </div>
        `;
    }

    selectNode(nodeId) {
        // Remove previous selection
        document.querySelectorAll('.tree-node').forEach(node => {
            node.classList.remove('selected');
        });

        // Add selection to clicked node
        const node = document.querySelector(`[data-node-id="${nodeId}"]`);
        if (node) {
            node.classList.add('selected');
            this.selectedNode = nodeId;
        }
    }

    updateLoadingState(loading) {
        const container = document.getElementById('genealogy-content');
        if (container && loading) {
            container.innerHTML = `
                <div class="loading-state">
                    <p>📊 Loading genealogy tree...</p>
                    <div class="spinner"></div>
                </div>
            `;
        }
    }

    renderOriginalTree() {
        const treeCanvas = document.getElementById('tree-canvas');
        const minimap = document.getElementById('tree-minimap');
        const minimapSvg = document.getElementById('minimap-svg');
        
        if (!treeCanvas || !this.treeData) return;

        // Build node hierarchy exactly like original workshop
        const nodes = [];
        const nodeMap = {};
        const generations = {};
        
        // Process all variants into node data
        Object.keys(this.treeData).forEach(key => {
            const data = this.treeData[key];
            const node = {
                key: key,
                name: data.info ? data.info.name : (data.name || key),
                generation: data.info ? data.info.generation : (data.generation || 0),
                type: data.info ? data.info.type : (data.type || 'Unknown'),
                description: data.info ? data.info.description : (data.description || ''),
                is_hybrid: data.info ? data.info.is_hybrid : (data.is_hybrid || false),
                parents: data.info ? (data.info.parents || []) : (data.parents || []),
                children: data.children || [],
                job_title: data.info ? (data.info.job_title || '') : (data.job_title || ''),
                job_company: data.info ? (data.info.job_company || '') : (data.job_company || ''),
                created: data.info ? (data.info.created || '') : (data.created || ''),
                x: 0,
                y: 0
            };
            nodes.push(node);
            nodeMap[key] = node;
            
            // Group by generation
            if (!generations[node.generation]) {
                generations[node.generation] = [];
            }
            generations[node.generation].push(node);
        });

        // Calculate positions using compact card dimensions
        const cardWidth = 200;
        const cardHeight = 85;
        const verticalGap = 100;
        const horizontalGap = 15;
        const childIndent = 25;

        const rootNodes = nodes.filter(node => !node.parents || node.parents.length === 0);
        const positionedNodes = new Set();
        let currentY = 20;
        let maxX = 0;

        // Position nodes hierarchically with staggered layout for large generations
        const positionNodeAndChildren = (node, x, y, parentWidth = 0) => {
            if (positionedNodes.has(node.key)) return { width: 0, height: 0 };
            
            node.x = x;
            node.y = y;
            positionedNodes.add(node.key);
            
            const children = nodes.filter(child => 
                child.parents && child.parents.includes(node.key) && !positionedNodes.has(child.key)
            ).sort((a, b) => {
                const aTime = a.created ? new Date(a.created).getTime() : 0;
                const bTime = b.created ? new Date(b.created).getTime() : 0;
                return bTime - aTime;
            });
            
            if (children.length === 0) {
                maxX = Math.max(maxX, x + cardWidth);
                return { width: cardWidth, height: cardHeight };
            }
            
            // Stagger large generations (more than 4 children)
            const maxPerRow = 4;
            const shouldStagger = children.length > maxPerRow;
            
            let childX = x + childIndent;
            let childY = y + verticalGap;
            let totalChildWidth = 0;
            let maxChildHeight = 0;
            
            if (shouldStagger) {
                // Staggered layout: arrange in multiple rows
                const rows = Math.ceil(children.length / maxPerRow);
                const staggerOffset = 40; // Horizontal offset for each row
                
                children.forEach((child, i) => {
                    const row = Math.floor(i / maxPerRow);
                    const col = i % maxPerRow;
                    
                    const rowX = childX + (row * staggerOffset) + (col * (cardWidth + horizontalGap));
                    const rowY = childY + (row * (cardHeight + 20)); // Small vertical offset per row
                    
                    const childDimensions = positionNodeAndChildren(child, rowX, rowY, cardWidth);
                    maxChildHeight = Math.max(maxChildHeight, childDimensions.height + (row * (cardHeight + 20)));
                });
                
                // Calculate total width for staggered layout
                const lastRowItems = children.length % maxPerRow || maxPerRow;
                const lastRow = rows - 1;
                totalChildWidth = (lastRow * staggerOffset) + (lastRowItems * cardWidth) + ((lastRowItems - 1) * horizontalGap);
            } else {
                // Normal horizontal layout for small generations
                children.forEach((child, i) => {
                    const childDimensions = positionNodeAndChildren(child, childX, childY, cardWidth);
                    childX += childDimensions.width + horizontalGap;
                    totalChildWidth += childDimensions.width + (i < children.length - 1 ? horizontalGap : 0);
                    maxChildHeight = Math.max(maxChildHeight, childDimensions.height);
                });
            }
            
            if (totalChildWidth > cardWidth) {
                const centerOffset = (totalChildWidth - cardWidth) / 2;
                node.x = x + centerOffset;
                maxX = Math.max(maxX, x + totalChildWidth);
            } else {
                maxX = Math.max(maxX, x + cardWidth);
            }
            
            return { 
                width: Math.max(cardWidth, totalChildWidth), 
                height: cardHeight + verticalGap + maxChildHeight 
            };
        };

        // Position root nodes
        let rootX = 20;
        rootNodes.forEach(rootNode => {
            const treeDimensions = positionNodeAndChildren(rootNode, rootX, currentY);
            rootX += treeDimensions.width + horizontalGap * 2;
        });

        // Handle orphaned nodes
        const orphanedNodes = nodes.filter(node => !positionedNodes.has(node.key));
        orphanedNodes.forEach((node, i) => {
            node.x = rootX + i * (cardWidth + horizontalGap);
            node.y = currentY;
            positionedNodes.add(node.key);
        });

        // Calculate canvas size
        const canvasWidth = maxX + 40;
        const maxY = Math.max(...nodes.map(n => n.y));
        const canvasHeight = maxY + cardHeight + 40;

        treeCanvas.style.width = `${canvasWidth}px`;
        treeCanvas.style.height = `${canvasHeight}px`;
        treeCanvas.style.position = 'relative';

        // Create connections and cards
        const connectionsHtml = this.createConnectionLines(nodes, nodeMap, cardWidth, cardHeight);
        const cardsHtml = nodes.map(node => this.createVariantCard(node, cardWidth, cardHeight)).join('');

        treeCanvas.innerHTML = connectionsHtml + cardsHtml;

        // Create minimap
        this.createMinimap(nodes, canvasWidth, canvasHeight, minimapSvg, cardWidth, cardHeight);

        // Initialize navigation
        this.initializeTreeNavigation(treeCanvas, minimap);

        // Initialize minimap viewport
        this.initializeMinimapViewport(canvasWidth, canvasHeight);
    }

    createVariantCard(node, cardWidth, cardHeight) {
        const isRecent = this.isRecentlyCreated(node.created);
        const hybridBadge = node.is_hybrid ? '<span class="tree-badge hybrid">🧬 Hybrid</span>' : '';
        const newBadge = isRecent ? '<span class="tree-badge new">NEW</span>' : '';
        const generationBadge = `<span class="tree-badge generation">Gen ${node.generation}</span>`;
        
        const jobInfo = (node.job_title || node.job_company) ? 
            `<div class="tree-card-job">🎯 ${node.job_title} ${node.job_company ? `@ ${node.job_company}` : ''}</div>` : '';
        
        const parentInfo = node.parents.length > 0 ? 
            `<div class="tree-card-parent">📁 Child of: ${node.parents.map(p => p.replace('.html', '')).join(', ')}</div>` : '';
        
        return `
            <div class="tree-card ${isRecent ? 'recent' : ''}" 
                 style="left: ${node.x}px; top: ${node.y}px; width: ${cardWidth}px; height: ${cardHeight}px;"
                 data-key="${node.key}">
                <div class="tree-card-header">
                    <div class="tree-card-title">${node.name}</div>
                    <div class="tree-card-badges">
                        ${newBadge}${hybridBadge}${generationBadge}
                    </div>
                </div>
                <div class="tree-card-content">
                    <div class="tree-card-desc">${node.description}</div>
                    ${jobInfo}
                    ${parentInfo}
                </div>
                <div class="tree-card-actions">
                    <button onclick="window.variantsDashboardComponent?.showPreviewModal('${node.key}')" class="tree-btn" title="Preview">👁️</button>
                    <button onclick="window.treeViewerComponent?.showBranchModal('${node.key}')" class="tree-btn branch" title="Branch/Clone">🌿</button>
                    <button onclick="window.open('/agent_workspace/output/${node.key.replace('.html', '.pdf')}', '_blank')" class="tree-btn" title="Download PDF">📄</button>
                    <button onclick="if(window.variantsDashboardComponent) window.variantsDashboardComponent.deleteVariant('${node.key}')" class="tree-btn delete" title="Delete">🗑️</button>
                </div>
            </div>
        `;
    }

    createConnectionLines(nodes, nodeMap, cardWidth, cardHeight) {
        const lines = [];
        const cardCenterX = cardWidth / 2;
        const cardCenterY = cardHeight / 2;
        
        nodes.forEach(node => {
            if (node.parents && node.parents.length > 0) {
                node.parents.forEach(parentKey => {
                    const parent = nodeMap[parentKey];
                    if (parent) {
                        const x1 = parent.x + cardCenterX;
                        const y1 = parent.y + cardHeight;
                        const x2 = node.x + cardCenterX;
                        const y2 = node.y;
                        
                        lines.push(`
                            <line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" 
                                  class="tree-connection ${node.is_hybrid ? 'hybrid' : ''}" 
                                  stroke-width="2" marker-end="url(#arrowhead)"/>
                        `);
                    }
                });
            }
        });
        
        const maxX = Math.max(...nodes.map(n => n.x + cardWidth));
        const maxY = Math.max(...nodes.map(n => n.y + cardHeight));
        
        return `
            <svg class="tree-connections" style="position: absolute; top: 0; left: 0; width: ${maxX}px; height: ${maxY}px; pointer-events: none; z-index: 1;">
                <defs>
                    <marker id="arrowhead" markerWidth="10" markerHeight="7" 
                            refX="10" refY="3.5" orient="auto">
                        <polygon points="0 0, 10 3.5, 0 7" fill="#666" />
                    </marker>
                </defs>
                ${lines.join('')}
            </svg>
        `;
    }

    createMinimap(nodes, canvasWidth, canvasHeight, minimapSvg, cardWidth, cardHeight) {
        // Set viewBox to maintain aspect ratio
        minimapSvg.setAttribute('viewBox', `0 0 ${canvasWidth} ${canvasHeight}`);
        minimapSvg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
        minimapSvg.style.width = '100%';
        minimapSvg.style.height = '100%';
        
        // Create connection lines for minimap
        const connectionLines = [];
        nodes.forEach(node => {
            if (node.parents && node.parents.length > 0) {
                node.parents.forEach(parentKey => {
                    const parent = nodes.find(n => n.key === parentKey);
                    if (parent) {
                        connectionLines.push(`
                            <line x1="${parent.x + cardWidth/2}" y1="${parent.y + cardHeight}" 
                                  x2="${node.x + cardWidth/2}" y2="${node.y}" 
                                  stroke="#cbd5e0" stroke-width="1"/>
                        `);
                    }
                });
            }
        });
        
        // Create minimap nodes
        const minimapNodes = nodes.map(node => {
            const isRecent = this.isRecentlyCreated(node.created);
            let color = '#48bb78';
            if (node.generation === 0) color = '#667eea';
            if (node.is_hybrid) color = '#f56565';
            if (isRecent) color = '#38a169';
            
            const strokeColor = isRecent ? '#2f855a' : 'white';
            const strokeWidth = isRecent ? '2' : '1';
            
            return `
                <rect x="${node.x}" y="${node.y}" 
                      width="${cardWidth}" height="${cardHeight}" 
                      fill="${color}" 
                      stroke="${strokeColor}" 
                      stroke-width="${strokeWidth}"
                      rx="3" 
                      data-key="${node.key}"
                      style="cursor: pointer;">
                    <title>${node.name}</title>
                </rect>
                <text x="${node.x + cardWidth/2}" y="${node.y + cardHeight/2 + 2}" 
                      text-anchor="middle" 
                      fill="white" 
                      font-size="10" 
                      font-weight="bold"
                      pointer-events="none">
                    ${node.name.length > 15 ? node.name.substring(0, 12) + '...' : node.name}
                </text>
            `;
        }).join('');
        
        minimapSvg.innerHTML = connectionLines.join('') + minimapNodes;
        
        // Add click handlers
        minimapSvg.querySelectorAll('rect[data-key]').forEach(rect => {
            rect.addEventListener('click', (e) => {
                const nodeKey = e.target.getAttribute('data-key');
                this.focusOnNode(nodeKey);
            });
        });
    }

    initializeTreeNavigation(treeCanvas, minimap) {
        const treeMain = document.getElementById('tree-main');
        let isDragging = false;
        let lastX, lastY;

        treeMain.addEventListener('mousedown', (e) => {
            if (e.target.closest('.tree-card') || e.target.closest('.tree-btn')) return;
            isDragging = true;
            lastX = e.clientX;
            lastY = e.clientY;
            treeMain.style.cursor = 'grabbing';
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            
            const deltaX = e.clientX - lastX;
            const deltaY = e.clientY - lastY;
            
            treeMain.scrollLeft -= deltaX;
            treeMain.scrollTop -= deltaY;
            
            lastX = e.clientX;
            lastY = e.clientY;
            
            // Update minimap viewport
            this.updateMinimapViewport();
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
            treeMain.style.cursor = 'grab';
        });

        // Update viewport on scroll
        treeMain.addEventListener('scroll', () => {
            this.updateMinimapViewport();
        });

        // Bind buttons
        document.getElementById('focus-recent')?.addEventListener('click', () => this.focusOnRecent());
        document.getElementById('reset-tree')?.addEventListener('click', () => this.resetTreeView());
    }

    focusOnNode(nodeKey) {
        const card = document.querySelector(`[data-key="${nodeKey}"]`);
        const treeMain = document.getElementById('tree-main');
        
        if (card && treeMain) {
            const cardRect = card.getBoundingClientRect();
            const containerRect = treeMain.getBoundingClientRect();
            
            treeMain.scrollTo({
                left: card.offsetLeft - (treeMain.clientWidth / 2) + (card.offsetWidth / 2),
                top: card.offsetTop - (treeMain.clientHeight / 2) + (card.offsetHeight / 2),
                behavior: 'smooth'
            });
        }
    }

    focusOnRecent() {
        const recentCard = document.querySelector('.tree-card.recent');
        if (recentCard) {
            const nodeKey = recentCard.getAttribute('data-key');
            this.focusOnNode(nodeKey);
        }
    }

    resetTreeView() {
        const treeMain = document.getElementById('tree-main');
        if (treeMain) {
            treeMain.scrollTo({
                left: 0,
                top: 0,
                behavior: 'smooth'
            });
        }
    }

    isRecentlyCreated(created) {
        if (!created) return false;
        const createdDate = new Date(created);
        const now = new Date();
        const timeDiff = now - createdDate;
        return timeDiff < (7 * 24 * 60 * 60 * 1000); // 7 days
    }

    showBranchModal(parentFilename) {
        // Create branch modal overlay
        const modal = document.createElement('div');
        modal.className = 'branch-modal-overlay';
        modal.innerHTML = `
            <div class="branch-modal">
                <div class="branch-modal-header">
                    <h3>🌿 Create Branch from ${parentFilename.replace('.html', '')}</h3>
                    <button class="branch-modal-close">&times;</button>
                </div>
                <div class="branch-modal-body">
                    <form id="branch-form">
                        <div class="form-group">
                            <label for="branch-name">Branch Name:</label>
                            <input type="text" id="branch-name" name="branchName" 
                                   placeholder="e.g., frontend-focused, senior-dev-version" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="job-title">Job Title (optional):</label>
                            <input type="text" id="job-title" name="jobTitle" 
                                   placeholder="e.g., Senior Frontend Developer">
                        </div>
                        
                        <div class="form-group">
                            <label for="company-name">Company (optional):</label>
                            <input type="text" id="company-name" name="companyName" 
                                   placeholder="e.g., TechCorp Inc">
                        </div>
                        
                        <div class="form-group">
                            <label for="focus-type">Focus Area:</label>
                            <select id="focus-type" name="focusType">
                                <option value="">Select focus...</option>
                                <option value="frontend-focused">Frontend Development</option>
                                <option value="backend-focused">Backend Development</option>
                                <option value="fullstack-balanced">Full Stack Balanced</option>
                                <option value="leadership-focused">Leadership & Management</option>
                                <option value="technical-architect">Technical Architecture</option>
                                <option value="devops-focused">DevOps & Infrastructure</option>
                                <option value="data-focused">Data Science & Analytics</option>
                                <option value="mobile-focused">Mobile Development</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>Job Description:</label>
                            <div class="job-input-options">
                                <div class="saved-jobs-mini-section">
                                    <label for="saved-jobs-select">📋 Use Saved Job:</label>
                                    <select id="saved-jobs-select" name="savedJobSelect">
                                        <option value="">Select a saved job...</option>
                                    </select>
                                </div>
                                <div class="or-divider">OR</div>
                                <div class="manual-job-section">
                                    <label for="job-description">✏️ Enter manually:</label>
                                    <textarea id="job-description" name="jobDescription" rows="3"
                                              placeholder="Paste job description to tailor the resume..."
                                              class="linkedin-target-textarea"></textarea>
                                </div>
                                <div class="linkedin-mini-section linkedin-fetch-container">
                                    <label>🔗 Fetch from LinkedIn:</label>
                                    <div class="linkedin-input-group">
                                        <input type="url" id="branch-linkedin-url" class="linkedin-url-input" 
                                               placeholder="https://linkedin.com/jobs/view/..." />
                                        <button type="button" class="linkedin-fetch-btn btn btn-sm btn-secondary">Fetch</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
                <div class="branch-modal-footer">
                    <button type="button" class="btn btn-secondary branch-modal-close">Cancel</button>
                    <button type="button" class="btn btn-primary" id="create-branch-btn">🌿 Create Branch</button>
                </div>
            </div>
        `;

        // Add to document
        document.body.appendChild(modal);

        // Add event listeners
        modal.addEventListener('click', (e) => {
            if (e.target.classList.contains('branch-modal-overlay') || 
                e.target.classList.contains('branch-modal-close')) {
                this.closeBranchModal(modal);
            }
        });

        // Create branch button
        document.getElementById('create-branch-btn').addEventListener('click', () => {
            this.createBranch(parentFilename, modal);
        });

        // Add escape key listener
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                this.closeBranchModal(modal);
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);

        // Store escape handler for cleanup
        modal._escapeHandler = escapeHandler;

        // Load saved jobs for the dropdown
        this.loadSavedJobsForBranch();

        // Handle saved job selection
        document.getElementById('saved-jobs-select').addEventListener('change', (e) => {
            this.handleSavedJobSelection(e.target.value);
        });

        // Focus the branch name input
        setTimeout(() => {
            document.getElementById('branch-name').focus();
        }, 100);

        // Set up LinkedIn functionality for this modal
        this.setupBranchLinkedInFunctionality();
    }

    setupBranchLinkedInFunctionality() {
        // Add explicit LinkedIn functionality to the branch modal
        const linkedInBtn = document.querySelector('.branch-modal .linkedin-fetch-btn');
        const linkedInUrl = document.querySelector('#branch-linkedin-url');
        const jobDescription = document.querySelector('#job-description');
        const jobTitle = document.querySelector('#job-title');
        const companyName = document.querySelector('#company-name');

        if (linkedInBtn && linkedInUrl) {
            console.log('🔗 Setting up branch modal LinkedIn functionality');
            
            linkedInBtn.addEventListener('click', async (e) => {
                console.log('🔗 Branch modal LinkedIn button clicked');
                
                const url = linkedInUrl.value.trim();
                if (!url) {
                    alert('Please enter a LinkedIn job URL');
                    return;
                }

                // Show loading state
                linkedInBtn.disabled = true;
                linkedInBtn.textContent = '⏳ Fetching...';

                try {
                    console.log('🔗 Fetching LinkedIn data for branch modal:', url);
                    
                    // Use the global API client
                    const result = await window.apiClient.fetchLinkedInJob(url);
                    console.log('🔗 Branch modal LinkedIn result:', result);

                    if (result.success) {
                        // Populate fields
                        if (jobDescription && result.content) {
                            jobDescription.value = result.content;
                        }
                        if (jobTitle && result.title) {
                            jobTitle.value = result.title;
                        }
                        if (companyName && result.company) {
                            companyName.value = result.company;
                        }

                        // Clear URL input
                        linkedInUrl.value = '';

                        // Show success
                        this.showBranchLinkedInSuccess();
                    } else {
                        alert('Failed to fetch LinkedIn data: ' + (result.message || result.error));
                    }
                } catch (error) {
                    console.error('🔗 Branch modal LinkedIn error:', error);
                    alert('Error fetching LinkedIn data: ' + error.message);
                } finally {
                    // Restore button
                    linkedInBtn.disabled = false;
                    linkedInBtn.textContent = 'Fetch';
                }
            });
        } else {
            console.warn('🔗 LinkedIn elements not found in branch modal');
        }
    }

    showBranchLinkedInSuccess() {
        // Simple success notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            border-radius: 4px;
            padding: 12px 16px;
            z-index: 1100;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        `;
        notification.textContent = '✅ LinkedIn job data fetched successfully!';
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }

    closeBranchModal(modal) {
        if (modal._escapeHandler) {
            document.removeEventListener('keydown', modal._escapeHandler);
        }
        modal.remove();
    }

    async createBranch(parentFilename, modal) {
        const form = document.getElementById('branch-form');
        const formData = new FormData(form);
        
        const branchName = formData.get('branchName');
        if (!branchName.trim()) {
            alert('Please enter a branch name');
            return;
        }

        // Disable the create button to prevent double submission
        const createBtn = document.getElementById('create-branch-btn');
        createBtn.disabled = true;
        createBtn.textContent = '🔄 Creating...';

        try {
            const variantData = {
                parent: parentFilename,
                variant_name: branchName.trim(),
                job_title: formData.get('jobTitle') || '',
                company_name: formData.get('companyName') || '',
                focus_type: formData.get('focusType') || 'balanced',
                job_description: formData.get('jobDescription') || ''
            };

            console.log('Creating branch with data:', variantData);

            const response = await apiClient.createVariant(variantData);
            
            if (response.success) {
                console.log('Branch created successfully:', response);
                
                // Close modal
                this.closeBranchModal(modal);
                
                // Show success message
                this.showBranchSuccess(branchName, response.job_id);
                
                // Reload tree to show new branch
                setTimeout(() => {
                    this.loadGenealogyTree();
                }, 2000);
            } else {
                throw new Error(response.error || 'Branch creation failed');
            }

        } catch (error) {
            console.error('Failed to create branch:', error);
            alert(`Failed to create branch: ${error.message}`);
        } finally {
            // Re-enable button
            createBtn.disabled = false;
            createBtn.textContent = '🌿 Create Branch';
        }
    }

    async loadSavedJobsForBranch() {
        try {
            const savedJobs = await apiClient.getJobDescriptions();
            const select = document.getElementById('saved-jobs-select');
            
            if (!select) return;
            
            // Clear existing options except the first one
            select.innerHTML = '<option value="">Select a saved job...</option>';
            
            // Add saved jobs as options
            savedJobs.forEach(job => {
                const option = document.createElement('option');
                option.value = job.filename;
                option.textContent = `${job.title} (${job.company})`;
                if (job.active) {
                    option.textContent += ' [Active]';
                }
                select.appendChild(option);
            });
            
        } catch (error) {
            console.error('Failed to load saved jobs for branch:', error);
        }
    }

    async handleSavedJobSelection(filename) {
        if (!filename) return;
        
        try {
            const savedJobs = await apiClient.getJobDescriptions();
            const selectedJob = savedJobs.find(job => job.filename === filename);
            
            if (selectedJob) {
                // Populate the form fields
                const jobTitleInput = document.getElementById('job-title');
                const companyInput = document.getElementById('company-name');
                const jobDescTextarea = document.getElementById('job-description');
                
                if (jobTitleInput && selectedJob.title && selectedJob.title !== 'Unknown Position') {
                    jobTitleInput.value = selectedJob.title;
                }
                if (companyInput && selectedJob.company && selectedJob.company !== 'Unknown Company') {
                    companyInput.value = selectedJob.company;
                }
                if (jobDescTextarea) {
                    // Get full job content
                    const fullContent = this.getJobContentForBranch(selectedJob);
                    jobDescTextarea.value = fullContent;
                }
            }
            
        } catch (error) {
            console.error('Failed to load selected job:', error);
        }
    }

    getJobContentForBranch(job) {
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

    showBranchSuccess(branchName, jobId) {
        // Create success notification
        const notification = document.createElement('div');
        notification.className = 'branch-success-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">🌿</span>
                <span class="notification-text">Branch "${branchName}" is being created...</span>
                <button class="notification-close">&times;</button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
        
        // Manual close
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
    }

    initializeMinimapViewport(canvasWidth, canvasHeight) {
        const viewport = document.getElementById('minimap-viewport');
        const minimapContent = document.querySelector('.minimap-content');
        
        if (!viewport || !minimapContent) return;

        this.canvasWidth = canvasWidth;
        this.canvasHeight = canvasHeight;
        
        // Initial viewport setup
        this.updateMinimapViewport();
        
        // Make viewport draggable
        let isViewportDragging = false;
        let startX, startY;
        
        viewport.addEventListener('mousedown', (e) => {
            isViewportDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            e.preventDefault();
            e.stopPropagation();
        });
        
        document.addEventListener('mousemove', (e) => {
            if (!isViewportDragging) return;
            
            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;
            
            const treeMain = document.getElementById('tree-main');
            const minimapRect = minimapContent.getBoundingClientRect();
            const scaleX = this.canvasWidth / minimapRect.width;
            const scaleY = this.canvasHeight / minimapRect.height;
            
            treeMain.scrollLeft += deltaX * scaleX;
            treeMain.scrollTop += deltaY * scaleY;
            
            startX = e.clientX;
            startY = e.clientY;
            
            this.updateMinimapViewport();
        });
        
        document.addEventListener('mouseup', () => {
            isViewportDragging = false;
        });
        
        // Click to navigate on minimap
        minimapContent.addEventListener('click', (e) => {
            if (e.target === viewport) return;
            
            const rect = minimapContent.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const clickY = e.clientY - rect.top;
            
            const scaleX = this.canvasWidth / rect.width;
            const scaleY = this.canvasHeight / rect.height;
            
            const treeMain = document.getElementById('tree-main');
            treeMain.scrollTo({
                left: (clickX * scaleX) - (treeMain.clientWidth / 2),
                top: (clickY * scaleY) - (treeMain.clientHeight / 2),
                behavior: 'smooth'
            });
        });
    }

    updateMinimapViewport() {
        const viewport = document.getElementById('minimap-viewport');
        const minimapContent = document.querySelector('.minimap-content');
        const treeMain = document.getElementById('tree-main');
        
        if (!viewport || !minimapContent || !treeMain || !this.canvasWidth) return;
        
        const minimapRect = minimapContent.getBoundingClientRect();
        const scaleX = minimapRect.width / this.canvasWidth;
        const scaleY = minimapRect.height / this.canvasHeight;
        
        const viewportWidth = treeMain.clientWidth * scaleX;
        const viewportHeight = treeMain.clientHeight * scaleY;
        const viewportLeft = treeMain.scrollLeft * scaleX;
        const viewportTop = treeMain.scrollTop * scaleY;
        
        viewport.style.width = `${viewportWidth}px`;
        viewport.style.height = `${viewportHeight}px`;
        viewport.style.left = `${viewportLeft}px`;
        viewport.style.top = `${viewportTop}px`;
        viewport.style.display = 'block';
    }

    addOriginalTreeStyles() {
        const styles = `
            <style id="original-tree-styles">
                #genealogy-content {
                    width: 100%;
                    max-width: 100%;
                    overflow: hidden;
                    box-sizing: border-box;
                }
                
                .tree-container {
                    display: flex;
                    height: 500px;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    overflow: hidden;
                    background: #f8f9fa;
                    width: 100%;
                    max-width: 100%;
                    box-sizing: border-box;
                }
                
                .tree-minimap {
                    width: 350px;
                    background: white;
                    border-right: 1px solid #e2e8f0;
                    position: relative;
                    overflow: hidden;
                    display: flex;
                    flex-direction: column;
                }
                
                .minimap-header {
                    padding: 12px;
                    border-bottom: 1px solid #e2e8f0;
                    background: #f8f9fa;
                }
                
                .minimap-header h4 {
                    margin: 0 0 8px 0;
                    font-size: 14px;
                    color: #2d3748;
                }
                
                .minimap-controls {
                    display: flex;
                    gap: 8px;
                    flex-wrap: wrap;
                }
                
                .minimap-btn {
                    background: #4285f4;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 11px;
                    cursor: pointer;
                    transition: background 0.2s ease;
                }
                
                .minimap-btn:hover {
                    background: #3367d6;
                }
                
                .minimap-content {
                    flex: 1;
                    position: relative;
                    overflow: hidden;
                    cursor: crosshair;
                    height: 400px;
                }
                
                .minimap-viewport {
                    position: absolute;
                    border: 3px solid #4285f4;
                    background: rgba(66, 133, 244, 0.15);
                    pointer-events: all;
                    z-index: 10;
                    border-radius: 2px;
                    cursor: move;
                    display: none;
                }
                
                .minimap-viewport:hover {
                    background: rgba(66, 133, 244, 0.25);
                    border-color: #3367d6;
                }
                
                .minimap-svg {
                    display: block;
                    width: 100%;
                    height: 100%;
                    max-height: 400px;
                }
                
                .tree-main-view {
                    flex: 1;
                    overflow: auto;
                    cursor: grab;
                    position: relative;
                    width: 0;
                    min-width: 0;
                }
                
                .tree-canvas {
                    position: relative;
                    min-width: 100%;
                    min-height: 100%;
                }
                
                .tree-card {
                    position: absolute;
                    background: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
                    padding: 8px;
                    transition: all 0.2s ease;
                    z-index: 5;
                }
                
                .tree-card:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
                    border-color: #cbd5e0;
                }
                
                .tree-card.recent {
                    border: 2px solid #48bb78;
                    box-shadow: 0 0 12px rgba(72, 187, 120, 0.15);
                    animation: pulse-new 2s ease-in-out infinite;
                }
                
                @keyframes pulse-new {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.02); }
                }
                
                .tree-card-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    margin-bottom: 6px;
                }
                
                .tree-card-title {
                    font-weight: 600;
                    font-size: 12px;
                    color: #2d3748;
                    line-height: 1.1;
                    flex: 1;
                    margin-right: 6px;
                }
                
                .tree-card-badges {
                    display: flex;
                    gap: 4px;
                    flex-wrap: wrap;
                }
                
                .tree-badge {
                    font-size: 9px;
                    padding: 1px 4px;
                    border-radius: 8px;
                    font-weight: 600;
                    white-space: nowrap;
                }
                
                .tree-badge.new {
                    background: linear-gradient(135deg, #48bb78, #38a169);
                    color: white;
                    animation: glow-new 2s ease-in-out infinite;
                }
                
                @keyframes glow-new {
                    0%, 100% { box-shadow: 0 0 5px rgba(72, 187, 120, 0.5); }
                    50% { box-shadow: 0 0 20px rgba(72, 187, 120, 0.8); }
                }
                
                .tree-badge.hybrid {
                    background: linear-gradient(135deg, #f56565, #ed8936);
                    color: white;
                }
                
                .tree-badge.generation {
                    background: #edf2f7;
                    color: #4a5568;
                }
                
                .tree-card-content {
                    margin-bottom: 6px;
                    font-size: 10px;
                }
                
                .tree-card-desc {
                    color: #4a5568;
                    margin-bottom: 3px;
                    line-height: 1.2;
                    display: none;
                }
                
                .tree-card-job {
                    color: #2b6cb0;
                    font-size: 10px;
                    margin-bottom: 1px;
                }
                
                .tree-card-parent {
                    color: #718096;
                    font-size: 9px;
                }
                
                .tree-card-actions {
                    display: flex;
                    gap: 4px;
                    justify-content: flex-end;
                }
                
                .tree-btn {
                    background: #f7fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 3px;
                    padding: 3px 5px;
                    font-size: 11px;
                    cursor: pointer;
                    transition: all 0.15s ease;
                }
                
                .tree-btn:hover {
                    background: #edf2f7;
                    border-color: #cbd5e0;
                }
                
                .tree-btn.delete:hover {
                    background: #fed7d7;
                    border-color: #f56565;
                    color: #c53030;
                }
                
                .tree-btn.branch:hover {
                    background: #c6f6d5;
                    border-color: #48bb78;
                    color: #276749;
                }
                
                .tree-connections {
                    pointer-events: none;
                }
                
                .tree-connection {
                    stroke: #a0aec0;
                    fill: none;
                }
                
                .tree-connection.hybrid {
                    stroke: #f56565;
                    stroke-dasharray: 5,5;
                }
                
                /* Branch Modal Styles */
                .branch-modal-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.6);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 1000;
                }
                
                .branch-modal {
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
                    max-width: 500px;
                    width: 90%;
                    max-height: 90vh;
                    overflow-y: auto;
                }
                
                .branch-modal-header {
                    padding: 24px 24px 0 24px;
                    border-bottom: 1px solid #e2e8f0;
                }
                
                .branch-modal-header h3 {
                    margin: 0 0 8px 0;
                    color: #2d3748;
                    font-size: 20px;
                    font-weight: 600;
                }
                
                .branch-modal-header p {
                    margin: 0 0 16px 0;
                    color: #718096;
                    font-size: 14px;
                }
                
                .branch-modal-body {
                    padding: 24px;
                }
                
                .form-group {
                    margin-bottom: 20px;
                }
                
                .form-group label {
                    display: block;
                    margin-bottom: 6px;
                    color: #4a5568;
                    font-weight: 500;
                    font-size: 14px;
                }
                
                .form-group input,
                .form-group select,
                .form-group textarea {
                    width: 100%;
                    padding: 10px 12px;
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                    font-size: 14px;
                    color: #2d3748;
                    background: white;
                    box-sizing: border-box;
                    transition: border-color 0.2s ease;
                }
                
                .form-group input:focus,
                .form-group select:focus,
                .form-group textarea:focus {
                    outline: none;
                    border-color: #3182ce;
                    box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
                }
                
                .form-group textarea {
                    resize: vertical;
                    min-height: 80px;
                }
                
                .form-group .required {
                    color: #e53e3e;
                }
                
                .branch-modal-footer {
                    padding: 0 24px 24px 24px;
                    display: flex;
                    gap: 12px;
                    justify-content: flex-end;
                }
                
                .branch-modal-btn {
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: 500;
                    cursor: pointer;
                    border: 1px solid transparent;
                    transition: all 0.2s ease;
                }
                
                .branch-modal-btn.primary {
                    background: #3182ce;
                    color: white;
                    border-color: #3182ce;
                }
                
                .branch-modal-btn.primary:hover:not(:disabled) {
                    background: #2c5282;
                    border-color: #2c5282;
                }
                
                .branch-modal-btn.primary:disabled {
                    background: #a0aec0;
                    border-color: #a0aec0;
                    cursor: not-allowed;
                }
                
                .branch-modal-btn.secondary {
                    background: white;
                    color: #4a5568;
                    border-color: #e2e8f0;
                }
                
                .branch-modal-btn.secondary:hover {
                    background: #f7fafc;
                    border-color: #cbd5e0;
                }
                
                .branch-success-notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: #c6f6d5;
                    border: 1px solid #9ae6b4;
                    border-radius: 8px;
                    padding: 16px;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                    z-index: 1100;
                    max-width: 400px;
                }
                
                .notification-content {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                
                .notification-icon {
                    font-size: 18px;
                }
                
                .notification-text {
                    flex: 1;
                    color: #276749;
                    font-size: 14px;
                    font-weight: 500;
                }
                
                .notification-close {
                    background: none;
                    border: none;
                    color: #276749;
                    font-size: 18px;
                    cursor: pointer;
                    padding: 0;
                    line-height: 1;
                }
                
                .notification-close:hover {
                    color: #22543d;
                }
                
                /* Branch Modal Job Input Styles */
                .job-input-options {
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                    background: #f8f9fa;
                    padding: 12px;
                }

                .saved-jobs-mini-section {
                    margin-bottom: 12px;
                }

                .saved-jobs-mini-section label {
                    display: block;
                    margin-bottom: 4px;
                    font-size: 12px;
                    font-weight: 500;
                    color: #4a5568;
                }

                .saved-jobs-mini-section select {
                    width: 100%;
                    padding: 6px 10px;
                    border: 1px solid #e2e8f0;
                    border-radius: 4px;
                    font-size: 12px;
                    background: white;
                }

                .or-divider {
                    text-align: center;
                    margin: 12px 0;
                    color: #718096;
                    font-size: 11px;
                    font-weight: 500;
                    position: relative;
                }

                .or-divider::before {
                    content: '';
                    position: absolute;
                    top: 50%;
                    left: 0;
                    right: 0;
                    height: 1px;
                    background: #e2e8f0;
                }

                .or-divider {
                    background: #f8f9fa;
                    padding: 0 10px;
                    display: inline-block;
                }

                .manual-job-section {
                    margin-bottom: 12px;
                }

                .manual-job-section label {
                    display: block;
                    margin-bottom: 4px;
                    font-size: 12px;
                    font-weight: 500;
                    color: #4a5568;
                }

                .manual-job-section textarea {
                    width: 100%;
                    padding: 6px 10px;
                    border: 1px solid #e2e8f0;
                    border-radius: 4px;
                    font-size: 12px;
                    resize: vertical;
                    min-height: 60px;
                }

                .linkedin-mini-section {
                    margin-top: 12px;
                }

                .linkedin-mini-section label {
                    display: block;
                    margin-bottom: 4px;
                    font-size: 12px;
                    font-weight: 500;
                    color: #4a5568;
                }

                .linkedin-mini-section .linkedin-input-group {
                    display: flex;
                    gap: 6px;
                }

                .linkedin-mini-section input {
                    flex: 1;
                    padding: 6px 10px;
                    border: 1px solid #e2e8f0;
                    border-radius: 4px;
                    font-size: 12px;
                }

                .linkedin-mini-section .btn {
                    padding: 6px 12px;
                    font-size: 11px;
                }
            </style>
        `;
        
        if (!document.getElementById('original-tree-styles')) {
            document.head.insertAdjacentHTML('beforeend', styles);
        }
    }
}

// Initialize when loaded
window.treeViewerComponent = new TreeViewerComponent();
console.log('✅ Tree Viewer component loaded');
