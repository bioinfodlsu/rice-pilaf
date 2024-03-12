import os
import pickle

import networkx as nx


def generate_mapping(mapping, edge_list_file, int_edge_list_node_mapping_file):
    G = None
    with open(edge_list_file, "r") as edge_list, open(
        int_edge_list_node_mapping_file, "rb"
    ) as int_edge_list_node_map:
        G = nx.read_edgelist(edge_list)
        int_edge_list_node_mapping = pickle.load(int_edge_list_node_map)

    sorted_nodes = sorted(G.nodes())

    for i, node in enumerate(sorted_nodes):
        mapping[i] = int_edge_list_node_mapping[int(node)]

    print("Finished mapping integer node labels to their (original) string node labels")


def save_node_mapping(mapping, node_mapping_dir):
    if not os.path.exists(node_mapping_dir):
        os.makedirs(node_mapping_dir)

    with open(f"{node_mapping_dir}/networkx-node-mapping.pickle", "wb") as handle:
        pickle.dump(mapping, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"Generated {node_mapping_dir}/networkx-node-mapping.pickle")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "edge_list_file",
        help="text file corresponding to the edge list with the node labels converted to integers",
    )
    parser.add_argument(
        "int_edge_list_node_mapping_file",
        help="pickled dictionary mapping the integer node labels to the (original) string labels",
    )
    parser.add_argument(
        "output_dir",
        help="output directory for the pickled dictionary mapping the node labels in the networkx integer-indexed graph to their (original) string labels",
    )

    args = parser.parse_args()

    mapping = {}
    generate_mapping(mapping, args.edge_list_file, args.int_edge_list_node_mapping_file)
    save_node_mapping(mapping, args.output_dir)
