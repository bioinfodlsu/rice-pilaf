import subprocess
import pandas as pd

def create_empty_df():
    return pd.DataFrame({
        'Transcription Factor': ['-'],
        'p-value': ['-'],
        'adj. p-value': ['-']
    })

def perform_enrichment_all_tf(tf_set,gwas_loci):
    return create_empty_df()
    #for each tf in tf_set:
    #     perform_enrichment_specific_tf(tf,gwas_loci)
    # multiple_testing_correction()
    # return result_table

def perform_enrichment_specific_tf(tf,gwas_loci):
    pass
    #subprocess.run()



def multiple_testing_correction():
    pass