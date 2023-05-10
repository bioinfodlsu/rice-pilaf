library(clusterProfiler)
library(data.table)
library(ggplot2)
library(optparse)

option_list <- list(
       make_option(c("-g", "--input_genes"),
              type = "character", default = NULL,
              help = "text file containing the input genes (MSU ID)"
       ),
       make_option(c("-b", "--background_genes"),
              type = "character", default = NULL,
              help = "text file containing the background genes"
       ),
       make_option(c("-m", "--go_to_gene_mapping"),
              type = "character", default = NULL,
              help = "text file mapping the GO IDs to the genes"
       ),
       make_option(c("-t", "--go_to_term_mapping"),
              type = "character", default = NULL,
              help = "text file mapping the GO IDs to the GO terms"
       ),
       make_option(c("-o", "--output_dir"),
              type = "character", default = NULL,
              help = "output directory for the data frame and plot showing the enriched GO terms"
       )
)

opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser)

genes <- read.table(opt$input_genes)
genes <- genes[[1]]

background <- read.table(opt$background_genes)
background <- background[[1]]

gene_go <- read.table(opt$go_to_gene_mapping, stringsAsFactors = FALSE)
gene_go <- gene_go[, 3:4]
gene_go <- gene_go[, c(2, 1)]

go_label <- read.table(opt$go_to_term_mapping, sep = "\t", stringsAsFactors = FALSE)

go <- enricher(
       gene = genes,
       universe = background,
       TERM2GENE = gene_go,
       TERM2NAME = go_label
)

print("Finished enrichment analysis")

go_df <- as.data.frame(go)
write.table(go_df, paste0(opt$output_dir, "/go_df.txt"), sep = "\t", row.names = FALSE, quote = FALSE)

p1 <- dotplot(go,
       showCategory = nrow(go_df),
       title = "Enriched GO Terms",
       font.size = 10
)

ggsave(p1,
       filename = paste0(opt$output_dir, "/go_dotplot.png"),
       height = 22, width = 22, units = "cm"
)

print("Generated data frame and dot plot showing the enriched GO terms")
