import os

import networkx as nx
from cdlib import algorithms, readwrite


def detect_modules(
    edge_list_file,
    module_list_dir,
    density_threshold,
    affinity_threshold,
    closeness_threshold,
):
    G = None
    with open(edge_list_file, "r") as f:
        G = nx.read_edgelist(f)
    G = nx.convert_node_labels_to_integers(G, ordering="sorted")

    coms = algorithms.coach(
        G,
        density_threshold=density_threshold,
        affinity_threshold=affinity_threshold,
        closeness_threshold=closeness_threshold,
    )

    if not os.path.exists(module_list_dir):
        os.makedirs(module_list_dir)

    readwrite.write_community_csv(
        coms,
        f"{module_list_dir}/coach-int-module-list-{int(affinity_threshold * 1000)}.csv",
        "\t",
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "edge_list_file", help="text file corresponding to the edge list"
    )
    parser.add_argument("module_list_dir", help="output directory for the module list")
    parser.add_argument(
        "--density_threshold",
        type=float,
        required=False,
        default=0.7,
        help="minimum core density (default = 0.7)",
    )
    parser.add_argument(
        "--affinity_threshold",
        type=float,
        required=False,
        default=0.225,
        help="maximum core affinity (default = 0.225)",
    )
    parser.add_argument(
        "--closeness_threshold",
        type=float,
        required=False,
        default=0.5,
        help="minimum neighbor closeness (default = 0.5)",
    )

    args = parser.parse_args()

    detect_modules(
        args.edge_list_file,
        args.module_list_dir,
        args.density_threshold,
        args.affinity_threshold,
        args.closeness_threshold,
    )
