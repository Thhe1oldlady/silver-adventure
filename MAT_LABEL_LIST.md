# Mat Label List

A simple JavaScript implementation for managing materials (mats) with labels. This project demonstrates practical programming concepts and can be used as an example for GitHub Copilot code suggestions.

## Features

- ✅ Add mats with names, materials, colors, sizes, and labels
- ✅ Search mats by labels
- ✅ Filter mats by material type
- ✅ Update mat information
- ✅ Remove mats from the list
- ✅ View collection statistics
- ✅ Web interface for interactive management

## Files

- `mat-label-list.js` - Core JavaScript implementation with MatLabelList class
- `mat-label-list.html` - Web interface for managing the mat collection
- `MAT_LABEL_LIST.md` - This documentation file

## Usage

### Command Line (Node.js)

```bash
node mat-label-list.js
```

This will run a demonstration showing all the features of the MatLabelList class.

### Web Interface

Open `mat-label-list.html` in your web browser to use the interactive interface.

### Programming API

```javascript
// Create a new mat list
const matList = new MatLabelList();

// Add a mat
matList.addMat("Yoga Mat", "rubber", ["exercise", "yoga"], "purple", 6);

// Search by label
const exerciseMats = matList.findMatsByLabel("exercise");

// Filter by material
const rubberMats = matList.findMatsByMaterial("rubber");

// Get statistics
const stats = matList.getStats();

// Display all mats
console.log(matList.displayMats());
```

## Class Methods

### `MatLabelList`

- `addMat(name, material, labels, color, size)` - Add a new mat
- `getAllMats()` - Get all mats in the collection
- `findMatsByLabel(label)` - Find mats containing a specific label
- `findMatsByMaterial(material)` - Find mats made of a specific material
- `findMatById(id)` - Find a mat by its unique ID
- `updateMatLabels(id, newLabels)` - Update the labels for a mat
- `removeMat(id)` - Remove a mat from the collection
- `getStats()` - Get collection statistics
- `displayMats()` - Get formatted string representation of all mats

## Example Data Structure

```javascript
{
  id: 1,
  name: "Yoga Mat Pro",
  material: "rubber",
  labels: ["exercise", "yoga", "fitness"],
  color: "purple",
  size: 6,
  createdAt: "2025-09-10T13:57:36.356Z"
}
```

## Use Cases

This mat label list system can be adapted for various inventory management scenarios:

- 🧘 Yoga studio equipment management
- 🏠 Home organization and storage
- 🏢 Office equipment tracking
- 🏭 Workshop materials inventory
- 🎨 Art supplies organization

## Contributing

This is a demonstration project for GitHub Copilot. Feel free to extend the functionality or adapt it for your specific needs.

## License

This project is part of the GitHub Skills repository and follows the repository's licensing terms.