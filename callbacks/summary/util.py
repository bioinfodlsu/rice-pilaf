from ..lift_over.util import *
from ..general_util import *
from ..coexpression.util import *
from ..constants import Constants

from collections import defaultdict


def get_liftover_summary(implicated_genes):
    """
    Returns a summary of results of the lift-over analysis

    Parameters:
    - implicated_genes: List of implicated genes

    Returns:
    - Data frame summarizing the results of the lift-over analysis
    """
    
    NB_IDX = 1                  # The Nipponbare IDs are in the second column
    NB_PREFIX = "LOC_Os"

    gene_to_orthologs_map = defaultdict(set)
    for row in implicated_genes:
        if row[NB_IDX].startswith(NB_PREFIX):
            for gene in row:
                if gene != NULL_PLACEHOLDER:
                    gene_to_orthologs_map[row[NB_IDX]].add(gene)

    gene_to_count = []
    for gene, orthologs in gene_to_orthologs_map.items():
        # Subtract 2 to remove OGI and Nipponbare
        gene_to_count.append([gene, len(orthologs) - 2])

    return pd.DataFrame(gene_to_count, columns=["Name", "# Orthologs"])


def get_num_qtl_pubs(qtl_str):
    """
    Returns the number of QTL-related publications given a string containing DOI links

    Parameters:
    - qtl_str: 

    Returns:
    - 
    """

    # Each QTL study has an associated DOI
    return qtl_str.count("doi.org")


def get_num_pubmed_pubs(pubmed_str):
    """
    Returns the number of PubMed publications given a string containing PubMed links
    """

    # Each PubMed study has an associated PubMed link
    return pubmed_str.count("pubmed")


def get_qtl_summary(genomic_intervals):
    genes = get_genes_in_Nb(genomic_intervals)[0]
    genes["# QTL Analyses"] = genes.apply(
        lambda x: get_num_qtl_pubs(x["QTL Analyses"]), axis=1
    )

    return genes[["Name", "# QTL Analyses"]]


def get_pubmed_summary(genomic_intervals):
    genes = get_genes_in_Nb(genomic_intervals)[0]
    genes["# PubMed Article IDs"] = genes.apply(
        lambda x: get_num_pubmed_pubs(x["PubMed Article IDs"]), axis=1
    )

    return genes[["Name", "# PubMed Article IDs"]]


def get_module_indices(modules):
    return [int(module.split(" ")[1]) for module in modules]


def get_ontology_terms_in_module(
    module_idx, enrichment_type, network, algo, parameters
):
    file = f"{Constants.ENRICHMENT_ANALYSIS}/{network}/output/{algo}/{parameters}/ontology_enrichment/{enrichment_type}/results/{enrichment_type}-df-{module_idx}.tsv"
    with open(file) as f:
        # Skip header
        next(f)
        ontology_terms = [line.strip().split("\t")[0] for line in f]

    return set(ontology_terms)


def get_ontology_terms_in_modules(modules, enrichment_type, network, algo, parameters):
    ontology_terms = set()
    for module in modules:
        ontology_terms = ontology_terms.union(
            get_ontology_terms_in_module(
                module, enrichment_type, network, algo, parameters
            )
        )

    return ontology_terms


def get_pathways_in_module(module_idx, tool, network, algo, parameters):
    file = f"{Constants.ENRICHMENT_ANALYSIS}/{network}/output/{algo}/{parameters}/pathway_enrichment/{tool}/results/{tool}-df-{module_idx}.tsv"
    with open(file) as f:
        # Skip header
        next(f)
        if tool == "ora":
            pathways = [line.strip().split("\t")[0] for line in f]
        elif tool == "pe":
            pathways = [line.strip().split("\t")[0][len("path:") :] for line in f]
        elif tool == "spia":
            pathways = ["dosa" + line.strip().split("\t")[2] for line in f]

    return set(pathways)


def get_pathways_in_modules(modules, tool, network, algo, parameters):
    pathways = set()
    for module in modules:
        pathways = pathways.union(
            get_pathways_in_module(module, tool, network, algo, parameters)
        )

    return pathways


def get_coexpression_summary(
    genomic_intervals,
    combined_gene_ids,
    submitted_addl_genes,
    network,
    algo,
    parameters,
):
    enriched_modules = get_module_indices(
        do_module_enrichment_analysis(
            combined_gene_ids,
            genomic_intervals,
            submitted_addl_genes,
            network,
            algo,
            parameters,
        )
    )

    with open(
        f"{Constants.NETWORK_MODULES}/{network}/MSU_to_modules/{algo}/{parameters}/genes_to_modules.pickle",
        "rb",
    ) as f, open(
        f"{Constants.GENES_TO_ONTOLOGY_PATHWAY}/genes_to_go.pickle", "rb"
    ) as f_go, open(
        f"{Constants.GENES_TO_ONTOLOGY_PATHWAY}/genes_to_to.pickle", "rb"
    ) as f_to, open(
        f"{Constants.GENES_TO_ONTOLOGY_PATHWAY}/genes_to_po.pickle", "rb"
    ) as f_po, open(
        f"{Constants.GENES_TO_ONTOLOGY_PATHWAY}/genes_to_pathway.pickle", "rb"
    ) as f_pathway:
        genes_to_modules_mapping = pickle.load(f)
        genes_to_go_mapping = pickle.load(f_go)
        genes_to_to_mapping = pickle.load(f_to)
        genes_to_po_mapping = pickle.load(f_po)
        genes_to_pathway_mapping = pickle.load(f_pathway)

        gene_to_coexpression = [
            [
                gene,
                len(genes_to_modules_mapping[gene]),
                len(genes_to_modules_mapping[gene].intersection(enriched_modules)),
                len(genes_to_go_mapping[gene]),
                len(
                    genes_to_go_mapping[gene].intersection(
                        get_ontology_terms_in_modules(
                            enriched_modules, "go", network, algo, parameters
                        )
                    )
                ),
                len(genes_to_to_mapping[gene]),
                len(
                    genes_to_to_mapping[gene].intersection(
                        get_ontology_terms_in_modules(
                            enriched_modules, "to", network, algo, parameters
                        )
                    )
                ),
                len(genes_to_po_mapping[gene]),
                len(
                    genes_to_po_mapping[gene].intersection(
                        get_ontology_terms_in_modules(
                            enriched_modules, "po", network, algo, parameters
                        )
                    )
                ),
                len(genes_to_pathway_mapping[gene]),
                len(
                    genes_to_pathway_mapping[gene].intersection(
                        get_pathways_in_modules(
                            enriched_modules, "ora", network, algo, parameters
                        )
                    )
                ),
                len(
                    genes_to_pathway_mapping[gene].intersection(
                        get_pathways_in_modules(
                            enriched_modules, "pe", network, algo, parameters
                        )
                    )
                ),
                len(
                    genes_to_pathway_mapping[gene].intersection(
                        get_pathways_in_modules(
                            enriched_modules, "spia", network, algo, parameters
                        )
                    )
                ),
            ]
            for gene in combined_gene_ids
        ]

        gene_to_coexpression_df = pd.DataFrame(
            gene_to_coexpression,
            columns=[
                "Name",
                "# Modules",
                "# Enriched Modules",
                "# Gene Ontology Terms",
                "# Enriched Gene Ontology Terms",
                "# Trait Ontology Terms",
                "# Enriched Trait Ontology Terms",
                "# Plant Ontology Terms",
                "# Enriched Plant Ontology Terms",
                "# Pathways",
                "# Enriched Pathways (Over-Representation)",
                "# Enriched Pathways (Pathway-Express)",
                "# Enriched Pathways (SPIA)",
            ],
        )

    return gene_to_coexpression_df


def create_summary_results_dir(
    genomic_intervals, addl_genes, network, algo, parameters
):
    temp_output_folder_dir = get_path_to_temp(
        genomic_intervals,
        Constants.TEMP_SUMMARY,
        f"{shorten_name(addl_genes)}/{network}/{algo}/{parameters}",
    )

    if not path_exists(temp_output_folder_dir):
        make_dir(temp_output_folder_dir)

    return temp_output_folder_dir


def make_summary_table(
    genomic_intervals,
    combined_gene_ids,
    submitted_addl_genes,
    network,
    algo,
    parameters,
):
    SUMMARY_RESULTS_DIR = create_summary_results_dir(
        genomic_intervals, submitted_addl_genes, network, algo, parameters
    )
    SUMMARY_RESULS_PATH = f"{SUMMARY_RESULTS_DIR}/summary.csv"

    if not path_exists(SUMMARY_RESULS_PATH):
        implicated_genes = get_all_genes(
            other_ref_genomes.keys(), genomic_intervals
        ).values.tolist()

        liftover_summary = get_liftover_summary(implicated_genes)

        qtl_summary = get_qtl_summary(genomic_intervals)
        pubmed_summary = get_pubmed_summary(genomic_intervals)

        coexpression_summary = get_coexpression_summary(
            genomic_intervals,
            combined_gene_ids,
            submitted_addl_genes,
            network,
            algo,
            parameters,
        )

        # Merge the summaries
        summary = liftover_summary.merge(
            qtl_summary, on="Name", how="left", validate="one_to_one"
        )
        summary = summary.merge(
            pubmed_summary, on="Name", how="left", validate="one_to_one"
        )

        # Use right merge since there may be additional genes included in the co-expression analysis
        summary = summary.merge(
            coexpression_summary, on="Name", how="right", validate="one_to_one"
        )

        summary = summary.rename(columns={"Name": "Gene"})

        # Sort by sum of columns
        summary["sum"] = summary.drop("Gene", axis=1).sum(axis=1)
        summary = summary.sort_values("sum", ascending=False)
        del summary["sum"]

        SUMMARY_RESULTS_PATH_WITH_TIMESTAMP = append_timestamp_to_filename(
            SUMMARY_RESULS_PATH
        )
        summary.to_csv(SUMMARY_RESULTS_PATH_WITH_TIMESTAMP, index=False)

        try:
            os.replace(SUMMARY_RESULTS_PATH_WITH_TIMESTAMP, SUMMARY_RESULS_PATH)
        except:
            pass

    return pd.read_csv(SUMMARY_RESULS_PATH)
