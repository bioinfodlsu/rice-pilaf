library(ggplot2)
library(optparse)
library(clusterProfiler)

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
    make_option(c("-m", "--to_to_gene_mapping"),
        type = "character", default = NULL,
        help = "text file mapping the TO IDs to the genes"
    ),
    make_option(c("-t", "--to_to_name_mapping"),
        type = "character", default = NULL,
        help = "text file mapping the TO IDs to the TO names"
    ),
    make_option(c("-o", "--output_dir"),
        type = "character", default = NULL,
        help = "output directory for the data frame and plot showing the enriched TO terms"
    )
)

opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser)

to <- enricher(
    gene = unlist(strsplit(readLines(opt$modules), "\t")[opt$module_index]),
    universe = unlist(strsplit(readLines(opt$background_genes), "\t")),
    TERM2GENE = read.table(opt$to_to_gene_mapping, sep = "\t", stringsAsFactors = FALSE),
    TERM2NAME = read.table(opt$to_to_name_mapping, sep = "\t", stringsAsFactors = FALSE)
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

to_df <- as.data.frame(to)
write.table(to_df, paste0(opt$output_dir, "/results/to-df-", opt$module_index, ".tsv"),
    sep = "\t", row.names = FALSE, quote = FALSE
)

if (nrow(to_df) > 0) {
    plot <- dotplot(to,
        showCategory = nrow(to_df),
        title = "Enriched TO Terms",
        font.size = 10
    )

    ggsave(plot,
        filename = paste0(opt$output_dir, "/plots/to-dotplot-", opt$module_index, ".png"),
        height = max(c(22, nrow(to_df))), width = 22, units = "cm"
    )

    print(paste0(
        "Generated data frame and dot plot showing the enriched TO terms for module #",
        opt$module_index
    ))
} else {
    print(paste0("No TO terms enriched for module #", opt$module_index))
}
