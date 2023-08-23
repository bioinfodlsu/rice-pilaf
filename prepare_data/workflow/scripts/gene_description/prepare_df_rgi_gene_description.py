import pandas as pd


def main(annotation_file, out_csv):

    gene_description_df = pd.DataFrame(
        columns=('Gene_ID', 'Description', 'UniProtKB/Swiss-Prot'))

    with open(annotation_file, 'r') as f:
        for i, line in enumerate(f):
            gene_ID, remaining = line.rstrip().split("\t")
            description, UniProt_ID = remaining.split(
                "[UniProtKB/Swiss-Prot:")
            description = description.rstrip()
            UniProt_ID = UniProt_ID.rstrip("]")
            gene_description_df.loc[i] = [gene_ID, description, UniProt_ID]

    gene_description_df.to_csv(out_csv, index=False)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('annotation_file', help='ann file from RGI')
    parser.add_argument('out_csv', help='path to output csv file')

    args = parser.parse_args()
    main(args.annotation_file, args.out_csv)
