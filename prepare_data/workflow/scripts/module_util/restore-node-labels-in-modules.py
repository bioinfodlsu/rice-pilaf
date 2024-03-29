import os
import pickle


def restore_node_labels(module_list_file, mapping_file, module_list_dir, algo):
    if not os.path.exists(module_list_dir):
        os.makedirs(module_list_dir)

    with open(module_list_file, "r") as modules, open(
        mapping_file, "rb"
    ) as mapping, open(f"{module_list_dir}/{algo}-module-list.tsv", "w") as output:
        mapping_dict = pickle.load(mapping)

        for module in modules:
            module = module.rstrip()
            nodes = module.split("\t")

            mapped_nodes = []
            for node in nodes:
                mapped_nodes.append(mapping_dict[int(node)])

            output.write("\t".join(mapped_nodes) + "\n")

    print(f"Generated {module_list_dir}/{algo}-module-list.tsv")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "module_list_file",
        help="text file corresponding to the module list where the node labels are integers",
    )
    parser.add_argument(
        "mapping_file", help="pickled integer-to-string node label mapping dictionary"
    )
    parser.add_argument(
        "module_list_dir",
        help="output directory for the module list where the nodes have been relabeled to their (original) string labels",
    )
    parser.add_argument("algo", help="name of community detection algorithm")

    args = parser.parse_args()

    restore_node_labels(
        args.module_list_file, args.mapping_file, args.module_list_dir, args.algo
    )
