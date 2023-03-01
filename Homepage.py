import streamlit as st
import gffutils
import pandas as pd
import subprocess
from collections import namedtuple

st.title("Rice Pilaf")
st.markdown(
"Welcome ! Rice Pilaf is short for Rice Post-GWAS Dashboard. "
"Ok, we are not good at abbreviations, but like a good pilaf, this dashboard combines many ingredients. "
"With this tool, you can do amazing things like ... (write me)"
)

#globally defined classes
Genomic_interval = namedtuple('Genomic_interval',['chrom','start','stop'])

#convert 'Chr01:10000-25000' to a Genomic_Interval named tuple
def to_genomic_interval(interval_str):
    chrom,interval=interval_str.split(":")
    start,stop = interval.split("-")
    start = int(start)
    stop = int(stop)
    return Genomic_interval(chrom,start,stop)

#helper functions
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
    return pd.concat(dfs)

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
    return pd.concat(dfs)




#for user input
with st.form("gwas_loci_input"):
    Nb_intervals_str = st.text_input("Provide genomic interval(s) from your GWAS:",
                       value='Chr01:10000-20000;Chr01:22000-25000'
                       )
    #N22 = st.checkbox("N22")
    #MH63 = st.checkbox("MH63"})
    other_ref_genomes = ['N22','MH63']
    other_refs = st.multiselect(
        'Search homologous regions of the following genomes:',
        other_ref_genomes,
        default = other_ref_genomes
    )

    submitted = st.form_submit_button("Submit")

#action begins here
#keep all layout related code here(?)
if submitted:

    st.text("You submitted the Nipponbare genomic interval(s) {}".format(Nb_intervals_str))
    st.text("The tabs below show a list of genes in Nipponbare and in homologous regions of the other references you chose")

    #parse input interval string
    Nb_intervals = []
    for interval_str in Nb_intervals_str.split(";"):
        Nb_intervals.append(to_genomic_interval(interval_str))

    tabs = st.tabs(['Nb']+other_refs)


    df_Nb = get_genes_from_Nb(Nb_intervals)
    tabs[0].text("Genes overlapping the site in the Nipponbare reference")
    tabs[0].dataframe(df_Nb)


    for i,other_ref in enumerate(other_refs):
        tabs[i+1].text("Genes from homologous regions in {}".format(other_ref))
        tabs[i+1].dataframe(get_genes_from_other_ref(other_ref,Nb_intervals))
