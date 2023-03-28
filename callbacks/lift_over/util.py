import gffutils
import pandas as pd

from collections import namedtuple

Genomic_interval = namedtuple('Genomic_interval',['chrom','start','stop'])

# Error codes for genomic interval input
NO_CHROM_INTERVAL_SEP = 1
NO_START_STOP_SEP = 2
START_STOP_NOT_INT = 3
START_GREATER_THAN_STOP = 4

# The first element is the error code and the second element is the malformed interval
def is_error(intervals):
    return isinstance(intervals[0], int)

def get_error_message(error_code):
    error_messages = {
        NO_CHROM_INTERVAL_SEP: 'A genomic interval should be entered as chrom:start-end. Use a semicolon (;) to separate multiple intervals',
        NO_START_STOP_SEP: 'Specify a valid start and end for the genomic interval',
        START_STOP_NOT_INT: 'The start and end of a genomic interval should be integers',
        START_GREATER_THAN_STOP: 'The start of a genomic interval should not be past the end'
    }

    return error_messages[error_code]

def sanitize_nb_intervals_str(nb_intervals_str):
    # Remove spaces
    nb_intervals_str = nb_intervals_str.replace(' ', '')

    # Remove trailing semicolons
    nb_intervals_str = nb_intervals_str.rstrip(';')

    return nb_intervals_str


#convert 'Chr01:10000-25000' to a Genomic_Interval named tuple
def to_genomic_interval(interval_str):
    try:
        chrom,interval=interval_str.split(":")
    except ValueError:
        return NO_CHROM_INTERVAL_SEP, interval_str

    try:    
        start,stop = interval.split("-")
    except ValueError:
        return NO_START_STOP_SEP, interval_str

    try:
        start = int(start)
        stop = int(stop)        
    except ValueError:
        return START_STOP_NOT_INT, interval_str
    
    if start > stop:
        return START_GREATER_THAN_STOP, interval_str

    return Genomic_interval(chrom,start,stop)

# Split 'Chr01:10000-25000;;Chr01:22000-25000'
def get_genomic_intervals_from_input(nb_intervals_str):
    nb_intervals_str = sanitize_nb_intervals_str(nb_intervals_str)
    nb_intervals = []
    
    nb_intervals_split = nb_intervals_str.split(";")

    for interval_str in nb_intervals_split:
        interval = to_genomic_interval(interval_str)

        # Check if interval is malformed
        if is_error(interval):
            return interval
        else:
            nb_intervals.append(interval)

    return nb_intervals

##getting genes from Nipponbare
def get_genes_from_Nb(Nb_intervals):

    dfs = []
    if is_error(Nb_intervals):
        Nb_intervals = []

    for Nb_interval in Nb_intervals:
        #load and search GFF_DB of Nipponbare
        db = gffutils.FeatureDB('data/annotations/Nb/IRGSPMSU.gff.db',keep_order=True)
        genes_in_interval = list(db.region(region=(Nb_interval.chrom,Nb_interval.start,Nb_interval.stop),
                                           completely_within=False,featuretype='gene'))

        #TODO should be a better way to do this?
        df = pd.DataFrame({
            'name': [gene.id for gene in genes_in_interval],
            'chrom':[gene.chrom for gene in genes_in_interval],
            'start':[gene.start for gene in genes_in_interval],
            'end':[gene.end for gene in genes_in_interval]
        })
        dfs.append(df)

    # Return empty dataframe if there are no results to concatenate
    try:
        table = pd.concat(dfs,ignore_index=True)
        if table.shape[0] == 0:
            return pd.DataFrame({
                'name': ['-'],
                'chrom': ['-'],
                'start': ['-'],
                'end': ['-']
            })
        
        return table

    except ValueError:
        return pd.DataFrame({
            'name': ['-'],
            'chrom': ['-'],
            'start': ['-'],
            'end': ['-']
        })

##get intervals from other refs that align to (parts) of the input loci
def get_genes_from_other_ref(ref,Nb_intervals):
    db_align = gffutils.FeatureDB("data/alignments/{0}/{0}.1to1.gff.db".format("Nb_"+str(ref)))
    db_annotation = gffutils.FeatureDB("data/annotations/{0}/{0}.gff.db".format(ref))
    #get corresponding intervals on ref
    dfs = []
    if is_error(Nb_intervals):
        Nb_intervals = []
        
    for Nb_interval in Nb_intervals:
        gff_intersections = list(db_align.region(region=(Nb_interval.chrom,Nb_interval.start,Nb_interval.stop),
                                completely_within=False))
        for intersection in gff_intersections:
            ref_interval = to_genomic_interval(intersection.attributes['Name'][0])
            genes_in_interval = list(db_annotation.region(region=(ref_interval.chrom,ref_interval.start,ref_interval.stop),
                                                   completely_within=False,featuretype='gene'))
            df = pd.DataFrame({
                'name': [gene.id for gene in genes_in_interval],
                'chrom':[gene.chrom for gene in genes_in_interval],
                'start':[gene.start for gene in genes_in_interval],
                'end':[gene.end for gene in genes_in_interval]
            })
            dfs.append(df)

    # Return empty dataframe if there are no results to concatenate
    try:
        table = pd.concat(dfs,ignore_index=True)
        if table.shape[0] == 0:
            return pd.DataFrame({
                'name': ['-'],
                'chrom': ['-'],
                'start': ['-'],
                'end': ['-']
            })
        
        return table
    
    except ValueError:
        return pd.DataFrame({
            'name': ['-'],
            'chrom': ['-'],
            'start': ['-'],
            'end': ['-']
        })
