# Reasoning Tree Visualizer

A React-based UI to visualize reasoning tree structures from JSON snapshot files using React Flow.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser to the URL shown (typically `http://localhost:5173`)

## Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Usage

1. Start the dev server (see Setup above)
2. Click "Choose File" and select a JSON file from the `tree_snapshots` directory (e.g., `tree_snapshots/ed32/10.json`)
3. The tree will be rendered automatically with React Flow

## Features

- **Tree Visualization**: Nodes are displayed in a hierarchical tree structure using React Flow
- **Node Details**: Click on any node to see its details (ID, brief, and reasoning) in a side panel
- **Visual Indicators**: 
  - Green nodes have reasoning content (active path)
  - Purple nodes don't have reasoning (collapsed branches)
- **Interactive Controls**: 
  - Zoom controls (bottom left)
  - Mini-map (bottom right)
  - Pan and zoom with mouse/trackpad
- **Responsive**: The UI adapts to different screen sizes

## Node Colors

- **Purple**: Nodes without reasoning (collapsed branches)
- **Green**: Nodes with reasoning (active path - full visibility)

## Controls

- **Click node**: View detailed information about the node in the side panel
- **Zoom controls**: Use the controls in the bottom left
- **Mini-map**: See an overview of the entire tree (bottom right)
- **Pan**: Click and drag on the canvas to pan around
- **Zoom**: Use mouse wheel or trackpad pinch to zoom

