import { useState, useMemo, useRef, useEffect } from 'react'
import { Network, DataSet } from 'vis-network/standalone'
import 'vis-network/styles/vis-network.css'
import './App.css'

function App() {
  const [graph, setGraph] = useState({ nodes: [], edges: [] })
  const [selectedNode, setSelectedNode] = useState(null)
  const [error, setError] = useState(null)

  // Test that React is rendering
  console.log('App component rendering')

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (event) => {
      try {
        const data = JSON.parse(event.target.result)
        const graphData = convertTreeToGraph(data)
        console.log('Nodes:', graphData.nodes.length)
        console.log('Edges:', graphData.edges.length)
        console.log('Graph:', graphData)
        setGraph(graphData)
      } catch (error) {
        setError(error.message)
        console.error('File parsing error:', error)
        alert('Error: ' + error.message)
      }
    }
    reader.readAsText(file)
  }

  const options = useMemo(() => ({
    layout: {
      hierarchical: {
        direction: 'UD',
        sortMethod: 'directed',
        levelSeparation: 300,
        nodeSpacing: 400,
        treeSpacing: 200,
        blockShifting: true,
        edgeMinimization: true,
        parentCentralization: true,
      },
    },
    edges: {
      color: { color: '#64748b', highlight: '#3b82f6' },
      width: 3,
      arrows: {
        to: {
          enabled: true,
          scaleFactor: 1.2,
        },
      },
      smooth: {
        type: 'curvedCW',
        roundness: 0.2,
      },
    },
    nodes: {
      shape: 'box',
      font: {
        color: '#ffffff',
        size: 14,
        face: 'Arial',
      },
      borderWidth: 3,
      borderColor: '#ffffff',
      shadow: true,
    },
    physics: {
      enabled: false,
    },
    interaction: {
      dragNodes: true,
      dragView: true,
      zoomView: true,
    },
    height: '100%',
    width: '100%',
  }), [])

  return (
    <div className="app">
      <div className="header">
        <h1>🌳 Reasoning Tree Visualizer</h1>
        <p>Select a JSON file to visualize</p>
        <p style={{ fontSize: '12px', marginTop: '10px' }}>App is rendering...</p>
      </div>

      <div className="controls">
        <input type="file" accept=".json" onChange={handleFileChange} />
      </div>

      <div className="graph-container">
        {error && (
          <div className="error-state">
            <p>Error: {error}</p>
            <p>Check browser console for details.</p>
          </div>
        )}
        {!error && graph.nodes.length === 0 ? (
          <div className="empty-state">
            <p>No tree loaded. Please select a JSON file.</p>
          </div>
        ) : !error ? (
          <GraphComponent 
            graph={graph} 
            options={options}
            onNodeSelect={(nodeData) => setSelectedNode(nodeData)}
          />
        ) : null}
      </div>

      {selectedNode && (
        <div className="details-panel">
          <div className="details-header">
            <h2>Node {selectedNode.nodeId}</h2>
            <button onClick={() => setSelectedNode(null)}>×</button>
          </div>
          <div className="details-content">
            <div>
              <strong>Brief:</strong>
              <p>{selectedNode.brief}</p>
            </div>
            {selectedNode.reasoning && (
              <div>
                <strong>Reasoning:</strong>
                <p>{selectedNode.reasoning}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

function convertTreeToGraph(node) {
  const nodes = []
  const edges = []

  function traverse(currentNode, parentId = null) {
    const nodeId = String(currentNode.id)
    const hasReasoning = !!(currentNode.reasoning && currentNode.reasoning.trim())

    const node = {
      id: nodeId,
      label: `Node ${currentNode.id}\n${(currentNode.brief || '(no brief)').substring(0, 40)}${(currentNode.brief || '').length > 40 ? '...' : ''}`,
      color: hasReasoning ? '#10b981' : '#667eea',
      data: {
        nodeId: currentNode.id,
        brief: currentNode.brief || '(no brief)',
        reasoning: currentNode.reasoning || null,
        hasReasoning,
      },
    }

    nodes.push(node)

    if (parentId !== null) {
      edges.push({
        from: parentId,
        to: nodeId,
        arrows: 'to',
        color: { color: '#64748b' },
        width: 3,
      })
    }

    if (currentNode.children && currentNode.children.length > 0) {
      currentNode.children.forEach((child) => {
        traverse(child, nodeId)
      })
    }
  }

  traverse(node)

  return { nodes, edges }
}

function GraphComponent({ graph, options, onNodeSelect }) {
  const containerRef = useRef(null)
  const networkRef = useRef(null)

  useEffect(() => {
    if (containerRef.current && graph.nodes.length > 0) {
      const data = {
        nodes: new DataSet(graph.nodes),
        edges: new DataSet(graph.edges),
      }
      
      const network = new Network(containerRef.current, data, options)
      networkRef.current = network
      
      network.on('select', function(params) {
        if (params.nodes.length > 0) {
          const nodeId = params.nodes[0]
          const node = graph.nodes.find(n => n.id === nodeId)
          if (node && onNodeSelect) {
            onNodeSelect(node.data)
          }
        }
      })
      
      return () => {
        if (networkRef.current) {
          networkRef.current.destroy()
          networkRef.current = null
        }
      }
    }
  }, [graph, options, onNodeSelect])

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
}

export default App

