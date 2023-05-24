library(data.table)
library(ggplot2)
library(optparse)
library(tidyverse)
library(clusterProfiler)

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

genes <- unlist(modules[opt$module_index])

background <- readLines(opt$background_genes)
background <- str_split(background, "\t")
background <- unlist(background)

kegg <- enrichKEGG(
  gene = genes,
  universe = background,
  organism = "dosa",
  keyType = "kegg",
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

kegg_df <- as.data.frame(kegg)
write.table(kegg_df, paste0(opt$output_dir, "/results/ora-df-", opt$module_index, ".tsv"),
  sep = "\t", row.names = FALSE, quote = FALSE
)

if (nrow(kegg_df) > 0) {
  plot <- dotplot(kegg,
    showCategory = nrow(kegg_df),
    title = "Enriched KEGG Pathways",
    font.size = 10
  )

  ggsave(plot,
    filename = paste0(opt$output_dir, "/plots/ora-dotplot-", opt$module_index, ".png"),
    height = max(c(22, nrow(kegg_df))), width = 22, units = "cm"
  )

  print(paste0(
    "Generated data frame and dot plot showing the enriched KEGG pathways for module #",
    opt$module_index
  ))
} else {
  print(paste0("No KEGG pathways enriched for module #", opt$module_index))
}
