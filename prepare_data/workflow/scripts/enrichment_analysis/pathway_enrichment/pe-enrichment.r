library(data.table)
library(ggplot2)
library(graphite)
library(tidyverse)
library(optparse)
library(ROntoTools)

option_list <- list(
    make_option(c("-g", "--modules"),
        type = "character", default = NULL,
        help = "text file containing the modules (gene IDs should be KEGG transcript IDs)"
    ),
    make_option(c("-i", "--module_index"),
        type = "integer", default = NULL,
        help = "index of the module of interest (first module is index 1)"
    ),
    make_option(c("-b", "--background_genes"),
        type = "character", default = NULL,
        help = "text file containing the background genes"
    ),
    make_option(c("-o", "--output_dir"),
        type = "character", default = NULL,
        help = "output directory for the data frame and plot showing the enriched pathways"
    )
)

opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser)

modules <- readLines(opt$modules)
modules <- str_split(modules, "\t")

genes <- paste0("dosa:", unlist(modules[opt$module_index]))
dummy_val <- 20
dummy_fc <- replicate(length(genes), dummy_val)
input_data <- setNames(dummy_fc, genes)

background <- readLines(opt$background_genes)
background <- str_split(background, "\t")
background <- paste0("dosa:", unlist(background))

kpg <- keggPathwayGraphs("dosa")
kpg <- setEdgeWeights(kpg)
kpg <- setNodeWeights(kpg)

pe_results <- pe(input_data,
    graphs = kpg,
    ref = background, nboot = 2000, verbose = TRUE
)

if (!dir.exists(opt$output_dir)) {
    dir.create(opt$output_dir, recursive = TRUE)
}

if (!dir.exists(paste0(opt$output_dir, "/results"))) {
    dir.create(paste0(opt$output_dir, "/results"), recursive = TRUE)
}

kegg_df <- head(summary(pe_results))
write.table(kegg_df, paste0(opt$output_dir, "/results/pe-df-", opt$module_index, ".tsv"),
    sep = "\t", row.names = TRUE, quote = FALSE
)

cat("\n")
print(paste0(
    "Generated data frame showing the enriched KEGG pathways for module #",
    opt$module_index
))
