A_HREF = '<a style="white-space:nowrap" target = "_blank" href="'
CLOSE_A_HREF = '">'
LINK_ICON = '&nbsp;&nbsp;<i class="fa-solid fa-up-right-from-square fa-2xs"></i></a>'


def get_genes_from_kegg_link(link):
    idx = link.find('?')
    query = link[idx:].split('+')

    return '\n'.join(query[1:])


def get_kegg_link(result, id_col, genes_col):
    return A_HREF + 'http://www.genome.jp/kegg-bin/show_pathway?' + \
        result[id_col] + '+' + result[genes_col].str.split('\n').str.join('+') + \
        CLOSE_A_HREF + result[id_col] + LINK_ICON


def get_go_link(result, id_col):
    return A_HREF + 'https://amigo.geneontology.org/amigo/term/' + \
        result[id_col] + \
        CLOSE_A_HREF + result[id_col] + LINK_ICON


def get_to_po_link(result, id_col):
    return A_HREF + 'https://www.ebi.ac.uk/ols4/ontologies/to/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252F' + \
        result[id_col].str.replace(':', '_') + \
        CLOSE_A_HREF + result[id_col] + LINK_ICON


def get_uniprot_link(result, id_col):
    return A_HREF + 'https://www.uniprot.org/uniprotkb/' + \
        result[id_col] + '/entry' + CLOSE_A_HREF + \
        result[id_col] + LINK_ICON


def get_pubmed_link(result, id_col):
    return A_HREF + 'https://pubmed.ncbi.nlm.nih.gov/' + \
        result[id_col] + '/entry' + CLOSE_A_HREF + \
        result[id_col] + LINK_ICON


def get_doi_link_single_str(doi):
    return A_HREF + 'https://doi.org/' + doi + CLOSE_A_HREF + doi + LINK_ICON
