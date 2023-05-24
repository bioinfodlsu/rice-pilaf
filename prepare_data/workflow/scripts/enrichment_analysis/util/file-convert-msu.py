import csv
import os
import pickle


def convert_msu(msu_id_file, mapping_file, output_dir, target_id, skip_no_matches):
    if not os.path.exists(f'{output_dir}/{target_id}'):
        os.makedirs(f'{output_dir}/{target_id}')

    output_file_name = msu_id_file.split('/')[-1]
    # Change file extension to tsv
    output_file_name = output_file_name[:-len('.txt')] + '.tsv'

    with open(msu_id_file) as msu_file, open(mapping_file, 'rb') as mapping, open(f'{output_dir}/{target_id}/{output_file_name}', 'w') as output:
        mapping_dict = pickle.load(mapping)

        csv_reader = csv.reader(msu_file, delimiter='\t')
        for line in csv_reader:
            output_set = set()
            for msu_id in line:
                if len(mapping_dict[msu_id]) != 0:
                    output_set = output_set.union(mapping_dict[msu_id])

            output.write('\t'.join(list(output_set)))

            if skip_no_matches and len(output_set) > 0:
                output.write('\n')
            elif not skip_no_matches:
                output.write('\n')

    print(f'Generated {output_dir}/{target_id}/{output_file_name}')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'msu_id_file', help='text file containing the list of MSU accessions to be converted')
    parser.add_argument(
        'mapping_file', help="pickled dictionary mapping the MSU accessions to the target IDs")
    parser.add_argument(
        'output_dir', help='output directory for the file containing the equivalent IDs after conversion')
    parser.add_argument(
        'target_id', help='either "entrez" or "transcript"')
    parser.add_argument(
        '--skip_no_matches', action='store_true', help = 'accessions that cannot be converted will be skipped'
    )

    args = parser.parse_args()

    convert_msu(args.msu_id_file, args.mapping_file,
                args.output_dir, args.target_id, args.skip_no_matches)
