library(KEGGREST)

genes <- keggLink("pathway", "dosa")
genes_df <- t(data.frame(as.list(genes)))

write.table(genes_df, "C:/Users/DLSU/Documents/rice_pilaf/static/app_data/enrichment_analysis/mapping/kegg-dosa-geneset.tsv",
            sep = "/t", row.names = TRUE, col.names = FALSE, quote = FALSE)

# write.table(genes_df,
#             paste0(opt$output_dir, "/results/spia-df-", opt$module_index, ".tsv"),
#             sep = "/t", row.names = TRUE, quote = FALSE
# )