class Constants(object):
    DATA = 'static'
    APP_DATA = f'{DATA}/app_data'
    RAW_DATA = f'{DATA}/raw_data'

    ANNOTATIONS = f'{APP_DATA}/annotations'
    ALIGNMENTS = f'{APP_DATA}/alignments'
    OGI_MAPPING = f'{APP_DATA}/ogi_mapping'

    GENOMES_NIPPONBARE = f'{APP_DATA}/genomes/Nipponbare'
    ANNOTATIONS_NB = f'{ANNOTATIONS}/Nb'
    OPEN_CHROMATIN = f'{APP_DATA}/open_chromatin'
    OPEN_CHROMATIN_PANICLE = f'{OPEN_CHROMATIN}/panicle'

    NETWORKS = f'{RAW_DATA}/networks'
    NETWORKS_DISPLAY = f'{APP_DATA}/networks_display'
    NETWORKS_DISPLAY_OS_CX = f'{NETWORKS_DISPLAY}/OS-CX'

    TEMP = f'{DATA}/temp'
    IMPLICATED_GENES = f'{TEMP}/implicated_genes'
    TEMP_IGV = f'igv'

    TEMP_TFBS = f'{TEMP}/tf_enrichment'
    TFBS_BEDS = f'{APP_DATA}/tf_enrichment'

    DATA_PREPARATION_SCRIPTS = 'prepare_data/workflow/scripts'
    ENRICHMENT_ANALYSIS_SCRIPTS = f'{DATA_PREPARATION_SCRIPTS}/enrichment_analysis'
    ORA_ENRICHMENT_ANALYSIS_PROGRAM = f'{ENRICHMENT_ANALYSIS_SCRIPTS}/ontology_enrichment/generic-enrichment.r'

    ENRICHMNET_ANALYSIS_DATA = f'{APP_DATA}/enrichment_analysis'
    ENRICHMENT_ANALYSIS_OUTPUT = f'{ENRICHMNET_ANALYSIS_DATA}/output'
    ENRICHMENT_ANALYSIS_MAPPING = f'{ENRICHMNET_ANALYSIS_DATA}/mapping'
    ENRICHMENT_ANALYSIS_MODULES = f'{ENRICHMNET_ANALYSIS_DATA}/modules'

    TRANSCRIPT_TO_MSU_DICT = f'{ENRICHMENT_ANALYSIS_MAPPING}/transcript-to-msu-id.pickle'
    KEGG_DOSA_GENESET = f'{ENRICHMENT_ANALYSIS_MAPPING}/kegg-dosa-geneset.pickle'
    KEGG_DOSA_PATHWAY_NAMES = f'{ENRICHMENT_ANALYSIS_MAPPING}/kegg-dosa-pathway-names.tsv'

    def __init__(self):
        pass
