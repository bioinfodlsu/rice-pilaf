class Constants(object):
    DATA = 'static'

    ANNOTATIONS = f'{DATA}/annotations'
    ALIGNMENTS = f'{DATA}/alignments'
    OGI_MAPPING = f'{DATA}/ogi_mapping'

    IGV = f'{DATA}/igv'
    GENOMES_NIPPONBARE = f'{DATA}/genomes/Nipponbare'
    ANNOTATIONS_NB = f'{ANNOTATIONS}/Nb'
    OPEN_CHROMATIN = f'{DATA}/open_chromatin'
    OPEN_CHROMATIN_PANICLE = f'{OPEN_CHROMATIN}/panicle'

    NETWORKS = f'{DATA}/networks'
    NETWORKS_DISPLAY = f'{DATA}/networks_display'
    NETWORKS_DISPLAY_CLUSTERONE = f'{NETWORKS_DISPLAY}/clusterone'
    NETWORKS_DISPLAY_CLUSTERONE_MODULES = f'{NETWORKS_DISPLAY_CLUSTERONE}/modules'

    TEMP = f'{DATA}/temp'
    IMPLICATED_GENES = f'{TEMP}/implicated_genes'

    ENRICHMENT_ANALAYSIS = 'enrichment_analysis'
    ENRICHMENT_ANALYSIS_OUTPUT = f'{ENRICHMENT_ANALAYSIS}/data/output'
    ENRICHMENT_ANALYSIS_OUTPUT_ONTOLOGY = f'{ENRICHMENT_ANALYSIS_OUTPUT}/ontology_enrichment'
    ENRICHMENT_ANALYSIS_OUTPUT_PATHWAY = f'{ENRICHMENT_ANALYSIS_OUTPUT}/pathway_enrichment'
    ORA_ENRICHMENT_ANALYSIS_PROGRAM = f'{ENRICHMENT_ANALAYSIS}/ontology_enrichment/generic-enrichment.r'

    def __init__(self):
        pass
