suppressPackageStartupMessages({
    library(optparse)
    library(clusterProfiler)
})

option_list <- list(
    make_option(c("-g", "--input_genes"),
        type = "character", default = NULL,
        help = "text file containing the input genes (gene IDs should be MSU accessions)"
    ),
    make_option(c("-b", "--background_genes"),
        type = "character", default = NULL,
        help = "text file containing the background genes"
    ),
    make_option(c("-m", "--module_to_gene_mapping"),
        type = "character", default = NULL,
        help = "text file mapping the modules to the genes"
    ),
    make_option(c("-o", "--output_dir"),
        type = "character", default = NULL,
        help = "output directory for the data frame and plot showing the enriched modules"
    )
)

opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser)

go <- enricher(
    gene = unlist(strsplit(readLines(opt$input_genes), "\t")[1]),       # There is only a single line
    universe = unlist(strsplit(readLines(opt$background_genes), "\t")),
    TERM2GENE = read.table(opt$module_to_gene_mapping,
        sep = "\t", stringsAsFactors = FALSE
    ),
    minGSSize = 2,
    maxGSSize = 100000,
    # pAdjustMethod = "none"
)

if (!dir.exists(paste0(opt$output_dir, "/enriched_modules"))) {
    dir.create(paste0(opt$output_dir, "/enriched_modules"), recursive = TRUE)
}

tryCatch({
    write.table((as.data.frame(go))[c("ID", "p.adjust")],
        paste0(opt$output_dir, "/enriched_modules/ora-df", ".tsv"),
        sep = "\t", row.names = FALSE, quote = FALSE
    )
}, error = function(err) {
    df <- data.frame(matrix(nrow = 0, ncol = 2))
    colnames(df) <- c("ID", "p.adjust")
    write.table(df,
        paste0(opt$output_dir, "/enriched_modules/ora-df", ".tsv"),
        sep = "\t", row.names = FALSE, quote = FALSE
    )
})
