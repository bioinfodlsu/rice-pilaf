import csv
import os
from collections import defaultdict
import pickle


def main(gene_id_table,output_dir):

    rap_to_msu = defaultdict(list)
    symbol_to_msu = defaultdict(list)

    with open(gene_id_table, "r") as f:
        csv_reader = csv.reader(f)
        next(csv_reader)
        for line in csv_reader:
            _, iric, msu, rap, _, _, _, symbols = line

            msu_ids = msu.split(",") #some lines have multiple MSU ids
            rap_ids = rap.split(",") #some have multiple RAP ids.
            symbols_list = symbols.strip('][').split(", ") #gene symbol is written as "['ABC1','DEF2']"

            if len(msu_ids) == len(rap_ids): # if they are same, the map is (maybe) one-to-one
                for i in range(len(rap_ids)):
                    rap_to_msu[rap_ids[i]] = msu_ids[i]
            else:
                for rap_id in rap_ids:
                    for msu_id in msu_ids:
                        rap_to_msu[rap_id] = msu_id


            for symbol in symbols_list:
                symbol = symbol.rstrip("'").lstrip("'") #extraneous single quotes
                for msu_id in msu_ids:
                    symbol_to_msu[symbol] = msu_id

    #write pickle file
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f'{output_dir}/rap_to_msu.pickle', 'wb') as f:
        pickle.dump(rap_to_msu, f, protocol=pickle.HIGHEST_PROTOCOL)

    with open(f'{output_dir}/genesymbol_to_msu.pickle', 'wb') as f:
        pickle.dump(symbol_to_msu, f, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    import argparse
    import csv

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'gene_id_table', help='gene id table')
    parser.add_argument(
        'output_dir', help='output directory for the pickled otherIDs-to-MSUID mapping dictionaries')

    args = parser.parse_args()
    main(args.gene_id_table,args.output_dir)




