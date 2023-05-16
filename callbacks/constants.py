class Constants(object):
    DATA = 'static'

    ANNOTATIONS = f'{DATA}/annotations'
    ALIGNMENTS = f'{DATA}/alignments'
    OGI_MAPPING = f'{DATA}/ogi_mapping'
    IGV = f'{DATA}/igv'
    GENOMES_NIPPONBARE = f'{DATA}/genomes/Nipponbare'
    ANNOTATIONS_NB = f'{ANNOTATIONS}/Nb'
    TEMP = f'{DATA}/temp'
    OPEN_CHROMATIN = f'{DATA}/open_chromatin'
    OPEN_CHROMATIN_PANICLE = f'{OPEN_CHROMATIN}/panicle'

    def __init__(self):
        pass
