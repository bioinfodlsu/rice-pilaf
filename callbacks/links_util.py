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


def construct_link(link, text, dash=False):
    if dash:
        return dcc.Link([
            text, LINK_ICON_DASH],
            href=link,
            target='_blank'
        )

    # Do not use formatted strings since some functions operate on Series
    return A_HREF + link + CLOSE_A_HREF + text + LINK_ICON


def get_genes_from_kegg_link(link):
    idx = link.find('?')
    query = link[idx:].split('+')

    return '\n'.join(query[1:])


def get_kegg_link(result, id_col, genes_col):
    LINK = 'http://www.genome.jp/kegg-bin/show_pathway?' + \
        result[id_col] + '+' + result[genes_col].str.split('\n').str.join('+')
    return construct_link(LINK, result[id_col])


def get_go_link(result, id_col):
    LINK = 'https://amigo.geneontology.org/amigo/term/' + result[id_col]
    return construct_link(LINK, result[id_col])


def get_to_po_link(result, id_col):
    LINK = 'https://www.ebi.ac.uk/ols4/ontologies/to/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252F' + \
        result[id_col].str.replace(':', '_')
    return construct_link(LINK, result[id_col])


def get_uniprot_link(result, id_col):
    LINK = 'https://www.uniprot.org/uniprotkb/' + result[id_col] + '/entry'
    return construct_link(LINK, result[id_col])


def get_uniprot_link_single_str(id, dash=False):
    LINK = 'https://www.uniprot.org/uniprotkb/' + id + '/entry'
    return construct_link(LINK, id, dash)


def get_pubmed_link(result, id_col):
    LINK = 'https://pubmed.ncbi.nlm.nih.gov/' + result[id_col] + '/entry'
    return construct_link(LINK, result[id_col])


def get_doi_link_single_str(doi, dash=False):
    LINK = 'https://doi.org/' + doi
    return construct_link(LINK, doi, dash)


def get_pubmed_link_single_str(pubmed, dash=False):
    LINK = 'https://pubmed.ncbi.nlm.nih.gov/' + \
        pubmed + '/entry'
    return construct_link(LINK, pubmed, dash)


def get_rgi_genecard_link_single_str(accession, dash=False):
    LINK = 'https://riceome.hzau.edu.cn/genecard/' + accession
    return construct_link(LINK, accession, dash)


def get_rgi_genecard_link(result, id_col):
    LINK = 'https://riceome.hzau.edu.cn/genecard/' + result[id_col]
    return construct_link(LINK, result[id_col])


def get_msu_browser_link_single_str(accession, dash=False):
    LINK = 'http://rice.uga.edu/cgi-bin/gbrowse/rice/?name=' + accession
    return construct_link(LINK, accession, dash)


def get_msu_browser_link(result, id_col):
    LINK = 'http://rice.uga.edu/cgi-bin/gbrowse/rice/?name=' + result[id_col]
    return construct_link(LINK, result[id_col])


def get_rgi_orthogroup_link_single_str(accession, dash=False):
    LINK = 'https://riceome.hzau.edu.cn/orthogroup/' + accession
    return construct_link(LINK, accession, dash)


def get_rgi_orthogroup_link(result, id_col):
    LINK = 'https://riceome.hzau.edu.cn/orthogroup/' + result[id_col]
    return construct_link(LINK, result[id_col])


def get_interpro_link_single_str(term, id, dash=False):
    LINK = 'https://www.ebi.ac.uk/interpro/entry/InterPro/' + id
    return construct_link(LINK, term, dash)


def get_pfam_link_single_str(term, id, dash=False):
    LINK = 'https://www.ebi.ac.uk/interpro/entry/pfam/' + id
    return construct_link(LINK, term, dash)


def get_rapdb_single_str(id, dash=False):
    LINK = 'https://ensembl.gramene.org/Oryza_sativa/Gene/Summary?db=core;g=' + id
    return construct_link(LINK, id, dash)


def get_gramene_transcript_single_str(id):
    LINK = 'https://ensembl.gramene.org/Oryza_sativa/Gene/Summary?db=core;t=' + id
    return construct_link(LINK, id)
