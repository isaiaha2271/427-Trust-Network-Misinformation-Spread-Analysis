import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

from urllib.parse import urlparse

import copy
import logging
import collections


# silences matplotlib logger
logging.getLogger('matplotlib').setLevel(logging.WARNING)

#compute betweeness centrality of nodes
def betweenes_centrality(G):
    dict1 = nx.betweenness_centrality(G)
    listo = list(dict1.items())
    
    listo.sort(reverse = True, key=lambda pair: pair[1])
    return listo
#compute degree centrality of nodes
def degree_centrality(G):
    dict1 = nx.degree_centrality(G)
    listo = list(dict1.items())
    listo.sort(reverse= True, key=lambda pair: pair[1])
    return listo


# intializes graph
def initialize_graph(G):
    nx.set_node_attributes(
        G, 1 / len(G.nodes), "rank"
    )  # initializing rank for each node
    nx.set_node_attributes(
        G, 0, "rank_distribution"
    )  # creating distrbution attribute of ndoe

    G.graph["dangling_mass_set"] = (
        set()
    )  # will store set of nodes with no outgoing edges

    # set rank distribution value attributes for each node
    for node in G.nodes:
        num_out_edges = len(G.out_edges(node))
        G.nodes[node]["num_out_edges"] = num_out_edges

        if num_out_edges == 0:
            G.nodes[node]["rank_distribution"] = G.nodes[node]["rank"]
            G.graph["dangling_mass_set"].add(node)
        else:

            G.nodes[node]["rank_distribution"] = G.nodes[node]["rank"] / num_out_edges

    return G


# simulates one iteration of page rank algo
def simulate_pr_round(G, damp_factor):

    # for nodes in dangling node set intialize current dangling amss value
    dangling_mass = sum(G.nodes[node_]["rank"] for node_ in G["dangling_mass_set"])

    # for every node update its rank val & rank distribution val

    base = (1 - damp_factor) / len(G.nodes) + (
        damp_factor * (dangling_mass / len(G.nodes))
    )  # base compuation for  rank update used for every ndoe

    for node in G.nodes:
        incoming_rank_sum = sum(
            [G.nodes[src]["rank_distribution"] for src, _ in G.in_edges(node)]
        )  # get sum of incming edge ranks

        G.nodes[node]["rank"] = (
            base + damp_factor * incoming_rank_sum
        )  # assing sum of incoming rank to current node rank

        # update the nodes rank distribtution value
        if G.nodes[node]["num_out_edges"] == 0:
            G.nodes[node]["rank_distribution"] = G.nodes[node]["rank"]
        else:
            G.nodes[node]["rank_distribution"] = (
                G.nodes[node]["rank"] / G.nodes[node]["num_out_edges"]
            )

    return G


# simulates page_rank algo until convergence
def simulate_page_rank(G, damp_factor=0.85, delta_limit=0.001, max_iterations=1e5):

    G = initialize_graph(G)

    prev_rank = {}

    delta = 0

    # perform page rank round
    while delta > delta_limit and max_iterations:
        # store prev_ranks
        for node in G.nodes:
            prev_rank[node] = G.nodes[node]["rank"]

        G = simulate_pr_round(G, damp_factor)  # simulate one round of page rank

        # get change in new ranks vs prev ranks
        delta = sum(abs(G.nodes[node]["rank"] - prev_rank[node]) for node in G.nodes)

    return G


# writes page_rank values to a file
def ouput_page_rank_scores(pagerank_scores, file_path):
   # pagerank_scores = nx.pagerank(G, alpha=0.85)

    sorted_pagerank = sorted(pagerank_scores.items(), 
                         key=lambda item: item[1], 
                         reverse=True)

    # Write the sorted results to the file
    try:
        # Open the file in write mode ('w'). This creates the file if it doesn't exist, 
        # or overwrites it if it does.
        with open(file_path, 'w') as f:
            # Write a header
            f.write("--- PageRank Analysis Results (Sorted by Score) ---\n")
            f.write("Rank | Score (alpha=0.85) | URL\n")
            f.write("-" * 50 + "\n")
            
            # Iterate through the sorted list of (URL, Score) tuples
            for rank, (url, score) in enumerate(sorted_pagerank, 1):
                # Format the output string: Rank, Score (formatted to 6 decimal places), and URL
                output_line = f"{rank:<4} | {score:.6f} | {url}\n"
                f.write(output_line)

        print(f"\n Success: PageRank scores have been written to '{file_path}'")

    except IOError as e:
        print(f"\n Error writing file: {e}")


# writes graph to gml file
def write_outgraph(G, file_name):
    try:
        # Use write_gml to save the graph.
        # The 'pagerank' attribute is automatically included.
        nx.write_gml(G, file_name)
        print(f"\nSuccessfully exported graph to: {file_name}")
        print(
            "This file contains nodes and edges, with the 'pagerank' score saved as a node attribute."
        )

    except Exception as e:
        print(f"An error occurred during GML export: {e}")



#plot sorted lists of page rank, degree centrality, betwenesss centrality nodes, return nodes common in all three
def plot_measures(page_rank_vals, degree_cent, betweeness_cent):
    pr_nodes = []
    pr_vals = []

    degree_nodes= []
    degree_vals = []
    between_nodes = []

    between_vals = []

    for node,val in page_rank_vals:
        pr_nodes.append(str(node))
        pr_vals.append(val)
    plt.bar(pr_nodes,pr_vals)
    plt.xlabel("Nodes")
    plt.ylabel("Value")
    plt.title("Top 10 Nodes by Page Rank Value")
    plt.show()

    

    for node1,val1 in degree_cent:
        degree_nodes.append(str(node1))
        degree_vals.append(val1)
    plt.bar(degree_nodes,degree_vals)
    plt.xlabel("Nodes")
    plt.ylabel("Value")
    plt.title("Top 10 Nodes by Degree Centrality")
    plt.show()

    for node_,val_ in betweeness_cent:
        between_nodes.append(str(node_))
        between_vals.append(val_)
    plt.bar(between_nodes,between_vals)
    plt.xlabel("Nodes")
    plt.ylabel("Value")
    plt.title("Top 10 Nodes by Betweness Centrality")
    plt.show()


    #return set of nodes that appear in degree, betweeness, centrality measures
    set1,set2,set3 = set(degree_nodes),set(between_nodes),set(pr_nodes)
    return set1.intersection(set2,set3)

    


# plots digraph of page rank nodes
def plot_digraph(G,pagerank_scores):
    print(f"Nodes found: {G.number_of_nodes()}")
    print(f"Edges found: {G.number_of_edges()}")
    
    #pagerank_scores = nx.pagerank(G, alpha=0.85)    
    #pagerank_scores = simulate_page_rank(G, damp_factor=0.85,delta_limit=0.001)

    
    # 1. Create a list of scores corresponding to the order of nodes in G
    # The order is important: it must match the nodes in G.nodes()
    #node_scores_list = [G.nodes[node]["rank"] for node in G.nodes()]
    node_scores_list = [pagerank_scores[node] for node in G.nodes()]


    # 2. Scale the node sizes based on the PageRank score
    # Multiply by a large factor (e.g., 20000) to make the differences visible
    node_sizes = [v * 20000 for v in node_scores_list]

    # Plot
    plt.figure(figsize=(12, 8))

    # 1. Choose a layout algorithm to position the nodes
    # 'spring_layout' is often best for web graphs as it pulls connected nodes together
    pos = nx.spring_layout(G, seed=42)  # Use a seed for reproducible results

    # 2. Draw the graph
    nx.draw_networkx_nodes(
        G,
        pos,
        node_size=node_sizes,  # Node size reflects score (Importance)
        node_color=node_scores_list,  # Node color reflects score
        cmap=plt.cm.coolwarm,  # Choose a Colormap (e.g., 'coolwarm', 'Blues')
        linewidths=0.5,
        edgecolors="black",
    )

    # Draw the directed edges with arrows
    nx.draw_networkx_edges(
        G,
        pos,
        arrowstyle="->",  # Ensures clear arrows for directed graph
        arrowsize=5,  # Adjust size of arrowheads
        edge_color="gray",
        alpha=0.6,
    )
    
    '''# Draw Labels (Shortened URLs)
    labels = {node: node.replace("https://", "").replace("http://", "").replace("www.", "")[:25] + "..." 
              for node in G.nodes()}
    
    nx.draw_networkx_labels(
        G, 
        pos, 
        labels=labels, 
        font_size=8, 
        font_color='black',
        font_weight='bold'
    )
'''
    # Customize the display
    plt.title("DiGraph Visualization with PageRank Centrality")
    plt.axis("off")  # Turn off the axis lines and numbers
    plt.show()
