library(clusterProfiler)
library(data.table)
library(ggplot2)

genes <- read.table("data/modules/cluster1.txt")
genes <- genes[[1]]

background <- read.table("data/all_genes.txt")
background <- background[[1]]


kegg <- enrichKEGG(
  gene = genes_transcript,
  universe = background_transcript,
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
