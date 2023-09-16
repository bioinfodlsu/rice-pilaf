from dash import dcc, html

A_HREF = '<a target = "_blank" href="'
CLOSE_A_HREF = '">'
LINK_ICON = '<span style="white-space:nowrap">&nbsp;&nbsp;<i class="fa-solid fa-up-right-from-square fa-2xs"></i></span></a>'
LINK_ICON_DASH = html.Span([
    ' ', html.I(
        id='demo-link',
        className='fa-solid fa-up-right-from-square fa-2xs ms-1'
    )], style={'white-space': 'nowrap'}
)


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


def get_doi_link_single_str(doi, dash=False):
    LINK = 'https://doi.org/' + doi
    if dash:
        return dcc.Link([
            doi, LINK_ICON_DASH],
            href=LINK,
            target='_blank'
        )

    return A_HREF + LINK + CLOSE_A_HREF + doi + LINK_ICON


def get_pubmed_link_single_str(pubmed):
    return A_HREF + 'https://pubmed.ncbi.nlm.nih.gov/' + \
        pubmed + '/entry' + CLOSE_A_HREF + \
        pubmed + LINK_ICON


def get_rgi_genecard_link_single_str(accession, dash=False):
    LINK = 'https://riceome.hzau.edu.cn/genecard/' + accession
    if dash:
        return dcc.Link([
            accession, LINK_ICON_DASH],
            href=LINK,
            target='_blank'
        )

    return A_HREF + LINK + CLOSE_A_HREF + accession + LINK_ICON


def get_rgi_genecard_link(result, id_col):
    return A_HREF + 'https://riceome.hzau.edu.cn/genecard/' + result[id_col] + CLOSE_A_HREF + result[id_col] + LINK_ICON


def get_rgi_orthogroup_link_single_str(accession, dash=False):
    LINK = 'https://riceome.hzau.edu.cn/orthogroup/' + accession
    if dash:
        return dcc.Link([
            accession, LINK_ICON_DASH],
            href=LINK,
            target='_blank'
        )

    return A_HREF + LINK + CLOSE_A_HREF + accession + LINK_ICON


def get_rgi_orthogroup_link(result, id_col):
    return A_HREF + 'https://riceome.hzau.edu.cn/orthogroup/' + result[id_col] + CLOSE_A_HREF + result[id_col] + LINK_ICON


def get_interpro_link_single_str(term, id):
    return A_HREF + 'https://www.ebi.ac.uk/interpro/entry/InterPro/' + id + CLOSE_A_HREF + term + LINK_ICON


def get_pfam_link_single_str(term, id):
    return A_HREF + 'https://www.ebi.ac.uk/interpro/entry/pfam/' + id + CLOSE_A_HREF + term + LINK_ICON


def get_rapdb_single_str(id, dash=False):
    LINK = 'https://ensembl.gramene.org/Oryza_sativa/Gene/Summary?db=core;g=' + id
    if dash:
        return dcc.Link([
            id, LINK_ICON_DASH],
            href=LINK,
            target='_blank'
        )

    return A_HREF + LINK + CLOSE_A_HREF + id + LINK_ICON
