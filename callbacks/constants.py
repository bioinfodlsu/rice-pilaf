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
    TEMP_IGV = f'{TEMP}/igv'

    DATA_PREPARATION_SCRITPS = 'prepare_data/workflow/scripts'
    ENRICHMENT_ANALAYSIS_SCRIPTS = f'{DATA_PREPARATION_SCRITPS}/enrichment_analysis'
    ORA_ENRICHMENT_ANALYSIS_PROGRAM = f'{ENRICHMENT_ANALAYSIS_SCRIPTS}/ontology_enrichment/generic-enrichment.r'
    ENRICHMENT_ANALYSIS_OUTPUT = f'{APP_DATA}/enrichment_analysis/output'
    ENRICHMENT_ANALYSIS_OUTPUT_ONTOLOGY = f'{ENRICHMENT_ANALYSIS_OUTPUT}/ontology_enrichment'
    ENRICHMENT_ANALYSIS_OUTPUT_PATHWAY = f'{ENRICHMENT_ANALYSIS_OUTPUT}/pathway_enrichment'

    def __init__(self):
        pass
