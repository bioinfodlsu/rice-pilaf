import pickle


def convert_to_int_edgelist(mapping, input_file, output_file):
    with open(input_file, 'r') as orig_graph, open(output_file, 'w') as int_graph:
        for line in orig_graph:
            edges = line.split('\t')

            if edges[0] not in mapping:
                mapping[edges[0]] = len(mapping)

            if edges[1] not in mapping:
                mapping[edges[1]] = len(mapping)

            node1 = str(mapping[edges[0]])
            node2 = str(mapping[edges[1]])

            int_graph.write(node1 + " " + node2 + "\n")


def save_node_mapping(mapping, mapping_file):
    with open(mapping_file, 'wb') as handle:
        pickle.dump(mapping, handle, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    mapping = {}

    # convert_to_int_edgelist(mapping, )
