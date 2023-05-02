import os

import networkx as nx
from cdlib import algorithms, readwrite


def detect_modules(edge_list_file, module_list_dir, epsilon, min_com_size):
    G = None
    with open(edge_list_file, 'r') as f:
        G = nx.read_edgelist(f)
    G = nx.convert_node_labels_to_integers(G, ordering="sorted")

    coms = algorithms.demon(G, epsilon=epsilon, min_com_size=min_com_size)

    if not os.path.exists(module_list_dir):
        os.makedirs(module_list_dir)

    readwrite.write_community_csv(
        coms, f'{module_list_dir}/demon-int-module-list.csv', '\t')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'edge_list_file', help='text file corresponding to the edge list')
    parser.add_argument(
        'module_list_dir', help='output directory for the module list')
    parser.add_argument(
        '-epsilon', type=float, required=False, default=0.25, help='merging threshold (default = 0.25)'
    )
    parser.add_argument(
        '-min_com_size', type=int, required=False, default=3, help='minimum size of a module (default = 3)'
    )

    args = parser.parse_args()

    detect_modules(args.edge_list_file,
                   args.module_list_dir, args.epsilon, args.min_com_size)
