import gffutils

def main(input_gff,output_gff_db):
    db = gffutils.create_db(input_gff, output_gff_db,merge_strategy="warning")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input_gff',help='input GFF file')
    parser.add_argument('output_gff_db',help='output GFF index file')

    args= parser.parse_args()
    main(args.input_gff, args.output_gff_db)