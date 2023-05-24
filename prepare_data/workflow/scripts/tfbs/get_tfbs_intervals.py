from collections import defaultdict
import os

def main(all_tfbs,out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    tfbs_intervals = defaultdict(list) #key=TF gene name, values = (chr,start,end)
    tfbs_gff = defaultdict(list)#key=TF gene name, values = gff line
    all_tfbs_f = open(all_tfbs,"r")
    for gff_record in all_tfbs_f:
        gff_info = gff_record.split("\t")
        chrom = gff_info[0]
        start = gff_info[3]
        end = gff_info[4]
        tf = gff_info[8].split(";")[0].split("=")[1]
        tfbs_intervals[tf].append((chrom,start,end))
        tfbs_gff[tf].append(gff_record)

    for tf,intervals in tfbs_intervals.items():
        tff_interval_f = open(os.path.join(out_dir,tf+str("_intervals")),"w")
        for chrom,start,end in intervals:
            tff_interval_f.write("\t".join([chrom,start,end])+"\n")
    for tf,gff_records in tfbs_gff.items():
        tff_gff_f = open(os.path.join(out_dir,tf+str(".gff")),"w")
        tff_gff_f.writelines(gff_records)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('all_tfbs_gff',help='GFF file containing all TFBS downloaded from PlantTFDB')
    parser.add_argument('out_dir',help='path to output folder where TF-specific interval and gff files will go')

    args= parser.parse_args()
    main(args.all_tfbs_gff, args.out_dir)