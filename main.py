import networkx as nx
import helper

data_filepath = "ia-wiki-trust-dir-cleaned.edges"

def main ():
  import networkx as nx

  # Reads the file into the graph
  G = nx.read_edgelist(
    data_filepath, 
    create_using=nx.DiGraph(), 
    nodetype=str, 
    data=(('sign', int),) 
  )
  print ("Loaded graph")

  # print(list(G.edges(data=True)))
  # Output: [('NodeA', 'NodeB', {'sign': 1}), ('NodeB', 'NodeC', {'sign': -1}), ...]

  # Visualizes the graph 
  helper.export_top_incoming_nodes(G, top_n=10)
  helper.show_balanced_graph(G, max_nodes=100)



if __name__ == "__main__":
  main()
