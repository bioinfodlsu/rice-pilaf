class Constants(object):
    LIFT_OVER = 'lift-over'
    COEXPRESSION = 'co-expression'
    TFBS = 'tf-enrichment'
    IGV = 'browse-loci'
    TEXT_MINING = 'text-mining'

    DATA = 'static'
    APP_DATA = f'{DATA}/app_data'
    RAW_DATA = f'{DATA}/raw_data'

    ANNOTATIONS = f'{APP_DATA}/annotations'
    ALIGNMENTS = f'{APP_DATA}/alignments'
    OGI_MAPPING = f'{APP_DATA}/ogi_mapping'
    GENE_DESCRIPTIONS = f'{APP_DATA}/gene_descriptions'
    TEXT_MINING = f'{APP_DATA}/text_mining'
    QTARO = f'{APP_DATA}/qtaro'

    GENOMES_NIPPONBARE = f'{APP_DATA}/genomes/Nipponbare'
    ANNOTATIONS_NB = f'{ANNOTATIONS}/Nb'
    OPEN_CHROMATIN = f'{APP_DATA}/open_chromatin'
    OPEN_CHROMATIN_PANICLE = f'{OPEN_CHROMATIN}/panicle'
    QTARO_DICTIONARY = f'{QTARO}/qtaro.pickle'

    NETWORKS = f'{APP_DATA}/networks'
    NETWORKS_DISPLAY = f'{APP_DATA}/networks_display'
    NETWORKS_MODULES = f'{APP_DATA}/networks_modules'

    TEMP = f'{DATA}/temp'
    IMPLICATED_GENES = f'{TEMP}/implicated_genes'
    TEMP_IGV = 'igv'
    TEMP_COEXPRESSION = 'co_expression'

    TEMP_TFBS = 'tf_enrichment'
    TFBS_BEDS = f'{APP_DATA}/tf_enrichment'
    PROMOTER_BED = 'query_promoter_intervals'
    GENOME_WIDE_BED = 'query_genomic_intervals'

    DATA_PREPARATION_SCRIPTS = 'prepare_data/workflow/scripts'
    ENRICHMENT_ANALYSIS_SCRIPTS = f'{DATA_PREPARATION_SCRIPTS}/enrichment_analysis'
    ORA_ENRICHMENT_ANALYSIS_PROGRAM = f'{ENRICHMENT_ANALYSIS_SCRIPTS}/ontology_enrichment/generic-enrichment.r'

    ENRICHMENT_ANALYSIS = f'{APP_DATA}/enrichment_analysis'
    ENRICHMENT_ANALYSIS_MAPPING = 'mapping'
    ENRICHMENT_ANALYSIS_MODULES = 'modules'

    TRANSCRIPT_TO_MSU_DICT = f'{ENRICHMENT_ANALYSIS_MAPPING}/transcript-to-msu-id.pickle'
    KEGG_DOSA_GENESET = f'{ENRICHMENT_ANALYSIS_MAPPING}/kegg-dosa-geneset.pickle'
    KEGG_DOSA_PATHWAY_NAMES = f'{ENRICHMENT_ANALYSIS_MAPPING}/kegg-dosa-pathway-names.tsv'

    TEXT_MINING_ANNOTATED_ABSTRACTS = f'{TEXT_MINING}/annotated_abstracts.tsv'

    def __init__(self):
        pass
