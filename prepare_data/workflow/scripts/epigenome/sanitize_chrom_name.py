import re

def main(input_file,output_file):
    '''
    Expects chromosome name that looks like chr1 and replaces it by Chr01
    '''
    pattern = r'^[Cc][Hh][Rr][0-1]$|^[Cc][Hh][Rr][0-1][0-9]'
    with open(input_file,'r') as infile, open(output_file,'w') as outfile:
        for line in infile:
            line = line.split("\t")
            chr_name = line[0]
            if re.fullmatch(pattern,chr_name) is not None:
                chr_number = chr_name[3:]
                if len(chr_number) == 1:
                    chr_number = '0'+chr_number
                    chr_name = 'Chr'+chr_number
                    line[0] = chr_name
                outfile.write("\t".join(line))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file',help='bed file with peaks')
    parser.add_argument('output_file', help='output file with chr names consistent with app')

    args= parser.parse_args()
    main(args.input_file, args.output_file)