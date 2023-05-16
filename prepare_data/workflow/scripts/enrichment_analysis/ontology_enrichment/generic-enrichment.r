library(clusterProfiler)
library(data.table)
library(ggplot2)
library(optparse)
library(tidyverse)
library(GO.db)

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

modules <- readLines(opt$input_genes)
modules <- str_split(modules, "\t")

genes <- unlist(modules[1]) # There is only a single line

background <- readLines(opt$background_genes)
background <- str_split(background, "\t")
background <- unlist(background)

go <- enricher(
    gene = genes,
    universe = background,
    TERM2GENE = read.table(opt$module_to_gene_mapping,
        sep = "\t", stringsAsFactors = FALSE
    )
)

if (!dir.exists(opt$output_dir)) {
    dir.create(opt$output_dir, recursive = TRUE)
}

if (!dir.exists(paste0(opt$output_dir, "/enriched_modules"))) {
    dir.create(paste0(opt$output_dir, "/enriched_modules"), recursive = TRUE)
}

go_df <- as.data.frame(go)
write.table(go_df,
    paste0(opt$output_dir, "/enriched_modules/ora-df", ".tsv"),
    sep = "\t", row.names = FALSE, quote = FALSE
)

if (nrow(go_df) > 0) {
    plot <- dotplot(go,
        showCategory = nrow(go_df),
        title = "Enriched modules",
        font.size = 10
    )

    ggsave(plot,
        filename = paste0(opt$output_dir, "/enriched_modules/ora-dotplot", ".png"),
        height = max(c(22, nrow(go_df))), width = 22, units = "cm"
    )
}
