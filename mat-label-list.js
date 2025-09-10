/**
 * Mat Label List - A simple system to manage materials with labels
 * This demonstrates JavaScript programming with GitHub Copilot
 */

class MatLabelList {
    constructor() {
        this.mats = [];
        this.nextId = 1;
    }

    /**
     * Add a new mat with labels to the list
     * @param {string} name - Name of the mat
     * @param {string} material - Material type (e.g., 'rubber', 'foam', 'fabric')
     * @param {Array<string>} labels - Array of labels for the mat
     * @param {string} color - Color of the mat
     * @param {number} size - Size in square feet
     * @returns {Object} The created mat object
     */
    addMat(name, material, labels = [], color = 'unknown', size = 0) {
        const mat = {
            id: this.nextId++,
            name: name,
            material: material,
            labels: Array.isArray(labels) ? labels : [labels],
            color: color,
            size: size,
            createdAt: new Date().toISOString()
        };
        
        this.mats.push(mat);
        return mat;
    }

    /**
     * Get all mats in the list
     * @returns {Array} Array of all mats
     */
    getAllMats() {
        return [...this.mats];
    }

    /**
     * Find mats by label
     * @param {string} label - Label to search for
     * @returns {Array} Array of mats with the specified label
     */
    findMatsByLabel(label) {
        return this.mats.filter(mat => 
            mat.labels.some(l => l.toLowerCase().includes(label.toLowerCase()))
        );
    }

    /**
     * Find mats by material type
     * @param {string} material - Material type to search for
     * @returns {Array} Array of mats with the specified material
     */
    findMatsByMaterial(material) {
        return this.mats.filter(mat => 
            mat.material.toLowerCase().includes(material.toLowerCase())
        );
    }

    /**
     * Find mat by ID
     * @param {number} id - ID of the mat to find
     * @returns {Object|null} The mat object or null if not found
     */
    findMatById(id) {
        return this.mats.find(mat => mat.id === id) || null;
    }

    /**
     * Update mat labels
     * @param {number} id - ID of the mat to update
     * @param {Array<string>} newLabels - New labels array
     * @returns {boolean} True if updated successfully, false otherwise
     */
    updateMatLabels(id, newLabels) {
        const mat = this.findMatById(id);
        if (mat) {
            mat.labels = Array.isArray(newLabels) ? newLabels : [newLabels];
            return true;
        }
        return false;
    }

    /**
     * Remove a mat from the list
     * @param {number} id - ID of the mat to remove
     * @returns {boolean} True if removed successfully, false otherwise
     */
    removeMat(id) {
        const index = this.mats.findIndex(mat => mat.id === id);
        if (index > -1) {
            this.mats.splice(index, 1);
            return true;
        }
        return false;
    }

    /**
     * Get summary statistics
     * @returns {Object} Statistics about the mat collection
     */
    getStats() {
        const totalMats = this.mats.length;
        const materials = [...new Set(this.mats.map(mat => mat.material))];
        const allLabels = [...new Set(this.mats.flatMap(mat => mat.labels))];
        const totalSize = this.mats.reduce((sum, mat) => sum + mat.size, 0);
        
        return {
            totalMats,
            uniqueMaterials: materials.length,
            materials,
            uniqueLabels: allLabels.length,
            allLabels,
            totalSize
        };
    }

    /**
     * Display all mats in a formatted way
     * @returns {string} Formatted string representation of all mats
     */
    displayMats() {
        if (this.mats.length === 0) {
            return "No mats in the list.";
        }

        let output = "Mat Label List:\n";
        output += "================\n\n";

        this.mats.forEach(mat => {
            output += `ID: ${mat.id}\n`;
            output += `Name: ${mat.name}\n`;
            output += `Material: ${mat.material}\n`;
            output += `Color: ${mat.color}\n`;
            output += `Size: ${mat.size} sq ft\n`;
            output += `Labels: ${mat.labels.join(', ')}\n`;
            output += `Created: ${new Date(mat.createdAt).toLocaleDateString()}\n`;
            output += "---\n";
        });

        return output;
    }
}

// Example usage and demonstration
function demonstrateMatLabelList() {
    console.log("=== Mat Label List Demo ===\n");
    
    const matList = new MatLabelList();
    
    // Add some sample mats
    matList.addMat("Yoga Mat Pro", "rubber", ["exercise", "yoga", "fitness"], "purple", 6);
    matList.addMat("Kitchen Runner", "fabric", ["kitchen", "anti-slip", "washable"], "blue", 12);
    matList.addMat("Entrance Mat", "coir", ["outdoor", "entrance", "weather-resistant"], "brown", 4);
    matList.addMat("Meditation Cushion", "foam", ["meditation", "comfortable", "portable"], "green", 2);
    matList.addMat("Exercise Mat", "rubber", ["exercise", "gym", "non-slip"], "black", 8);

    console.log("All mats:");
    console.log(matList.displayMats());

    console.log("Mats with 'exercise' label:");
    console.log(matList.findMatsByLabel("exercise"));

    console.log("\nRubber mats:");
    console.log(matList.findMatsByMaterial("rubber"));

    console.log("\nCollection statistics:");
    console.log(matList.getStats());

    console.log("\nUpdating mat #2 labels...");
    matList.updateMatLabels(2, ["kitchen", "anti-slip", "washable", "decorative"]);

    console.log("Mat #2 after update:");
    console.log(matList.findMatById(2));

    return matList;
}

// Export for use in other modules (if using Node.js modules)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { MatLabelList, demonstrateMatLabelList };
}

// Run demonstration if this file is executed directly
if (typeof window === 'undefined') {
    // In Node.js environment
    demonstrateMatLabelList();
}