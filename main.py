import argparse
import networkx as nx
import matplotlib.pyplot as plt
import helper

# MAIN FUNCTION
def main():

    # PARSER SECTION
    # Creates the parser object in order to read in the passed in arguments and flags.
    #   Utilizes the argparse library to ease the implementation for a working CL structure.
    parser = argparse.ArgumentParser(
        prog="Trust Network Misinformation Spread Analyzer",
        description="Analyzes and visualizes graphs representing misinformation spread in trust networks.",
    )

    # Adds additional options and arguments to the parser, accoring to this CL structure:
    #   python ./graph.py ..
    parser.add_argument("--input", type=str)
    parser.add_argument("--pagerank_values", type=str)
    parser.add_argument("--plot_graph", type=bool)


    # Parses and gathers the arguments
    args = parser.parse_args()
    graph = None

    # Specifies the directed graph  (graph.gml) to be used in the page rank algorithm
    if args.input:
        graph = nx.read_edgelist(f"{args.input}",nodetype=int,data=(("trust",int),), create_using=nx.DiGraph())


    else:
        print("No --input loaded ")

    

    graph = helper.simulate_page_rank(graph)
    pr_dict = nx.pagerank(graph)

    #obtain top 10 nodes by betweeness and degree cent 
    betweeness_list = helper.betweenes_centrality(graph)[:10][::-1]
    degree_cent_list = helper.degree_centrality(graph)[:10][::-1]
    pr_score_list = sorted(pr_dict.items(), key=lambda item: item[1], reverse=True)[:10][::-1]
    

    #obtain nodes appearing in all three top 10 lists
    overlapping_nodes = helper.plot_measures(pr_score_list,degree_cent_list,betweeness_list)
    if overlapping_nodes:
        print("The following nodes have high betweeness, degree centrality, and page_rank values:" )
        for node in overlapping_nodes:
            print(f"{node} ", end="")

    print("\n")




    
    # Displays the graph
    if args.plot_graph:
        helper.plot_digraph(graph,pr_dict)


    if args.pagerank_values:
        helper.ouput_page_rank_scores(graph, args.pagerank_values)
        
   


# Runs the program
if __name__ == "__main__":
    main()


'''python ./main.py --input trust_1.edges --plot_graph True'''

