import gffutils
from collections import defaultdict


def main(gff_db,upstream_win_len, downstream_win_len, out_file_path):
    promoter_win_len = upstream_win_len + downstream_win_len
    db = gffutils.FeatureDB(gff_db, keep_order=True)
    promoter_sizes = defaultdict(int)
    for gene in db.features_of_type('gene'):
        promoter_sizes[gene.seqid] += promoter_win_len

    with open(out_file_path,"w") as promoter_sizes_f :
        for gene,promoter_size in promoter_sizes.items():
            promoter_sizes_f.write(gene+"\t"+str(promoter_size)+"\n")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('gff_db',help='path to gff db')
    parser.add_argument('upstream_win_len',type=int,help='how many bps upstream of TSS do we search for motifs')
    parser.add_argument('downstream_win_len', type=int,help='how many bps downstream of TSS do we search for motifs')
    parser.add_argument('out_file_path',help='path to output fasta file')

    args= parser.parse_args()
    main(args.gff_db,args.upstream_win_len, args.downstream_win_len,
         args.out_file_path)