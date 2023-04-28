import pickle
mapping = {}

with open('rice_pilaf/data/networks/OS-CX.txt', 'r') as orig_graph, open('rice.txt', 'w') as int_graph:
    for line in orig_graph:
        edges = line.split('\t')

        if edges[0] not in mapping:
            mapping[edges[0]] = len(mapping)

        if edges[1] not in mapping:
            mapping[edges[1]] = len(mapping)

        node1 = str(mapping[edges[0]])
        node2 = str(mapping[edges[1]])

        int_graph.write(node1 + " " + node2 + "\n")


with open('rice_mapping.pickle', 'wb') as handle:
    pickle.dump(mapping, handle, protocol=pickle.HIGHEST_PROTOCOL)
