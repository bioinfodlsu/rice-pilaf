from collections import defaultdict
import os

chrom_name_map = {
    'Chr1':'Chr01',
    'Chr2':'Chr02',
    'Chr3':'Chr03',
    'Chr4':'Chr04',
    'Chr5':'Chr05',
    'Chr6':'Chr06',
    'Chr7':'Chr07',
    'Chr8':'Chr08',
    'Chr9':'Chr09',
    'Chr10':'Chr10',
    'Chr11':'Chr11',
    'Chr12':'Chr12',
    'ChrSy':'ChrSy',
    'ChrUn':'ChrUn'
}

def main(all_tfbs,out_dir):
    if not os.path.exists(os.path.join(out_dir,"intervals")):
        os.makedirs(os.path.join(out_dir,"intervals"))
    if not os.path.exists(os.path.join(out_dir,"gffs")):
        os.makedirs(os.path.join(out_dir, "gffs"))

    tfbs_intervals = defaultdict(list) #key=TF gene name, values = (chr,start,end)
    tfbs_gff = defaultdict(list)#key=TF gene name, values = gff line
    with open(all_tfbs,"r") as all_tfbs_f:
        for gff_record in all_tfbs_f:
            gff_info = gff_record.split("\t")
            chrom = gff_info[0]
            start = gff_info[3]
            end = gff_info[4]
            tf = gff_info[8].split(";")[0].split("=")[1]
            #as interval
            tfbs_intervals[tf].append((chrom,start,end))
            #as gff
            gff_info[0] = chrom_name_map[chrom]
            gff_record_chrom_name_modified = "\t".join(gff_info)
            tfbs_gff[tf].append(gff_record_chrom_name_modified)

    for tf,intervals in tfbs_intervals.items():
        with open(os.path.join(out_dir,"intervals",tf),"w") as tff_interval_f:
            for chrom,start,end in intervals:
                tff_interval_f.write(f"{chrom_name_map[chrom]}\t{start}\t{end}\n")
                #tff_interval_f.write("\t".join([chrom,start,end])+"\n")

    for tf,gff_records in tfbs_gff.items():
        with open(os.path.join(out_dir,"gffs",tf+str(".gff")),"w") as tff_gff_f:
            tff_gff_f.writelines(gff_records)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('all_tfbs_gff',help='GFF file containing all TFBS downloaded from PlantTFDB')
    parser.add_argument('out_dir',help='path to output folder where TF-specific interval and gff files will go')

    args= parser.parse_args()
    main(args.all_tfbs_gff, args.out_dir)