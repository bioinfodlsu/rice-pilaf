import os
import pickle


def convert_msu_to_transcript(cluster_file, mapping_file, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(cluster_file) as clusters, open(mapping_file, 'rb') as mapping, open(f'{output_dir}/{cluster_file[:-len(".txt")]}_transcript_id.txt', 'w') as output_file:
        mapping_dict = pickle.load(mapping)

        for node in clusters:
            node = node.rstrip()
            for transcript_id in mapping_dict[node]:
                output_file.write(f'{transcript_id}\n')


if __name__ == '__main__':
    convert_msu_to_transcript(
        'data/clusters', 'data/msu-to-transcript-id.pickle', 'data/clusters_transcript_id')
