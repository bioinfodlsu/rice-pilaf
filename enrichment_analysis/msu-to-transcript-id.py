import os
import pickle
from collections import defaultdict


def load_msu_transcript_mapping(mapping, id_file):
    with open(id_file) as f:
        for line in f:
            line = line.rstrip()

            # MSU ID
            if line[0] == 'L':
                msu_id = line
            else:
                mapping[msu_id].append(line)

    print("Finished mapping MSU IDs to KEGG transcript IDs")


def save_msu_transcript_mapping(mapping, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f'{output_dir}/msu-to-transcript-id.pickle', 'wb') as handle:
        pickle.dump(mapping, handle,
                    protocol=pickle.HIGHEST_PROTOCOL)

    print(f'Generated {output_dir}/networkx-node-mapping.pickle')


if __name__ == '__main__':
    mapping = defaultdict(list)
    load_msu_transcript_mapping(mapping, 'data/temp/all-transcript-id.txt')
    save_msu_transcript_mapping(mapping, 'data')
