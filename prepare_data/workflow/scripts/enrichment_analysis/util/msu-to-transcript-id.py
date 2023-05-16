import os
import pickle
from collections import defaultdict


def load_msu_to_transcript(msu_to_transcript_dict, id_file):
    with open(id_file) as f:
        for line in f:
            line = line.rstrip()

            # MSU ID
            if line[0] == 'L':
                msu_id = line
            else:
                msu_to_transcript_dict[msu_id].add(line)


def load_msu_to_rap(msu_to_rap_dict, rap_to_msu_file):
    with open(rap_to_msu_file) as rap_to_msu:
        for line in rap_to_msu:
            line = line.rstrip()

            rap, msu = line.split('\t')
            msu = msu.split(',')

            for id in msu:
                # Remove ".1" in "LOC_Os01g01019.1"
                id_components = id.split('.')
                id = id_components[0]

                if id != "None" and rap != "None":
                    msu_to_rap_dict[id].add(rap)


def load_rap_to_transcript(rap_to_transcript_dict, rap_to_transcipt_file):
    with open(rap_to_transcipt_file) as rap_to_transcript:
        for line in rap_to_transcript:
            line = line.split('\t')
            if line[0] != 'Transcript_ID':      # Ignore header row
                rap_to_transcript_dict[line[1]].add(line[0])


def map_using_rb_dp(msu_to_transcript_dict, msu_to_rap_dict, rap_to_transcript_dict, gene):
    transcript_ids = set()

    for rap_id in msu_to_rap_dict[gene]:
        transcript_ids = transcript_ids.union(rap_to_transcript_dict[rap_id])

    msu_to_transcript_dict[gene] = msu_to_transcript_dict[gene].union(
        transcript_ids)


def map_no_transcript_id(msu_to_transcript_dict, msu_to_rap_dict, rap_to_transcript_dict, no_transcript_id_file):
    with open(no_transcript_id_file) as no_transcript_id:
        for gene in no_transcript_id:
            gene = gene.rstrip()
            map_using_rb_dp(msu_to_transcript_dict,
                            msu_to_rap_dict, rap_to_transcript_dict, gene)

    print("Finished mapping MSU IDs to KEGG transcript IDs")


def save_msu_transcript_mapping(msu_to_transcript_dict, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f'{output_dir}/msu-to-transcript-id.pickle', 'wb') as handle:
        pickle.dump(msu_to_transcript_dict, handle,
                    protocol=pickle.HIGHEST_PROTOCOL)

    print(f'Generated {output_dir}/msu-to-transcript-id.pickle')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'riceidconverter_msu_to_transcript_id_file', help='text file containing MSU accessions and their respective KEGG transcript IDs as mapped via riceidcoverter')
    parser.add_argument(
        'riceidconverter_no_transcript_id_file', help='text file containing the list of MSU accessions that cannot be mapped by riceidcoverter to KEGG transcript IDs')
    parser.add_argument(
        'rap_to_msu_file', help='text file mapping RAP to MSU accessions')
    parser.add_argument(
        'rap_to_transcript_file', help='text file mapping RAP accessions to KEGG transcript IDs')
    parser.add_argument(
        'output_dir', help='output directory for the pickled dictionary mapping MSU accessions to their respective KEGG transcript IDs')

    args = parser.parse_args()

    msu_to_transcript_dict = defaultdict(set)
    msu_to_rap_dict = defaultdict(set)
    rap_to_transcript_dict = defaultdict(set)

    load_msu_to_transcript(msu_to_transcript_dict,
                           args.riceidconverter_msu_to_transcript_id_file)
    load_msu_to_rap(msu_to_rap_dict, args.rap_to_msu_file)
    load_rap_to_transcript(
        rap_to_transcript_dict, args.rap_to_transcript_file)

    map_no_transcript_id(msu_to_transcript_dict, msu_to_rap_dict, rap_to_transcript_dict,
                         args.riceidconverter_no_transcript_id_file)
    save_msu_transcript_mapping(msu_to_transcript_dict, args.output_dir)
