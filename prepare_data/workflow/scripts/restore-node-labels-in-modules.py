import pickle


def restore_node_labels(module_list_file, mapping_file, module_list_dir):
    with open(module_list_file, 'r') as modules, open(mapping_file, 'rb') as mapping, open(f'{module_list_dir}/module-list.txt', 'w') as output:
        mapping_dict = pickle.load(mapping)

        for module in modules:
            nodes = module.split('\t')
            nodes = nodes[:-1]                         # Ignore newline

            mapped_nodes = []
            for node in nodes:
                mapped_nodes.append(mapping_dict[int(node)])

            output.write('\t'.join(mapped_nodes) + '\n')

    print(f'Generated {module_list_dir}/module-list.txt')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'module_list_file', help='text file corresponding to the module list where the node labels are integers')
    parser.add_argument(
        'mapping_file', help='pickled integer-to-string node label mapping dictionary')
    parser.add_argument(
        'module_list_dir', help='output directory for the module list where the node labels are strings (i.e., the nodes are labeled with their original labels)')

    args = parser.parse_args()

    restore_node_labels(args.module_list_file,
                        args.mapping_file, args.module_list_dir)
