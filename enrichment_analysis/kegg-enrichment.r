library(clusterProfiler)
library(data.table)
library(ggplot2)
library(riceidconverter)

genes <- read.table("data/cluster1.txt")
genes <- genes[[1]]

background <- read.table("data/all_genes.txt")
background <- background[[1]]

genes_transcript <- c()
na_genes_transcript <- c()
for (gene in genes) {
  transcript_id <- RiceIDConvert(gene, fromType = "MSU", toType = "TRANSCRIPTID")
  for (id in transcript_id$TRANSCRIPTID) {
    if (is.na(id)) {
      print(gene)
      na_genes_transcript <- append(na_genes_transcript, gene)
    } else {
      genes_transcript <- append(genes_transcript, id)
    }
  }
}

lapply(na_genes_transcript, write, "data/cluster1-na-transcript-id.txt", append = TRUE, sep = "\n")
lapply(genes_transcript, write, "data/cluster1-transcript-id.txt", append = TRUE, sep = "\n")

background_transcript <- c()
na_background_transcript <- c()
for (gene in background) {
  transcript_id <- RiceIDConvert(gene, fromType = "MSU", toType = "TRANSCRIPTID")
  for (id in transcript_id$TRANSCRIPTID) {
    if (is.na(id)) {
      print(gene)
      na_background_transcript <- append(na_background_transcript, gene)
    } else {
      background_transcript <- append(background_transcript, id)
    }
  }
}

lapply(na_background_transcript, write, "data/all-na-transcript-id.txt", append = TRUE, sep = "\n")
lapply(background_transcript, write, "data/all-transcript-id.txt", append = TRUE, sep = "\n")

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
