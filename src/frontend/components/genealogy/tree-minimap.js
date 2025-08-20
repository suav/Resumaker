/**
 * Tree Minimap Component - Provides navigation overview for large trees
 */

class TreeMinimapComponent {
    constructor() {
        this.minimap = null;
        this.viewport = null;
        this.init();
    }

    init() {
        this.bindEvents();
    }

    bindEvents() {
        // Listen for genealogy tab initialization
        document.addEventListener('tab:genealogy:init', () => {
            this.setupMinimap();
        });

        // Handle minimap interactions
        document.addEventListener('click', (e) => {
            if (e.target.matches('.minimap-toggle')) {
                this.toggleMinimap();
            }
        });
    }

    setupMinimap() {
        // Add minimap to the genealogy content if it doesn't exist
        const genealogyContent = document.getElementById('genealogy-content');
        if (!genealogyContent) return;

        // Check if minimap already exists
        if (document.querySelector('.tree-minimap-container')) return;

        const minimapHTML = `
            <div class="tree-minimap-container" style="display: none;">
                <div class="minimap-header">
                    <h5>Tree Overview</h5>
                    <button class="minimap-close">×</button>
                </div>
                <div class="minimap-canvas">
                    <div class="minimap-viewport"></div>
                </div>
            </div>
        `;

        genealogyContent.insertAdjacentHTML('beforeend', minimapHTML);
        this.addMinimapStyles();
    }

    toggleMinimap() {
        const minimap = document.querySelector('.tree-minimap-container');
        if (minimap) {
            const isVisible = minimap.style.display !== 'none';
            minimap.style.display = isVisible ? 'none' : 'block';
            
            if (!isVisible) {
                this.updateMinimap();
            }
        }
    }

    updateMinimap() {
        // Simple minimap update - could be enhanced with actual tree structure
        const viewport = document.querySelector('.minimap-viewport');
        const canvas = document.querySelector('.minimap-canvas');
        
        if (viewport && canvas) {
            // Basic viewport representation
            viewport.style.width = '30%';
            viewport.style.height = '40%';
            viewport.style.left = '10px';
            viewport.style.top = '10px';
        }
    }

    addMinimapStyles() {
        const styles = `
            <style>
                .tree-minimap-container {
                    position: fixed;
                    top: 100px;
                    right: 20px;
                    width: 200px;
                    height: 150px;
                    background: white;
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    z-index: 1000;
                }

                .minimap-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 8px 12px;
                    background: #f8f9fa;
                    border-bottom: 1px solid #ddd;
                    border-radius: 6px 6px 0 0;
                }

                .minimap-header h5 {
                    margin: 0;
                    font-size: 12px;
                    color: #666;
                }

                .minimap-close {
                    background: none;
                    border: none;
                    font-size: 16px;
                    cursor: pointer;
                    color: #999;
                    padding: 0;
                    width: 20px;
                    height: 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }

                .minimap-close:hover {
                    color: #666;
                }

                .minimap-canvas {
                    position: relative;
                    width: 100%;
                    height: calc(100% - 40px);
                    background: #f8f9fa;
                    overflow: hidden;
                }

                .minimap-viewport {
                    position: absolute;
                    border: 2px solid #667eea;
                    background: rgba(102, 126, 234, 0.1);
                    cursor: move;
                }
            </style>
        `;
        
        if (!document.getElementById('tree-minimap-styles')) {
            const styleEl = document.createElement('div');
            styleEl.id = 'tree-minimap-styles';
            styleEl.innerHTML = styles;
            document.head.appendChild(styleEl);
        }
    }
}

// Initialize when loaded
window.treeMinimapComponent = new TreeMinimapComponent();
console.log('✅ Tree Minimap component loaded');