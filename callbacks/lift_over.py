from dash import dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate

import gffutils
import pandas as pd

from collections import namedtuple

Genomic_interval = namedtuple('Genomic_interval',['chrom','start','stop'])

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


def init_callback(app):
    @app.callback(
        Output('lift-over-results-intro', 'children'),
        Output('lift-over-results-tabs', 'children'),
        Input('lift-over-submit', 'n_clicks'),
        Input('lift-over-other-refs', 'value'),
        Input('lift-over-genomic-intervals', 'value')
    )
    def display_gene_tables(n_clicks, other_refs, nb_intervals_str):
        if n_clicks >= 1:
            tabs = ['NB']
            if other_refs:
                tabs = tabs + other_refs

            tabs_children = [dcc.Tab(label=tab, value=tab) for tab in tabs]

            nb_intervals = []
            for interval_str in nb_intervals_str.split(";"):
                nb_intervals.append(to_genomic_interval(interval_str))

            df_nb = get_genes_from_Nb(nb_intervals)
            # tabs[0].text("Genes overlapping the site in the Nipponbare reference")
            # tabs[0].dataframe(df_nb)


            # for i,other_ref in enumerate(other_refs):
            #     tabs[i+1].text("Genes from homologous regions in {}".format(other_ref))
            #     tabs[i+1].dataframe(get_genes_from_other_ref(other_ref,nb_intervals))


            return 'The tabs below show a list of genes in Nipponbare and in homologous regions of the other references you chose', \
                tabs_children
        
        raise PreventUpdate
    
    # Chain callback for active tab
    @app.callback(
        Output('lift-over-results-tabs', 'active_tab'),
        Input('lift-over-submit', 'n_clicks'),
    )
    def display_tab(n_clicks):
        if n_clicks >= 1:
            return 'tab-0'
        
        raise PreventUpdate
