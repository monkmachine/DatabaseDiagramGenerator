import json
from typing import Dict, Any

def generate_html(schema: Dict[str, Any]) -> str:
    """
    Generates a standalone HTML file containing a React Flow application
    to visualize the database schema.
    
    Uses UMD builds of React and React Flow via jsDelivr to ensure compatibility 
    with file:// protocol, and uses pure React.createElement to avoid 
    need for in-browser Babel transformation.
    """
    schema_json = json.dumps(schema)
    
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Database Diagram</title>
    <style>
        :root {
            --bg-color: #1a192b;
            --text-color: #fff;
            --node-bg: #25252e;
            --node-border: #444;
            --node-selected: #74b9ff;
            --control-bg: #1e1e24;
            --input-bg: #25252e;
            --header-bg-start: #323242;
            --header-bg-end: #2a2a35;
            --column-text: #ccc;
            --column-hover: rgba(255,255,255,0.05);
            --edge-color: #666;
            --edge-dim: 0.05;
        }

        [data-theme="light"] {
            --bg-color: #f5f6fa;
            --text-color: #2d3436;
            --node-bg: #ffffff;
            --node-border: #dcdde1;
            --node-selected: #0984e3;
            --control-bg: #ffffff;
            --input-bg: #f1f2f6;
            --header-bg-start: #f8f9fa;
            --header-bg-end: #e9ecef;
            --column-text: #636e72;
            --column-hover: rgba(0,0,0,0.03);
            --edge-color: #b2bec3;
            --edge-dim: 0.1;
        }

        body { margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: var(--bg-color); color: var(--text-color); overflow: hidden; transition: background 0.3s; }
        #root { width: 100vw; height: 100vh; }
        
        /* Custom Scrollbar for columns */
        .nopan { overflow-y: auto; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #888; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #555; }

        .controls {
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 10;
            background: var(--control-bg);
            padding: 16px;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.15);
            border: 1px solid var(--node-border);
            display: flex;
            flex-direction: column;
            gap: 12px;
            min-width: 260px;
            backdrop-filter: blur(10px);
            transition: background 0.3s, border-color 0.3s;
        }
        
        input {
            background: var(--input-bg);
            border: 1px solid var(--node-border);
            color: var(--text-color);
            padding: 10px 14px;
            border-radius: 6px;
            outline: none;
            transition: all 0.2s;
            font-size: 14px;
        }
        input:focus { border-color: var(--node-selected); }

        .legend {
            font-size: 13px;
            color: var(--column-text);
            margin-top: 4px;
            line-height: 1.4;
        }
        
        button {
            transition: all 0.2s;
        }
        button:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }

        .node-table {
            background: var(--node-bg);
            border: 1px solid var(--node-border);
            border-radius: 8px;
            min-width: 240px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            color: var(--text-color);
        }
        
        .node-table:hover {
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
            border-color: var(--edge-color);
            transform: translateY(-2px);
        }
        
        .node-table.selected {
            border-color: var(--node-selected);
            box-shadow: 0 0 0 2px var(--node-selected), 0 8px 24px rgba(0,0,0,0.2);
        }
        
        .node-table.dimmed {
            opacity: 0.2;
            filter: grayscale(1);
        }

        .table-header {
            background: linear-gradient(180deg, var(--header-bg-start) 0%, var(--header-bg-end) 100%);
            padding: 12px 16px;
            font-weight: 600;
            font-size: 15px;
            border-bottom: 1px solid var(--node-border);
            color: var(--text-color);
            letter-spacing: 0.5px;
        }
        
        .table-columns {
            padding: 8px 0;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .table-column {
            padding: 8px 16px;
            font-size: 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: var(--column-text);
            transition: background 0.1s;
            cursor: help; /* Hint for tooltip */
        }
        
        .table-column:hover {
            background: var(--column-hover);
            color: var(--text-color);
        }
        
        .column-type {
            color: #888;
            font-size: 11px;
            font-family: 'Consolas', 'Monaco', monospace;
            margin-left: 12px;
            background: rgba(127, 127, 127, 0.1);
            padding: 2px 6px;
            border-radius: 4px;
        }
        
        .pk-badge {
            color: #f1c40f;
            margin-right: 8px;
            font-size: 12px;
        }

        .fk-badge {
            color: #a5b1c2;
            margin-right: 8px;
            font-size: 10px;
            border: 1px solid #777;
            padding: 0 4px;
            border-radius: 3px;
        }
        
        /* Handles */
        .react-flow__handle {
            opacity: 0; 
            width: 8px;
            height: 8px;
            background: var(--node-selected); 
        }
        .node-table.selected .react-flow__handle {
            opacity: 1; 
        }

        .toggle-container {
            display: flex;
            align-items: center;
            font-size: 13px;
            color: var(--text-color);
            cursor: pointer;
            gap: 8px;
        }
        .toggle-switch {
            position: relative;
            width: 36px;
            height: 20px;
            background: var(--input-bg);
            border-radius: 20px;
            border: 1px solid var(--node-border);
            transition: background 0.2s;
        }
        .toggle-switch.active {
            background: var(--node-selected);
            border-color: var(--node-selected);
        }
        .toggle-thumb {
            position: absolute;
            top: 2px;
            left: 2px;
            width: 14px;
            height: 14px;
            background: #fff;
            border-radius: 50%;
            transition: transform 0.2s;
        }
        .toggle-switch.active .toggle-thumb {
            transform: translateX(16px);
        }
    </style>
    
    <!-- UMD Builds via jsDelivr -->
    <script src="https://cdn.jsdelivr.net/npm/react@18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/react-dom@18.2.0/umd/react-dom.production.min.js"></script>
    
    <!-- React Flow UMD -->
    <!-- Note: reactflow 11.x UMD build exports to window.ReactFlow -->
    <script src="https://cdn.jsdelivr.net/npm/reactflow@11.10.1/dist/umd/index.min.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reactflow@11.10.1/dist/style.css" />

    <!-- Dagre UMD -->
    <script src="https://cdn.jsdelivr.net/npm/dagre@0.8.5/dist/dagre.min.js"></script>
</head>
<body>
    <div id="root"></div>
    
    <!-- Inject Schema Data -->
    <script>
        window.initialSchema = __SCHEMA_JSON__;
    </script>

    <script>
        // Pure JS - No Babel needed
        const { useState, useEffect, useCallback, useMemo, createElement: h } = React;
        const { createRoot } = ReactDOM;
        
        // Handle ReactFlow export differences
        const ReactFlowObj = window.ReactFlow;
        const ReactFlowComp = ReactFlowObj.default || ReactFlowObj;
        const { 
            Background, 
            Controls, 
            useNodesState, 
            useEdgesState,
            MarkerType,
            Handle,
            Position
        } = ReactFlowObj;
        
        const dagre = window.dagre;
        const schema = window.initialSchema;

        // --- Components ---

        const TableNode = ({ data }) => {
            // Filter columns if 'showOnlyKeys' is true
            const visibleColumns = useMemo(() => {
                if (!data.showOnlyKeys) return data.columns;
                return data.columns.filter(col => col.pk || col.is_fk);
            }, [data.columns, data.showOnlyKeys]);

            return h('div', { 
                className: `node-table ${data.isSelected ? 'selected' : ''} ${data.isDimmed ? 'dimmed' : ''}` 
            }, [
                h('div', { className: 'table-header', key: 'header' }, [
                    h('span', { key: 'lbl' }, data.label),
                    data.showOnlyKeys && data.hiddenCount > 0 
                        ? h('span', { style: { fontSize: '10px', opacity: 0.7, marginLeft: '6px' }, key: 'cnt' }, `+${data.hiddenCount}`)
                        : null
                ]),
                h('div', { className: 'table-columns nopan', key: 'cols' }, 
                    visibleColumns.map((col, idx) => 
                        h('div', { 
                            key: idx, 
                            className: 'table-column', 
                            style: { position: 'relative' },
                            title: `Type: ${col.type}\nPK: ${col.pk ? 'Yes' : 'No'}\nFK: ${col.is_fk ? 'Yes' : 'No'}` 
                        }, [
                            // Target Handle (Left)
                            h(Handle, { 
                                type: 'target', 
                                position: 'left', 
                                id: col.name,
                                style: { left: -5 }, 
                                key: `h-tgt-${col.name}`
                            }),
                            h('span', { style: { display: 'flex', alignItems: 'center' }, key: 'name' }, [
                                col.pk ? h('span', { className: 'pk-badge', key: 'pk', title: 'Primary Key' }, '🔑') : null,
                                col.is_fk ? h('span', { className: 'fk-badge', key: 'fk', title: 'Foreign Key' }, 'FK') : null,
                                col.name
                            ]),
                            h('span', { className: 'column-type', key: 'type' }, col.type),
                            // Source Handle (Right)
                            h(Handle, { 
                                type: 'source', 
                                position: 'right', 
                                id: col.name,
                                style: { right: -5 }, 
                                key: `h-src-${col.name}`
                            })
                        ])
                    )
                )
            ]);
        };
        
        const nodeTypes = { table: TableNode };

        // Layout Graph using Dagre
        const getLayoutedElements = (nodes, edges, direction = 'LR') => {
            const dagreGraph = new dagre.graphlib.Graph();
            dagreGraph.setDefaultEdgeLabel(() => ({}));

            // Increased spacing for cleaner look
            dagreGraph.setGraph({ 
                rankdir: direction,
                ranksep: 100, // Horizontal separation between ranks
                nodesep: 40   // Vertical separation between nodes
            });

            nodes.forEach((node) => {
                // Approximate size: Width 240, Height based on columns (header 45 + 35 per col)
                // When filtering, height changes, but for layout stability we might want to keep it or re-calc.
                // For simplicity, we re-calc based on *current* visible columns in the node data passed here.
                const visibleColCount = node.data.showOnlyKeys 
                    ? node.data.columns.filter(c => c.pk || c.is_fk).length 
                    : node.data.columns.length;
                
                const height = 45 + (visibleColCount * 35);
                dagreGraph.setNode(node.id, { width: 240, height: height });
            });

            edges.forEach((edge) => {
                dagreGraph.setEdge(edge.source, edge.target);
            });

            dagre.layout(dagreGraph);

            const layoutedNodes = nodes.map((node) => {
                const nodeWithPosition = dagreGraph.node(node.id);
                return {
                    ...node,
                    position: {
                        x: nodeWithPosition.x - 120, // Center anchor fix
                        y: nodeWithPosition.y - (nodeWithPosition.height / 2),
                    },
                };
            });

            return { nodes: layoutedNodes, edges };
        };

        const App = () => {
            const [nodes, setNodes, onNodesChange] = useNodesState([]);
            const [edges, setEdges, onEdgesChange] = useEdgesState([]);
            const [searchTerm, setSearchTerm] = useState('');
            const [selectedNodeId, setSelectedNodeId] = useState(null);
            const [theme, setTheme] = useState('dark'); // 'dark' | 'light'
            const [showOnlyKeys, setShowOnlyKeys] = useState(false);

            // Apply theme class
            useEffect(() => {
                document.documentElement.setAttribute('data-theme', theme);
            }, [theme]);

            const toggleTheme = useCallback(() => {
                setTheme(prev => prev === 'dark' ? 'light' : 'dark');
            }, []);

            // Initialize Graph and Pre-process Data
            useEffect(() => {
                const initialNodes = [];
                const initialEdges = [];
                
                // 1. Pre-process schema to identify Foreign Key columns
                const fkColumns = {}; // { tableName: Set(colName) }
                
                Object.keys(schema.tables).forEach(tName => {
                    if (!fkColumns[tName]) fkColumns[tName] = new Set();
                    schema.tables[tName].foreign_keys.forEach(fk => {
                        fkColumns[tName].add(fk.from_column);
                    });
                });

                // 2. Create Nodes with `is_fk` flag
                Object.keys(schema.tables).forEach(tableName => {
                    const table = schema.tables[tableName];
                    const columnsWithFK = table.columns.map(col => ({
                        ...col,
                        is_fk: fkColumns[tableName]?.has(col.name) || false
                    }));

                    initialNodes.push({
                        id: tableName,
                        type: 'table',
                        data: { 
                            label: tableName, 
                            columns: columnsWithFK,
                            isSelected: false,
                            isDimmed: false,
                            showOnlyKeys: false, // Initial state
                            hiddenCount: 0
                        },
                        position: { x: 0, y: 0 } 
                    });
                });

                // 3. Create Edges
                Object.keys(schema.tables).forEach(tableName => {
                    const table = schema.tables[tableName];
                    table.foreign_keys.forEach(fk => {
                        if (schema.tables[fk.target_table]) {
                            initialEdges.push({
                                id: `e-${tableName}-${fk.from_column}-${fk.target_table}-${fk.to_column}`,
                                source: tableName,      
                                sourceHandle: fk.from_column,
                                target: fk.target_table, 
                                targetHandle: fk.to_column,
                                type: 'default',
                                animated: false,
                                style: { stroke: 'var(--edge-color)', strokeWidth: 2 },
                                markerEnd: { type: MarkerType.ArrowClosed, color: 'var(--edge-color)' },
                            });
                        }
                    });
                });

                const layout = getLayoutedElements(initialNodes, initialEdges);
                setNodes(layout.nodes);
                setEdges(layout.edges);
            }, []);

            // Handle Interaction & State Updates
            useEffect(() => {
                const style = getComputedStyle(document.body);
                const edgeColor = style.getPropertyValue('--edge-color').trim();
                const selectedColor = style.getPropertyValue('--node-selected').trim();
                const edgeDim = parseFloat(style.getPropertyValue('--edge-dim').trim() || '0.1');

                // Update Nodes
                setNodes((nds) => 
                    nds.map((node) => {
                        const matchesSearch = searchTerm === '' || node.data.label.toLowerCase().includes(searchTerm.toLowerCase());
                        
                        let isDimmed = !matchesSearch; 
                        let isSelected = false;

                        if (selectedNodeId) {
                            const isConnected = edges.some(e => 
                                (e.source === selectedNodeId && e.target === node.id) || 
                                (e.target === selectedNodeId && e.source === node.id)
                            );
                            
                            if (node.id === selectedNodeId) {
                                isSelected = true;
                                isDimmed = false;
                            } else if (isConnected) {
                                isDimmed = false;
                            } else {
                                isDimmed = true;
                            }
                        } else {
                            if (searchTerm && !matchesSearch) isDimmed = true;
                        }
                        
                        // Calculate hidden count
                        const visibleCount = node.data.columns.filter(c => c.pk || c.is_fk).length;
                        const hiddenCount = node.data.columns.length - visibleCount;

                        return {
                            ...node,
                            data: { 
                                ...node.data, 
                                isDimmed, 
                                isSelected, 
                                showOnlyKeys, // Propagate global filter state
                                hiddenCount
                            }
                        };
                    })
                );

                // Update Edges
                setEdges((eds) => 
                    eds.map((edge) => {
                        let stroke = edgeColor;
                        let strokeWidth = 2;
                        let opacity = 1;
                        let zIndex = 0;

                        if (selectedNodeId) {
                            if (edge.source === selectedNodeId || edge.target === selectedNodeId) {
                                stroke = selectedColor;
                                strokeWidth = 3;
                                zIndex = 10;
                            } else {
                                opacity = edgeDim; 
                            }
                        }

                        return {
                            ...edge,
                            zIndex,
                            style: { ...edge.style, stroke, strokeWidth, opacity },
                            markerEnd: { ...edge.markerEnd, color: stroke }
                        };
                    })
                );
                
                // Note: We might want to re-run layout when toggling keys, 
                // but Dagre layout is expensive and might jump around.
                // For now, we update node data but keep positions. 
                // If nodes shrink significantly, gaps will appear, which is acceptable.

            }, [searchTerm, selectedNodeId, edges.length, theme, showOnlyKeys]); 

            const onNodeClick = useCallback((event, node) => {
                setSelectedNodeId((prev) => (prev === node.id ? null : node.id));
            }, []);

            const onPaneClick = useCallback(() => {
                setSelectedNodeId(null);
            }, []);

            // Render
            return h(React.Fragment, null, [
                h('div', { className: 'controls', key: 'ctrl' }, [
                    h('div', { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' }, key: 'top' }, [
                        h('h3', { style: { margin: 0, fontSize: '18px', fontWeight: '600', color: 'var(--text-color)' }, key: 't' }, 'DB Diagram'),
                        h('button', {
                             onClick: toggleTheme,
                             style: {
                                background: 'transparent', border: '1px solid var(--node-border)', 
                                color: 'var(--text-color)', padding: '4px 8px', borderRadius: '4px', cursor: 'pointer', fontSize: '16px'
                             },
                             title: 'Toggle Theme',
                             key: 'theme-btn'
                        }, theme === 'dark' ? '☀️' : '🌙')
                    ]),
                    
                    // Search
                    h('input', { 
                        type: 'text', 
                        placeholder: 'Search tables...', 
                        value: searchTerm,
                        onChange: (e) => setSearchTerm(e.target.value),
                        key: 'inp'
                    }),

                    // Column Filter Toggle
                    h('div', { 
                        className: 'toggle-container', 
                        onClick: () => setShowOnlyKeys(!showOnlyKeys),
                        key: 'tgl'
                    }, [
                        h('div', { className: `toggle-switch ${showOnlyKeys ? 'active' : ''}`, key: 'sw' }, 
                            h('div', { className: 'toggle-thumb', key: 'th' })
                        ),
                        'Show Only Keys'
                    ]),

                    h('div', { className: 'legend', key: 'leg' }, [
                        'Hover columns for details.', h('br', { key: 'br' }), 'Shift + drag to select.'
                    ]),
                    
                    selectedNodeId ? h('button', {
                        onClick: () => setSelectedNodeId(null),
                        style: {
                            background: 'var(--node-selected)', border: 'none', padding: '8px 12px', 
                            borderRadius: '6px', cursor: 'pointer', color: '#fff',
                            fontWeight: '600', fontSize: '13px', marginTop: '5px'
                        },
                        key: 'btn'
                    }, 'Clear Selection') : null,
                    h('div', { style: { marginTop: '10px', fontSize: '11px', color: 'var(--column-text)' }, key: 'cred' }, 'Generated by Antigravity')
                ]),
                h(ReactFlowComp, {
                    nodes: nodes,
                    edges: edges,
                    onNodesChange: onNodesChange,
                    onEdgesChange: onEdgesChange,
                    onNodeClick: onNodeClick,
                    onPaneClick: onPaneClick,
                    nodeTypes: nodeTypes,
                    fitView: true,
                    minZoom: 0.1,
                    connectionLineType: 'default',
                    key: 'rf'
                }, [
                    h(Background, { color: theme === 'dark' ? '#888' : '#ccc', gap: 20, variant: 'dots', size: 1, key: 'bg' }),
                    h(Controls, { key: 'controls', style: { display: 'flex', flexDirection: 'column', gap: '2px' } }) 
                ])
            ]);
        };
        
        const root = createRoot(document.getElementById('root'));
        root.render(h(App));
    </script>
</body>
</html>
"""
    return html_template.replace("__SCHEMA_JSON__", schema_json)
