import os


def convert_module_to_edge_list(module, network_file, output_dir, filename):
    module = set(module)
    selected_nodes = set()
    with open(network_file) as network, open(f'{output_dir}/{filename}', 'w') as output:
        for edge in network:
            edge = edge.rstrip()
            nodes = edge.split('\t')

            if nodes[0] in module and nodes[1] in module:
                selected_nodes.add(nodes[0])
                selected_nodes.add(nodes[1])
                output.write(f'{nodes[0]}\t{nodes[1]}\n')

    assert len(module) == len(selected_nodes)


def convert_modules(network_file, module_file, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(module_file) as modules:
        for idx, module in enumerate(modules):
            module = module.rstrip()
            module = module.split('\t')
            filename = f'module-{idx + 1}.tsv'
            convert_module_to_edge_list(
                module, network_file, output_dir, filename)

            # Follow one-based indexing in R scripts for pathway enrichment analysis
            print(f'Generated edge list for module {idx + 1}')

    print("Finished generating edge lists for all modules")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'network_file', help='text file corresponding to the coexpression network')
    parser.add_argument(
        'module_file', help='text file corresponding to the list of modules')
    parser.add_argument(
        'output_dir', help='output directory for the edge list with the node labels converted to integers and for the pickled integer-to-string node label mapping dictionary'
    )

    args = parser.parse_args()
    convert_modules(args.network_file, args.module_file, args.output_dir)
