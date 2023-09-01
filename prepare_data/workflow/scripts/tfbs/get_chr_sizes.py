from Bio import SeqIO

def main(reference,out_file_path):
    ref_fasta = open(reference,'r')
    out_file = open(out_file_path,'w')
    for rec in SeqIO.parse(ref_fasta,'fasta'):
        name = rec.id
        seq = rec.seq
        seq_len = len(rec)
        out_file.write(name+"\t"+str(seq_len)+"\n")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('reference',help='Nipponbare ref')
    parser.add_argument('out_file_path',help='path to file to write chrom name and sizes')

    args= parser.parse_args()
    main(args.reference, args.out_file_path)