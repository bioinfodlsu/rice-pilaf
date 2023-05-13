library(clusterProfiler)
library(data.table)
library(ggplot2)
library(optparse)
library(tidyverse)
library(GO.db)

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

module <- readLines(opt$input_genes)
module <- str_split(module, "\t")

genes <- unlist(module[100])

background <- readLines(opt$background_genes)
background <- str_split(background, "\t")
background <- unlist(background)

gene_go <- read.table(opt$go_to_gene_mapping, sep = "\t", stringsAsFactors = FALSE)
go_label <- read.table(opt$go_to_term_mapping, sep = "\t", stringsAsFactors = FALSE)

go <- enricher(
    gene = genes,
    universe = background,
    TERM2GENE = gene_go,
    TERM2NAME = data.frame("GOID" = names(Term(GOTERM)), "term" = Term(GOTERM))
)

print("Finished enrichment analysis")

if (!dir.exists(opt$output_dir)) {
    dir.create(opt$output_dir, recursive = TRUE)
}

go_df <- as.data.frame(go)
write.table(go_df, paste0(opt$output_dir, "/go-df.csv"), sep = "\t", row.names = FALSE, quote = FALSE)

p1 <- dotplot(go,
    showCategory = nrow(go_df),
    title = "Enriched GO Terms",
    font.size = 10
)

ggsave(p1,
    filename = paste0(opt$output_dir, "/go-dotplot.png"),
    height = 22, width = 22, units = "cm"
)

print("Generated data frame and dot plot showing the enriched GO terms")
