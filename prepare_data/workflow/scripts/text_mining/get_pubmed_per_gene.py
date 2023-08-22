import pandas as pd
import os
import regex as re
import csv

COLNAMES = ['Gene', 'PMID', 'Title', 'Sentence', 'Score']


def perform_single_query(query_string, annotated_abstracts):
    df = pd.DataFrame(columns=COLNAMES)
    query_regex = re.compile(re.escape(query_string), re.IGNORECASE)
    with open(annotated_abstracts, 'r', encoding='utf8') as f:
        for line in f:
            if re.search(query_regex, line):
                PMID, Title, Sentence, IsInTitle, Entity, Annotations, Type, start_pos, end_pos, score = line.split(
                    '\t')

                if Type == 'Gene':
                    if Sentence == 'None':
                        Sentence = Title
                    df.loc[len(df.index)] = [
                        Entity, PMID, Title, Sentence, score]

    return df


def get_pubmed_per_gene(accession, gene_symbols, annotated_abstracts, output_directory):
    dfs = []
    for symbol in gene_symbols:
        dfs.append(perform_single_query(symbol, annotated_abstracts))

    pubmed_df = pd.concat(dfs, ignore_index=True)
    pubmed_df = pubmed_df.sort_values('Score', ascending=False)

    if not pubmed_df.empty:
        pubmed_df.to_csv(f'{output_directory}/{accession}.csv')


def get_pubmed_for_all_genes(gene_index, annotated_abstracts, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(gene_index, encoding='utf8') as f:
        csv_reader = csv.reader(f, delimiter=',')
        next(csv_reader)

        for line in csv_reader:
            # Some entries in the accession column consist of multiple accessionss
            accessions = line[2].split(',')
            # Remove the opening and closing brackets
            gene_symbols = line[-1][1:-1].split(',')
            gene_symbols = [gene_symbol.replace('"', '').replace(
                "'", '').strip() for gene_symbol in gene_symbols]

            if gene_symbols[0] != '':
                for accession in accessions:
                    if len(accession.strip()) > 0:
                        try:
                            get_pubmed_per_gene(accession, gene_symbols,
                                                annotated_abstracts, output_directory)
                        except:
                            with open(f'{output_directory}/error.txt', 'a') as error:
                                error.write(
                                    f'{accession}\t{",".join(gene_symbols)}\n')

                        print(f'Finished parsing entry for {accession}')

    print(f'Finished populating {output_directory}')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'gene_index_file', help='file containing gene accessions and their common names')
    parser.add_argument('annotated_abstracts_file',
                        help='file containing the annotated abstracts')
    parser.add_argument(
        'output_dir', help='output directory for the dictionary resulting from preprocessing the QTARO annotation file')

    args = parser.parse_args()

    get_pubmed_for_all_genes(args.gene_index_file,
                             args.annotated_abstracts_file, args.output_dir)
