# ===========
# CORE LOGIC
# ===========

# Go through each symbol associated with gene
# We use the word "symbol" to refer to the different accession IDs and gene symbols.

# - The symbol should not be "sandwiched" between alphanumeric characters
#   - This is to disambiguate PK1 from PK12
#   - This is also so that PK1 in (PK1) can still be matched

# - The symbol should not be after sp. or spp. (or their variants w/o periods)
#   - This is to disambiguate gene symbols from taxonomic nomenclature

# - If the symbol has 2 letters only, make matching case-sensitive
#   - This is to disambiguate go from GO
#   - Otherwise, make matching case-insensitive

# - If the symbol is an English word, make matching case-sensitive
#   - This is to disambiguate coin from COIN (cold inducible zinc finger protein)
#   - We are using the English word corpus from the NLTK

# - We have to replace some symbols for better disambiguation (based on a manually compiled list)
#   - For now, the only entry is tips. It yielded a lot of false matches with root tips etc.
#   - So we replace tips with TIPS and TIPs

# - We have to exclude some symbols under certain contexts (based on a manually compiled list)
#   - For example, PS is a symbol for some pistilloid-stamen gene.
#     However, PS is more commonly used in literature as an abbreviation for photosystem
#   - Another case is LOG, which is a symbol for lonely guy gene, but can often appear in the context of log <sub>2</sub>
#   - Our disambiguation strategy is as follows:
#     - Let x be the symbol of interest. It should be excluded if it stands for or refers to y.
#     - Let S be the set of symbols for that gene. Let S' = S \ {x} .
#     - If a PubMed article has a match in S', then it is included
#     - If a PubMed article matches x  but the article also contains y, then it is excluded
#     - If a PubMed article matches x and the article does not contain y, then it is included

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

SPECIES_LOOKBEHIND = '(?<!((spp)|(sp)|(spp\.)|(sp\.))\s+)'
ALPHANUMERIC_LOOKBEHIND = '(?<![a-zA-Z0-9])'
ALPHANUMERIC_LOOKAHEAD = '(?![a-zA-Z0-9])'


def perform_single_query(query_string, annotated_abstracts, ignore_case=True, symbol=None):
    df = pd.DataFrame(columns=COLNAMES)

    query_regex = re.compile(query_string, re.IGNORECASE)
    if not ignore_case:
        query_regex = re.compile(query_string)
    print(query_regex)

    pmid_score = defaultdict(lambda: 0)
    with open(annotated_abstracts, 'r', encoding='utf8') as f:
        PMIDs_to_be_skipped = []
        for line in f:
            skip_line = False
            if symbol:
                for context in symbols_to_be_excluded[symbol]:
                    if context.lower() in line.lower():
                        skip_line = True
                        PMIDs_to_be_skipped.append(line.split('\t')[0])
                        break

            if not skip_line:
                if re.search(query_regex, line):
                    try:
                        PMID, _, _, _, _, _, Type, _, _, score = line.split(
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
                                PMID, _, _, _, _, _, Type, _, _, score = line.split(
                                    '\t')
                                break
                            except:
                                pass

                    if Type == 'Gene' and PMID not in PMIDs_to_be_skipped:
                        pmid_score[PMID] = max(pmid_score[PMID], float(score))

    return pmid_score


def construct_query(gene_symbols):
    query_str_ignore_case = ''
    query_str_with_case = ''

    for symbol in gene_symbols:
        if symbol in symbols_to_be_replaced:
            for replacement_symbol in symbols_to_be_replaced[symbol]:
                if len(replacement_symbol) <= 3:
                    query_str_with_case += f'({SPECIES_LOOKBEHIND}({re.escape(replacement_symbol)}))|'
                else:
                    query_str_with_case += f'({re.escape(replacement_symbol)})|'
        else:
            if symbol.lower() in ENG_WORDS or symbol in symbols_to_be_excluded:
                if len(symbol) <= 3:
                    query_str_with_case += f'({SPECIES_LOOKBEHIND}({re.escape(symbol)}))|'
                else:
                    query_str_with_case += f'({re.escape(symbol)})|'
            else:
                if len(symbol) != 2:
                    if len(symbol) <= 3:
                        query_str_ignore_case += f'({SPECIES_LOOKBEHIND}({re.escape(symbol)}))|'
                    else:
                        query_str_ignore_case += f'({re.escape(symbol)})|'
                else:
                    query_str_with_case += f'({SPECIES_LOOKBEHIND}({re.escape(symbol)}))|'

    query_str_ignore_case = query_str_ignore_case[:-1]
    query_str_with_case = query_str_with_case[:-1]

    return query_str_ignore_case, query_str_with_case


def create_pubmed_dict_per_gene(gene_symbols, annotated_abstracts, symbol=None):
    query_str_ignore_case, query_str_with_case = construct_query(gene_symbols)

    pmid_score_ignore_case = None
    pmid_score_with_case = None

    if query_str_ignore_case:
        # Should not be sandwiched between alphanumeric characters
        query_str_ignore_case = f'{ALPHANUMERIC_LOOKBEHIND}({query_str_ignore_case}){ALPHANUMERIC_LOOKAHEAD}'
        pmid_score_ignore_case = perform_single_query(
            query_str_ignore_case, annotated_abstracts, ignore_case=True, symbol=symbol)
    if query_str_with_case:
        # Should not be sandwiched between alphanumeric characters
        query_str_with_case = f'{ALPHANUMERIC_LOOKBEHIND}({query_str_with_case}){ALPHANUMERIC_LOOKAHEAD}'
        pmid_score_with_case = perform_single_query(
            query_str_with_case, annotated_abstracts, ignore_case=False, symbol=symbol)

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

    return pmid_score


def get_pubmed_per_gene(accession, gene_symbols, annotated_abstracts, output_directory):
    pmid_score = create_pubmed_dict_per_gene(gene_symbols, annotated_abstracts)

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
                        get_pubmed_per_gene(accession, gene_symbols + [accession] + iricname + raprepname + rappredname,
                                            annotated_abstracts, output_directory)

                        print(f'Finished parsing entry for {accession}')

    print(f'Finished post-processing handling English gene symbols')


def handle_symbol_replacement(gene_index, annotated_abstracts, output_directory):
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

            is_there_symbol_to_be_replaced = False
            for idx, gene_symbol in enumerate(gene_symbols):
                if gene_symbol in symbols_to_be_replaced:
                    is_there_symbol_to_be_replaced = True

                if gene_symbol.isdigit():
                    # Handle cases like \\OsAMT1,2\\
                    gene_symbols[idx - 1] = gene_symbols[idx -
                                                         1] + ',' + gene_symbol
                    gene_symbols[idx] = ''

                if len(gene_symbol) == 1:
                    gene_symbols[idx] = ''

            if is_there_symbol_to_be_replaced:
                gene_symbols = list(filter(None, gene_symbols))

                for accession in accessions:
                    accession = accession.strip()
                    if accession:
                        get_pubmed_per_gene(accession, gene_symbols + [accession] + iricname + raprepname + rappredname,
                                            annotated_abstracts, output_directory)

                        print(f'Finished parsing entry for {accession}')

    print(f'Finished post-processing handling gene symbols to be replaced')


def handle_symbol_exclusion(gene_index, annotated_abstracts, output_directory):
    # Iterate to see which genes have excluded symbols
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

            is_there_symbol_to_be_excluded = False
            for idx, gene_symbol in enumerate(gene_symbols):
                if gene_symbol in symbols_to_be_excluded:
                    is_there_symbol_to_be_excluded = True

                if gene_symbol.isdigit():
                    # Handle cases like \\OsAMT1,2\\
                    gene_symbols[idx - 1] = gene_symbols[idx -
                                                         1] + ',' + gene_symbol
                    gene_symbols[idx] = ''

                if len(gene_symbol) == 1:
                    gene_symbols[idx] = ''

            if is_there_symbol_to_be_excluded:
                gene_symbols = list(filter(None, gene_symbols))

                for accession in accessions:
                    accession = accession.strip()
                    if accession:
                        get_pubmed_per_gene_with_excluded_symbols(accession, gene_symbols + [accession] + iricname + raprepname + rappredname,
                                                                  annotated_abstracts, output_directory)

                        print(f'Finished parsing entry for {accession}')

    print(f'Finished post-processing handling gene symbols to be excluded')


def get_pubmed_per_gene_with_excluded_symbols(accession, gene_symbols, annotated_abstracts, output_directory):
    # Iterate through every line in annotated abstracts
    # If line matches query without pertinent gene symbol, then include it
    # Else if line matches query with pertinent gene symbol:
    # - If excluded context is present in that line, then exclude it
    # - If excluded context is not present in that line, then include it

    excluded_gene_symbols = []
    included_gene_symbols = []
    for symbol in gene_symbols:
        if symbol in symbols_to_be_excluded:
            excluded_gene_symbols.append(symbol)
        else:
            included_gene_symbols.append(symbol)

    pmid_scores = []
    pmid_scores.append(create_pubmed_dict_per_gene(
        included_gene_symbols, annotated_abstracts))

    for symbol in excluded_gene_symbols:
        pmid_scores.append(create_pubmed_dict_per_gene(
            [symbol], annotated_abstracts, symbol))

    pmid_score = pmid_scores[0]
    for pmid_score_dict in pmid_scores[1:]:
        for pmid, score in pmid_score_dict.items():
            if pmid in pmid_score:
                pmid_score[pmid] = max(pmid_score[pmid], score)
            else:
                pmid_score[pmid] = score

    if pmid_score:
        with open(f'{output_directory}/{accession}.pickle', 'wb') as f:
            pickle.dump(pmid_score, f, protocol=pickle.HIGHEST_PROTOCOL)


def handle_symbol_after_species(gene_index, annotated_abstracts, output_directory):
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

            is_there_symbol_to_be_processed = False
            for idx, gene_symbol in enumerate(gene_symbols):
                if 0 < len(gene_symbol.strip()) and len(gene_symbol.strip()) <= 3:
                    is_there_symbol_to_be_processed = True

                if gene_symbol.isdigit():
                    # Handle cases like \\OsAMT1,2\\
                    gene_symbols[idx - 1] = gene_symbols[idx -
                                                         1] + ',' + gene_symbol
                    gene_symbols[idx] = ''

                if len(gene_symbol) == 1:
                    gene_symbols[idx] = ''

            if is_there_symbol_to_be_processed:
                gene_symbols = list(filter(None, gene_symbols))

                for accession in accessions:
                    accession = accession.strip()
                    if accession:
                        get_pubmed_per_gene(accession, gene_symbols + [accession] + iricname + raprepname + rappredname,
                                            annotated_abstracts, output_directory)

                        print(f'Finished parsing entry for {accession}')

    print(f'Finished post-processing handling gene symbols after sp., spp., sp, and spp')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'gene_index_file', help='file containing gene accessions and their common names')
    parser.add_argument(
        'annotated_abstracts_file',
        help='file containing the annotated abstracts')
    parser.add_argument(
        'symbol_replacement_file',
        help='file containing the replacement for selected symbols'
    )
    parser.add_argument(
        'symbol_exclusion_file',
        help='file containing the symbols that must be excluded under certain contexts'
    )
    parser.add_argument(
        'output_dir', help='output directory for the dictionaries with the PubMed IDs of related articles')

    args = parser.parse_args()

    with open(args.symbol_replacement_file) as f:
        symbols_to_be_replaced = {}
        csv_reader_e = csv.reader(f, delimiter='\t')
        for line in csv_reader_e:
            symbol = line[0]
            replacement = line[1].strip().split(',')
            symbols_to_be_replaced[symbol] = replacement

    with open(args.symbol_exclusion_file) as f:
        symbols_to_be_excluded = {}
        csv_reader_e = csv.reader(f, delimiter='\t')
        for line in csv_reader_e:
            symbol = line[0]
            context = line[1].strip().split(',')
            symbols_to_be_excluded[symbol] = context

    get_pubmed_for_all_genes(args.gene_index_file,
                             args.annotated_abstracts_file, args.output_dir)

    handle_symbol_after_species(args.gene_index_file,
                                args.annotated_abstracts_file, args.output_dir)

    handle_english_symbols(args.gene_index_file,
                           args.annotated_abstracts_file, args.output_dir)

    handle_symbol_replacement(args.gene_index_file,
                              args.annotated_abstracts_file, args.output_dir)

    handle_symbol_exclusion(args.gene_index_file,
                            args.annotated_abstracts_file, args.output_dir)
