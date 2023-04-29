import os
import pickle


def convert_to_int_edge_list(string_to_int_mapping, int_to_string_mapping, input_file, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, 'r') as orig_graph, open(f'{output_dir}/int-edge-list.txt', 'w') as int_graph:
        for line in orig_graph:
            edges = line.split('\t')

            if edges[0] not in string_to_int_mapping:
                string_to_int_mapping[edges[0]] = len(string_to_int_mapping)
                int_to_string_mapping[string_to_int_mapping[edges[0]]] = edges[0]

            if edges[1] not in string_to_int_mapping:
                string_to_int_mapping[edges[1]] = len(string_to_int_mapping)
                int_to_string_mapping[string_to_int_mapping[edges[1]]] = edges[1]

            node1 = str(string_to_int_mapping[edges[0]])
            node2 = str(string_to_int_mapping[edges[1]])

            int_graph.write(node1 + " " + node2 + "\n")

    print("Finished mapping string node labels to integer node labels")


def save_node_mapping(int_to_string_mapping, node_mapping_dir):
    if not os.path.exists(node_mapping_dir):
        os.makedirs(node_mapping_dir)

    with open(f'{node_mapping_dir}/int-edge-list-node-mapping.pickle', 'wb') as handle:
        pickle.dump(int_to_string_mapping, handle,
                    protocol=pickle.HIGHEST_PROTOCOL)

    print(f'Generated {node_mapping_dir}/int-edge-list-node-mapping.pickle')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input_edge_list_file', help='text file corresponding to the edge list where the node labels are strings')
    parser.add_argument(
        'output_dir', help='output directory for the edge list with the node labels converted to integers and for the pickled integer-to-string node label mapping dictionary'
    )

    args = parser.parse_args()

    string_to_int_mapping = {}
    int_to_string_mapping = {}
    convert_to_int_edge_list(
        string_to_int_mapping, int_to_string_mapping, args.input_edge_list_file, args.output_dir)
    save_node_mapping(int_to_string_mapping, args.output_dir)
