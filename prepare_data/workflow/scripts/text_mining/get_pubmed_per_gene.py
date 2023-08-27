from nltk.corpus import words
import pandas as pd
import os
import regex as re
import csv
import pickle

from collections import defaultdict

import nltk
nltk.download('words')

ENG_WORDS = set(words.words())

COLNAMES = ['Gene', 'PMID', 'Title', 'Sentence', 'Score']


def perform_single_query(query_string, annotated_abstracts, ignore_case=True):
    df = pd.DataFrame(columns=COLNAMES)

    query_regex = re.compile(query_string, re.IGNORECASE)
    if not ignore_case:
        query_regex = re.compile(query_string)
    print(query_regex)

    pmid_score = defaultdict(lambda: 0)
    with open(annotated_abstracts, 'r', encoding='utf8') as f:
        for line in f:
            if re.search(query_regex, line):
                try:
                    PMID, _, _, _, Entity, _, Type, _, _, score = line.split(
                        '\t')
                except Exception as e:
                    while True:
                        # Sometimes there is a newline in the abstract, which causes a literal line break
                        # in the CSV file
                        prev_line = line
                        try:
                            next_line = next(f)
                            line = prev_line.strip() + ' ' + next_line.strip()
                        except StopIteration:
                            break

                        try:
                            PMID, _, _, _, Entity, _, Type, _, _, score = line.split(
                                '\t')
                            break
                        except:
                            pass

                if Type == 'Gene':
                    pmid_score[PMID] = max(pmid_score[PMID], float(score))

    return pmid_score


def get_pubmed_per_gene(accession, gene_symbols, annotated_abstracts, output_directory):
    query_str_ignore_case = ''
    query_str_with_case = ''

    for symbol in gene_symbols:
        if len(symbol) != 2:
            query_str_ignore_case += f'({re.escape(symbol)})|'
        else:
            query_str_with_case += f'({re.escape(symbol)})|'

    query_str_ignore_case = query_str_ignore_case[:-1]
    query_str_with_case = query_str_with_case[:-1]

    pmid_score_ignore_case = None
    pmid_score_with_case = None

    if query_str_ignore_case:
        # Should not be sandwiched between alphanumeric characters
        query_str_ignore_case = f'(?<![a-zA-Z0-9])({query_str_ignore_case})(?![a-zA-Z0-9])'
        pmid_score_ignore_case = perform_single_query(
            query_str_ignore_case, annotated_abstracts, ignore_case=True)
    if query_str_with_case:
        # Should not be sandwiched between alphanumeric characters
        query_str_with_case = f'(?<![a-zA-Z0-9])({query_str_with_case})(?![a-zA-Z0-9])'
        pmid_score_with_case = perform_single_query(
            query_str_with_case, annotated_abstracts, ignore_case=False)

    pmid_score = {}
    if pmid_score_ignore_case:
        for pmid, score in pmid_score_ignore_case.items():
            pmid_score[pmid] = score

    if pmid_score_with_case:
        for pmid, score in pmid_score_with_case.items():
            if pmid in pmid_score:
                pmid_score[pmid] = max(pmid_score[pmid], score)
            else:
                pmid_score[pmid] = score

    if pmid_score:
        with open(f'{output_directory}/{accession}.pickle', 'wb') as f:
            pickle.dump(pmid_score, f, protocol=pickle.HIGHEST_PROTOCOL)


def get_pubmed_per_gene_english_sensitive(accession, gene_symbols, annotated_abstracts, output_directory):
    query_str_ignore_case = ''
    query_str_with_case = ''

    for symbol in gene_symbols:
        # English words should be case-sensitive (so that 'map' will be disambiguated from 'MAP')
        if symbol.lower() in ENG_WORDS:
            query_str_with_case += f'({re.escape(symbol)})|'
        else:
            if len(symbol) != 2:
                query_str_ignore_case += f'({re.escape(symbol)})|'
            else:
                query_str_with_case += f'({re.escape(symbol)})|'

    query_str_ignore_case = query_str_ignore_case[:-1]
    query_str_with_case = query_str_with_case[:-1]

    pmid_score_ignore_case = None
    pmid_score_with_case = None

    if query_str_ignore_case:
        # Should not be sandwiched between alphanumeric characters
        query_str_ignore_case = f'(?<![a-zA-Z0-9])({query_str_ignore_case})(?![a-zA-Z0-9])'
        pmid_score_ignore_case = perform_single_query(
            query_str_ignore_case, annotated_abstracts, ignore_case=True)
    if query_str_with_case:
        # Should not be sandwiched between alphanumeric characters
        query_str_with_case = f'(?<![a-zA-Z0-9])({query_str_with_case})(?![a-zA-Z0-9])'
        pmid_score_with_case = perform_single_query(
            query_str_with_case, annotated_abstracts, ignore_case=False)

    pmid_score = {}
    if pmid_score_ignore_case:
        for pmid, score in pmid_score_ignore_case.items():
            pmid_score[pmid] = score

    if pmid_score_with_case:
        for pmid, score in pmid_score_with_case.items():
            if pmid in pmid_score:
                pmid_score[pmid] = max(pmid_score[pmid], score)
            else:
                pmid_score[pmid] = score

    if pmid_score:
        with open(f'{output_directory}/{accession}.pickle', 'wb') as f:
            pickle.dump(pmid_score, f, protocol=pickle.HIGHEST_PROTOCOL)


def get_pubmed_for_all_genes(gene_index, annotated_abstracts, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(gene_index, encoding='utf8') as f:
        csv_reader = csv.reader(f, delimiter=',')
        next(csv_reader)

        for line in csv_reader:
            iricname = list(filter(None, line[1].strip().split(',')))
            raprepname = list(filter(None, line[3].strip().split(',')))
            rappredname = list(filter(None, line[4].strip().split(',')))

            # Some entries in the accession column consist of multiple accessions
            accessions = line[2].split(',')
            # Remove the opening and closing brackets
            gene_symbols = line[-1][1:-1].split(',')
            gene_symbols = [gene_symbol.replace('"', '').replace(
                "'", '').replace('\\', '').strip() for gene_symbol in gene_symbols]

            for idx, gene_symbol in enumerate(gene_symbols):
                if gene_symbol.isdigit():
                    # Handle cases like \\OsAMT1,2\\
                    gene_symbols[idx - 1] = gene_symbols[idx -
                                                         1] + ',' + gene_symbol
                    gene_symbols[idx] = ''

                if len(gene_symbol) == 1:
                    gene_symbols[idx] = ''

            gene_symbols = list(filter(None, gene_symbols))

            for accession in accessions:
                accession = accession.strip()
                if accession:
                    get_pubmed_per_gene(accession, gene_symbols + [accession] + iricname + raprepname + rappredname,
                                        annotated_abstracts, output_directory)

                    print(f'Finished parsing entry for {accession}')

    print(f'Finished populating {output_directory}')

# ================
# POST-PROCESSING
# ================


def handle_english_symbols(gene_index, annotated_abstracts, output_directory):
    with open(gene_index, encoding='utf8') as f:
        csv_reader = csv.reader(f, delimiter=',')
        next(csv_reader)

        for line in csv_reader:
            iricname = list(filter(None, line[1].strip().split(',')))
            raprepname = list(filter(None, line[3].strip().split(',')))
            rappredname = list(filter(None, line[4].strip().split(',')))

            # Some entries in the accession column consist of multiple accessions
            accessions = line[2].split(',')
            # Remove the opening and closing brackets
            gene_symbols = line[-1][1:-1].split(',')
            gene_symbols = [gene_symbol.replace('"', '').replace(
                "'", '').replace('\\', '').strip() for gene_symbol in gene_symbols]

            is_there_english_symbol = False
            for idx, gene_symbol in enumerate(gene_symbols):
                if gene_symbol.lower() in ENG_WORDS:
                    is_there_english_symbol = True

                if gene_symbol.isdigit():
                    # Handle cases like \\OsAMT1,2\\
                    gene_symbols[idx - 1] = gene_symbols[idx -
                                                         1] + ',' + gene_symbol
                    gene_symbols[idx] = ''

                if len(gene_symbol) == 1:
                    gene_symbols[idx] = ''

            if is_there_english_symbol:
                gene_symbols = list(filter(None, gene_symbols))

                for accession in accessions:
                    accession = accession.strip()
                    if accession:
                        get_pubmed_per_gene_english_sensitive(accession, gene_symbols + [accession] + iricname + raprepname + rappredname,
                                                              annotated_abstracts, output_directory)

                        print(f'Finished parsing entry for {accession}')

    print(f'Finished post-processing handling English gene symbols')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'gene_index_file', help='file containing gene accessions and their common names')
    parser.add_argument(
        'annotated_abstracts_file',
        help='file containing the annotated abstracts')
    parser.add_argument(
        'output_dir', help='output directory for the dictionary resulting from preprocessing the QTARO annotation file')

    args = parser.parse_args()

    # get_pubmed_for_all_genes(args.gene_index_file,
    #                          args.annotated_abstracts_file, args.output_dir)

    handle_english_symbols(args.gene_index_file,
                           args.annotated_abstracts_file, args.output_dir)
