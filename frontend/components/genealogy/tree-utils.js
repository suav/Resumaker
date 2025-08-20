/**
 * Tree Utilities - Helper functions for tree operations
 */

class TreeUtilsComponent {
    constructor() {
        this.init();
    }

    init() {
        // Utility functions for tree operations
    }

    // Calculate tree depth
    static calculateDepth(treeData) {
        if (!treeData) return 0;
        
        let maxDepth = 0;
        for (const [filename, nodeData] of Object.entries(treeData)) {
            const generation = nodeData.generation || 0;
            maxDepth = Math.max(maxDepth, generation);
        }
        return maxDepth;
    }

    // Find all children of a node
    static findChildren(treeData, parentFilename) {
        if (!treeData) return [];
        
        const children = [];
        for (const [filename, nodeData] of Object.entries(treeData)) {
            if (nodeData.parents && nodeData.parents.includes(parentFilename)) {
                children.push(filename);
            }
        }
        return children;
    }

    // Find all ancestors of a node
    static findAncestors(treeData, nodeFilename) {
        if (!treeData || !treeData[nodeFilename]) return [];
        
        const ancestors = [];
        const nodeData = treeData[nodeFilename];
        
        if (nodeData.parents) {
            for (const parent of nodeData.parents) {
                ancestors.push(parent);
                // Recursively find ancestors of parents
                const parentAncestors = this.findAncestors(treeData, parent);
                ancestors.push(...parentAncestors);
            }
        }
        
        return [...new Set(ancestors)]; // Remove duplicates
    }

    // Find the root nodes (nodes with no parents)
    static findRoots(treeData) {
        if (!treeData) return [];
        
        const roots = [];
        for (const [filename, nodeData] of Object.entries(treeData)) {
            if (!nodeData.parents || nodeData.parents.length === 0) {
                roots.push(filename);
            }
        }
        return roots;
    }

    // Find all leaf nodes (nodes with no children)
    static findLeaves(treeData) {
        if (!treeData) return [];
        
        const leaves = [];
        for (const [filename] of Object.entries(treeData)) {
            const children = this.findChildren(treeData, filename);
            if (children.length === 0) {
                leaves.push(filename);
            }
        }
        return leaves;
    }

    // Calculate tree statistics
    static getTreeStats(treeData) {
        if (!treeData) {
            return {
                totalNodes: 0,
                maxDepth: 0,
                rootNodes: 0,
                leafNodes: 0,
                hybridNodes: 0
            };
        }

        const totalNodes = Object.keys(treeData).length;
        const maxDepth = this.calculateDepth(treeData);
        const roots = this.findRoots(treeData);
        const leaves = this.findLeaves(treeData);
        
        let hybridNodes = 0;
        for (const [filename, nodeData] of Object.entries(treeData)) {
            if (nodeData.is_hybrid) {
                hybridNodes++;
            }
        }

        return {
            totalNodes,
            maxDepth,
            rootNodes: roots.length,
            leafNodes: leaves.length,
            hybridNodes
        };
    }

    // Format node display name
    static formatNodeName(nodeData, filename) {
        if (nodeData.name && nodeData.name !== filename) {
            return nodeData.name;
        }
        
        // Clean up filename for display
        let displayName = filename
            .replace('.html', '')
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
        
        // Truncate if too long
        if (displayName.length > 30) {
            displayName = displayName.substring(0, 27) + '...';
        }
        
        return displayName;
    }

    // Generate tree layout positions (simple linear layout)
    static generateLayout(treeData) {
        if (!treeData) return {};
        
        const layout = {};
        const roots = this.findRoots(treeData);
        
        let x = 50;
        let y = 50;
        const nodeWidth = 220;
        const nodeHeight = 120;
        const horizontalSpacing = 50;
        const verticalSpacing = 80;
        
        // Simple linear layout by generation
        const nodesByGeneration = {};
        for (const [filename, nodeData] of Object.entries(treeData)) {
            const generation = nodeData.generation || 0;
            if (!nodesByGeneration[generation]) {
                nodesByGeneration[generation] = [];
            }
            nodesByGeneration[generation].push(filename);
        }
        
        // Position nodes by generation
        for (const [generation, nodes] of Object.entries(nodesByGeneration)) {
            const genY = y + (parseInt(generation) * (nodeHeight + verticalSpacing));
            
            nodes.forEach((filename, index) => {
                const nodeX = x + (index * (nodeWidth + horizontalSpacing));
                layout[filename] = {
                    x: nodeX,
                    y: genY,
                    width: nodeWidth,
                    height: nodeHeight
                };
            });
        }
        
        return layout;
    }
}

// Export utilities
window.TreeUtils = TreeUtilsComponent;
console.log('✅ Tree Utils component loaded');