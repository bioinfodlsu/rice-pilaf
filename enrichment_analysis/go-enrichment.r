library(clusterProfiler)
library(data.table)
library(ggplot2)

genes <- read.table("data/modules/cluster1.txt")
genes <- genes[[1]]

background <- read.table("data/all_genes.txt")
background <- background[[1]]

gene_go <- read.table("data/go/agrigo.txt", stringsAsFactors = FALSE)
gene_go <- gene_go[, 3:4]
gene_go <- gene_go[, c(2,1)]

go_label <- read.table("data/go/go_terms.txt", sep = '\t', stringsAsFactors = FALSE)

go <- enricher(gene = genes,
               universe = background,
               TERM2GENE = gene_go,  
               TERM2NAME = go_label
)

go_df <- as.data.frame(go)
write.table(go_df, "data/output/go_df.txt", sep = "\t", row.names = FALSE, quote = FALSE)

p1 <- dotplot(go,
              showCategory = nrow(go_df),
              title = "Top 10 most statistically significant enriched GO terms",
              font.size = 10
)
ggsave(p1,
       filename = "data/go_dotplot.png",
       height = 22, width = 22, units = "cm"
)


