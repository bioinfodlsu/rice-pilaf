import os


def get_nodes(network_file, output_dir):
    all_nodes = set()

    with open(network_file) as network:
        for edge in network:
            edge = edge.rstrip()
            nodes = edge.split('\t')

            all_nodes.add(nodes[0])
            all_nodes.add(nodes[1])

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f'{output_dir}/all-genes.txt', 'w') as f:
        f.write('\n'.join(list(all_nodes)))

    print(f"Wrote {len(all_nodes)} nodes to {output_dir}/all-genes.txt")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'network_file', help='text file corresponding to the edge list')
    parser.add_argument(
        'output_dir', help='output directory for the list of nodes'
    )

    args = parser.parse_args()

    get_nodes(args.network_file, args.output_dir)
