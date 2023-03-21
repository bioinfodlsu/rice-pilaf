import dash
from dash import dcc, html, Input, Output, State
import gffutils
import pandas as pd
from collections import namedtuple
import dash_bootstrap_components as dbc

Genomic_interval = namedtuple('Genomic_interval',['chrom','start','stop'])
other_ref_genomes = ['N22','MH63']

genomic_interval = 'Chr01:10000-20000;Chr01:22000-25000'

#convert 'Chr01:10000-25000' to a Genomic_Interval named tuple
def to_genomic_interval(interval_str):
    chrom,interval=interval_str.split(":")
    start,stop = interval.split("-")
    start = int(start)
    stop = int(stop)
    return Genomic_interval(chrom,start,stop)

##getting genes from Nipponbare
def get_genes_from_Nb(Nb_intervals):

    dfs = []
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
    return pd.concat(dfs,ignore_index=True)

##get intervals from other refs that align to (parts) of the input loci
def get_genes_from_other_ref(ref,Nb_intervals):
    db_align = gffutils.FeatureDB("data/alignments/{0}/{0}.1to1.gff.db".format("Nb_"+str(ref)))
    db_annotation = gffutils.FeatureDB("data/annotations/{0}/{0}.gff.db".format(ref))
    #get corresponding intervals on ref
    dfs = []
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
    return pd.concat(dfs,ignore_index=True)

dash.register_page(__name__, path ="/", name="Input and Lift-over")

layout = html.Div(
    [
        dcc.Markdown('Provide genomic interval(s) from your GWAS:'),
        dbc.Input(
            type = 'text',
            style = {'width': '100%'},
            value = genomic_interval
        ),

        html.Br(),

        dcc.Markdown('Search homologous regions of the following genomes:'),
        dcc.Dropdown(other_ref_genomes, multi=True),

        html.Br(),

        html.Div(dcc.Input(id='input-on-submit', type='text')),
        dbc.Button('Submit', id='submit-val', n_clicks=0),
        html.Div(id='container-button-basic')
    ]
)




