library(clusterProfiler)
library(data.table)
library(ggplot2)
library(optparse)
library(tidyverse)

option_list <- list(
    make_option(c("-g", "--modules"),
        type = "character", default = NULL,
        help = "text file containing the modules (gene IDs should be MSU accessions)"
    ),
    make_option(c("-i", "--module_index"),
        type = "integer", default = NULL,
        help = "index of the module of interest (first module is index 1)"
    ),
    make_option(c("-b", "--background_genes"),
        type = "character", default = NULL,
        help = "text file containing the background genes"
    ),
    make_option(c("-m", "--po_to_gene_mapping"),
        type = "character", default = NULL,
        help = "text file mapping the PO IDs to the genes"
    ),
    make_option(c("-t", "--po_to_name_mapping"),
        type = "character", default = NULL,
        help = "text file mapping the PO IDs to the PO names"
    ),
    make_option(c("-o", "--output_dir"),
        type = "character", default = NULL,
        help = "output directory for the data frame and plot showing the enriched PO terms"
    )
)

opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser)

modules <- readLines(opt$modules)
modules <- str_split(modules, "\t")

genes <- unlist(modules[opt$module_index])

background <- readLines(opt$background_genes)
background <- str_split(background, "\t")
background <- unlist(background)

po <- enricher(
    gene = genes,
    universe = background,
    TERM2GENE = read.table(opt$po_to_gene_mapping, sep = "\t", stringsAsFactors = FALSE),
    TERM2NAME = read.table(opt$po_to_name_mapping, sep = "\t", stringsAsFactors = FALSE)
)

print("Finished enrichment analysis")

if (!dir.exists(opt$output_dir)) {
    dir.create(opt$output_dir, recursive = TRUE)
}

if (!dir.exists(paste0(opt$output_dir, "/results"))) {
    dir.create(paste0(opt$output_dir, "/results"), recursive = TRUE)
}

if (!dir.exists(paste0(opt$output_dir, "/plots"))) {
    dir.create(paste0(opt$output_dir, "/plots"), recursive = TRUE)
}

po_df <- as.data.frame(po)
write.table(po_df, paste0(opt$output_dir, "/results/po-df-", opt$module_index, ".tsv"),
    sep = "\t", row.names = FALSE, quote = FALSE
)

if (nrow(po_df) > 0) {
    plot <- dotplot(po,
        showCategory = nrow(po_df),
        title = "Enriched PO Terms",
        font.size = 10
    )

    ggsave(plot,
        filename = paste0(opt$output_dir, "/plots/po-dotplot-", opt$module_index, ".png"),
        height = max(c(22, nrow(po_df))), width = 22, units = "cm"
    )

    print(paste0(
        "Generated data frame and dot plot showing the enriched PO terms for module #",
        opt$module_index
    ))
} else {
    print(paste0("No PO terms enriched for module #", opt$module_index))
}
