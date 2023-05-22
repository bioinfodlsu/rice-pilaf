from collections import defaultdict
import os

def main(all_tfbs,out_dir):
    tfbs_intervals = defaultdict(list) #key=TF gene name, values = (chr,start,end)
    all_tfbs_f = open(all_tfbs,"r")
    for gff_record in all_tfbs_f:
        gff_info = gff_record.split("\t")
        chrom = gff_info[0]
        start = gff_info[3]
        end = gff_info[4]
        tf = gff_info[8].split(";")[0].split("=")[1]
        tfbs_intervals[tf].append((chrom,start,end))

    for tf,intervals in tfbs_intervals.items():
        tff_f = open(os.path.join(out_dir,tf),"a")
        for chrom,start,end in intervals:
            tff_f.write("\t".join([chrom,start,end])+"\n")




if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('all_tfbs_gff',help='GFF file containing all TFBS downloaded from PlantTFDB')
    parser.add_argument('out_dir',help='path to output folder where TF-specific interval files will go')

    args= parser.parse_args()
    main(args.all_tfbs_gff, args.out_dir)