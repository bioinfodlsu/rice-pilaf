# library(ggplot2)
library(optparse)
library(GO.db)
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
    make_option(c("-m", "--go_to_gene_mapping"),
        type = "character", default = NULL,
        help = "text file mapping the GO IDs to the genes"
    ),
    make_option(c("-o", "--output_dir"),
        type = "character", default = NULL,
        help = "output directory for the data frame and plot showing the enriched GO terms"
    )
)

opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser)

go <- enricher(
    gene = unlist(strsplit(readLines(opt$modules), "\t")[opt$module_index]),
    universe = unlist(strsplit(readLines(opt$background_genes), "\t")),
    TERM2GENE = read.table(opt$go_to_gene_mapping, sep = "\t", stringsAsFactors = FALSE),
    TERM2NAME = data.frame("GOID" = names(Term(GOTERM)), "term" = Term(GOTERM))
)

print("Finished enrichment analysis")

if (!dir.exists(opt$output_dir)) {
    dir.create(opt$output_dir, recursive = TRUE)
}

if (!dir.exists(paste0(opt$output_dir, "/results"))) {
    dir.create(paste0(opt$output_dir, "/results"), recursive = TRUE)
}

# if (!dir.exists(paste0(opt$output_dir, "/plots"))) {
#     dir.create(paste0(opt$output_dir, "/plots"), recursive = TRUE)
# }

go_df <- as.data.frame(go)
write.table(go_df, paste0(opt$output_dir, "/results/go-df-", opt$module_index, ".tsv"),
    sep = "\t", row.names = FALSE, quote = FALSE
)

if (nrow(go_df) > 0) {
    # plot <- dotplot(go,
    #     showCategory = nrow(go_df),
    #     title = "Enriched GO Terms",
    #     font.size = 10
    # )

    # ggsave(plot,
    #     filename = paste0(opt$output_dir, "/plots/go-dotplot-", opt$module_index, ".png"),
    #     height = max(c(22, nrow(go_df))), width = 22, units = "cm"
    # )

    print(paste0(
        "Generated data frame and dot plot showing the enriched GO terms for module #",
        opt$module_index
    ))
} else {
    print(paste0("No GO terms enriched for module #", opt$module_index))
}
