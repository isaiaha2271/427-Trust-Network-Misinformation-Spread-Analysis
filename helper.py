import networkx as nx
import igraph as ig
import matplotlib.pyplot as plt
import numpy as np
import csv


import networkx as nx
import matplotlib.pyplot as plt

def show_balanced_graph(G: nx.DiGraph, sign_attribute='sign', max_nodes=None):
    """
    Visualizes a signed directed graph with an optional node limit.
    
    Parameters:
    - G: A networkx DiGraph object
    - sign_attribute: Key for the sign
    - max_nodes: (Optional) Integer. If set, only visualizes the top N most connected nodes.
    """

    # Filter graph if max_nodes is set
    if max_nodes is not None and len(G) > max_nodes:
        print(f"Graph has {len(G)} nodes. Filtering to top {max_nodes} by degree...")
        # Sort nodes by degree (connectivity) and slice the top N
        top_nodes = sorted(G.degree, key=lambda x: x[1], reverse=True)[:max_nodes]
        nodes_to_keep = [n for n, d in top_nodes]
        G = G.subgraph(nodes_to_keep)

    # Setup the layout
    pos = nx.spring_layout(G, seed=42, k=1/np.sqrt(len(G.nodes())))

    # Create the Plot
    plt.figure(figsize=(10, 8))

    # Draw Nodes
    nx.draw_networkx_nodes(G, pos, node_size=300, node_color='lightblue', edgecolors='black')

    # Draw edges with different styles for positive/negative signs
    edge_signs = nx.get_edge_attributes(G, 'sign')
    if edge_signs:
      pos_edges = [(u, v) for u, v in G.edges() if edge_signs.get((u, v), edge_signs.get((v, u), 1)) > 0]
      neg_edges = [(u, v) for u, v in G.edges() if edge_signs.get((u, v), edge_signs.get((v, u), 1)) <= 0]
      
      nx.draw_networkx_edges(G, pos, edgelist=pos_edges, edge_color='lightgreen', 
                            width=1, alpha=0.6, label='Positive')
      nx.draw_networkx_edges(G, pos, edgelist=neg_edges, edge_color='red', 
                            width=1, style='dashed', alpha=0.6, label='Negative')
      plt.legend()
    else:
      nx.draw_networkx_edges(G, pos, alpha=0.4)
    
    nx.draw_networkx_labels(G, pos, font_size=8)

    # Final settings
    plt.title(f"Signed Graph ({len(G)} nodes)")
    plt.legend()
    plt.axis('off')
    plt.show()

def export_top_incoming_nodes(G, output_file="node_analysis.csv", top_n=5, sign_attribute='sign'):
    """
    Identifies the top N nodes with the highest incoming positive and negative edges.
    Writes the results to a CSV file.

    Parameters:
    - G: A networkx DiGraph
    - output_file: Filename for the output CSV
    - top_n: Number of top nodes to retrieve for each category
    - sign_attribute: The edge attribute key holding the sign (e.g., 'sign')
    """
    
    # Dictionary to store stats per node
    # Structure: {node_id: {'pos_in': 0, 'neg_in': 0, 'total_in': 0}}
    node_stats = {node: {'pos_in': 0, 'neg_in': 0} for node in G.nodes()}

    # 1. Iterate through all edges to count incoming signs
    # u -> v (u is source, v is destination)
    for u, v, data in G.edges(data=True):
        sign = data.get(sign_attribute, 0)
        
        if sign > 0:
            node_stats[v]['pos_in'] += 1
        elif sign < 0:
            node_stats[v]['neg_in'] += 1

    # 2. Prepare lists for sorting
    analysis_list = []
    for node, stats in node_stats.items():
        pos = stats['pos_in']
        neg = stats['neg_in']
        total = pos + neg
        
        # Calculate percentages (avoid division by zero)
        pos_pct = (pos / total * 100) if total > 0 else 0.0
        neg_pct = (neg / total * 100) if total > 0 else 0.0
        
        analysis_list.append({
            'node': node,
            'pos_in': pos,
            'neg_in': neg,
            'total_in': total,
            'pos_pct': pos_pct,
            'neg_pct': neg_pct
        })

    # Get Top N for Negative Incoming
    # Sort by 'neg_in' descending
    top_negative = sorted(analysis_list, key=lambda x: x['neg_in'], reverse=True)[:top_n]

    # Get Top N for Positive Incoming
    # Sort by 'pos_in' descending
    top_positive = sorted(analysis_list, key=lambda x: x['pos_in'], reverse=True)[:top_n]

    # Write to File
    print(f"Writing analysis to {output_file}...")
    with open(output_file, mode='w', newline='') as f:
        writer = csv.writer(f)
        
        # Section 1: Top Incoming Negative
        writer.writerow([f"--- TOP {top_n} NODES WITH HIGHEST INCOMING NEGATIVE EDGES ---"])
        writer.writerow(["Node", "Incoming Negative Count", "Negative Ratio (%)", "Total Incoming"])
        for item in top_negative:
            writer.writerow([
                item['node'], 
                item['neg_in'], 
                f"{item['neg_pct']:.2f}%", 
                item['total_in']
            ])
            
        writer.writerow([]) # Empty line for spacing

        # Section 2: Top Incoming Positive
        writer.writerow([f"--- TOP {top_n} NODES WITH HIGHEST INCOMING POSITIVE EDGES ---"])
        writer.writerow(["Node", "Incoming Positive Count", "Positive Ratio (%)", "Total Incoming"])
        for item in top_positive:
            writer.writerow([
                item['node'], 
                item['pos_in'], 
                f"{item['pos_pct']:.2f}%", 
                item['total_in']
            ])

    print("Done.")



