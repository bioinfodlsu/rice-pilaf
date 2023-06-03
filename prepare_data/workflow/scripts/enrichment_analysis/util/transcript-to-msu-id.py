import pickle
import os
from collections import defaultdict


def convert_transcript_to_msu(msu_to_transcript_dict):
    transcript_to_msu = defaultdict(set)
    with open(msu_to_transcript_dict, 'rb') as f:
        msu_to_transcript = pickle.load(f)

        for msu, transcript_ids in msu_to_transcript.items():
            for transcript in transcript_ids:
                transcript_to_msu[transcript].add(msu)

    return transcript_to_msu


def save_transcript_msu_mapping(transcript_to_msu, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f'{output_dir}/transcript-to-msu-id.pickle', 'wb') as handle:
        pickle.dump(transcript_to_msu, handle,
                    protocol=pickle.HIGHEST_PROTOCOL)

    print(f'Generated {output_dir}/transcript-to-msu-id.pickle')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'msu_to_transcript_dict', help='pickled dictionary mapping MSU accessions to their respective KEGG transcript IDs')
    parser.add_argument(
        'output_dir', help='output directory for the pickled dictionary mapping KEGG transcript IDs to their respective MSU accessions')

    args = parser.parse_args()

    transcript_to_msu = convert_transcript_to_msu(args.msu_to_transcript_dict)

    save_transcript_msu_mapping(transcript_to_msu, args.output_dir)
