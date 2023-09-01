library(KEGGREST)
library(optparse)

option_list <- list(
  make_option(c("-o", "--output_dir"),
    type = "character", default = NULL,
    help = "output directory for the text file containing the genes in each KEGG pathway for the organism 'dosa'"
  )
)

opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser)

genes <- keggLink("pathway", "dosa")
genes_df <- t(data.frame(as.list(genes)))

if (!dir.exists(opt$output_dir)) {
  dir.create(opt$output_dir, recursive = TRUE)
}

write.table(genes_df,
            paste0(opt$output_dir, "/kegg-dosa-geneset.tsv"),
            sep = "\t", row.names = TRUE, col.names = FALSE, quote = FALSE)

print(paste0("Generated ", opt$output_dir, "/kegg-dosa-geneset.tsv"))