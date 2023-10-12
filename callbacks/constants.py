class Constants(object):
    LABEL_INTRO = 'intro'
    LABEL_LIFT_OVER = 'lift-over'
    LABEL_COEXPRESSION = 'co-expression'
    LABEL_TFBS = 'tfbs'
    LABEL_IGV = 'browse-loci'
    LABEL_TEXT_MINING = 'text-mining'

    DATA = 'static'
    APP_DATA = f'{DATA}/app_data'
    RAW_DATA = f'{DATA}/raw_data'

    ANNOTATIONS = f'{APP_DATA}/annotations'
    ALIGNMENTS = f'{APP_DATA}/alignments'
    GENE_DESCRIPTIONS = f'{APP_DATA}/gene_descriptions'
    TEXT_MINING = f'{APP_DATA}/text_mining'
    QTARO = f'{APP_DATA}/qtaro'
    IRIC = f'{APP_DATA}/iric_data'

    GENE_ID_MAPPING = f'{APP_DATA}/gene_id_mapping'
    MSU_MAPPING = f'{GENE_ID_MAPPING}/msu_mapping'
    OGI_MAPPING = f'{GENE_ID_MAPPING}/ogi_mapping'
    NB_MAPPING = f'{GENE_ID_MAPPING}/nb_mapping'
    IRIC_MAPPING = f'{GENE_ID_MAPPING}/iric_mapping'

    GENOMES_NIPPONBARE = f'{APP_DATA}/genomes/Nipponbare'
    ANNOTATIONS_NB = f'{ANNOTATIONS}/Nb'
    # OPEN_CHROMATIN = f'{APP_DATA}/open_chromatin'
    # OPEN_CHROMATIN_PANICLE = f'{OPEN_CHROMATIN}/panicle'
    EPIGENOME = f'{APP_DATA}/epigenomic'
    QTARO_DICTIONARY = f'{QTARO}/qtaro.pickle'

    NETWORKS = f'{APP_DATA}/networks'
    NETWORK_MODULES = f'{APP_DATA}/network_modules'

    TEMP = f'{DATA}/temp'
    TEMP_LIFT_OVER = 'lift_over'
    TEMP_IGV = 'igv'
    TEMP_COEXPRESSION = 'co_expression'
    TEMP_TEXT_MINING = 'text_mining'

    TEMP_TFBS = 'tf_enrichment'
    TFBS_BEDS = f'{APP_DATA}/tf_enrichment'
    PROMOTER_BED = 'query_promoter_intervals'
    GENOME_WIDE_BED = 'query_genomic_intervals'
    TFBS_ANNOTATION = f'{TFBS_BEDS}/annotation'

    ENRICHMENT_ANALYSIS = f'{APP_DATA}/enrichment_analysis'
    ENRICHMENT_ANALYSIS_MAPPING = 'mapping'

    KEGG_DOSA_GENESET = f'{ENRICHMENT_ANALYSIS_MAPPING}/kegg-dosa-geneset.pickle'
    KEGG_DOSA_PATHWAY_NAMES = f'{ENRICHMENT_ANALYSIS_MAPPING}/kegg-dosa-pathway-names.tsv'

    TEXT_MINING_ANNOTATED_ABSTRACTS = f'{TEXT_MINING}/annotated_abstracts.tsv'
    TEXT_MINING_PUBMED = f'{TEXT_MINING}/pubmed_per_gene.pickle'

    P_VALUE_CUTOFF = 0.05

    # =========
    # Database
    # =========

    FILE_STATUS_DB = f'{TEMP}/file_status.db'
    FILE_STATUS_TABLE = 'file_status'

    # ==============================
    # INTRO TEXT FOR ANALYSIS PAGES
    # ==============================

    INTRO_LIFT_OVER = 'In this page, you can obtain the list of genes overlapping your input intervals. Optionally, you can choose genomes to lift-over your Nipponbare coordinates to.'
    INTRO_TEXT_MINING = 'In this page, you can retrieve gene names associated with traits, diseases, and chemicals, among others, from a database constructed from text-mined PubMed abstracts.'
    INTRO_COEXPRESSION = 'In this page, you can search for modules (communities or clusters) in rice co-expression networks, which are significantly enriched in the genes implicated by your GWAS. Likely functions of the modules are inferred by enrichment analysis against several ontologies and pathway databases.'
    INTRO_TFBS = 'In this page, you can search for transcription factors whose binding sites overlap significantly with your intervals,the idea being that your intervals might contain variants that affect the binding affinity of transcription factors.'
    INTRO_EPIGENOME = 'In this page, you can genome-browse your loci and overlay epigenomic information such as chromatin accessibility and histone modification marks.'

    def __init__(self):
        pass
