library(clusterProfiler)
library(data.table)
library(ggplot2)
library(riceidconverter)

module <- readLines("data/clusters/transcript/clusterone-module-list.txt")
module <- str_split(module, "\t")

genes <- unlist(module[1])

background <- readLines("data/all_genes/transcript/all_genes.txt")
background <- str_split(background, "\t")
background <- unlist(background)

kegg <- enrichKEGG(
  gene = genes,
  universe = background,
  organism = "dosa",
  keyType = "kegg",
)

kegg_df <- as.data.frame(kegg)
write.table(kegg_df, "data/kegg_df.txt", sep = "\t", row.names = FALSE, quote = FALSE)

p1 <- dotplot(kegg,
  showCategory = nrow(kegg_df),
  title = "Top 10 most statistically significant enriched KEGG terms",
  font.size = 10
)

ggsave(p1,
  filename = "data/kegg_dotplot.png",
  height = 22, width = 22, units = "cm"
)
