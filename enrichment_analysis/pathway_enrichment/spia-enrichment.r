library(data.table)
library(ggplot2)
library(riceidconverter)
library(SPIA)
library(graphite)
library(tidyverse)

# if (!dir.exists("data/kegg_dosa/SPIA")) {
#   dir.create("data/kegg_dosa/SPIA")
# }

module <- readLines("data/clusters/transcript/clusterone-module-list.txt")
module <- str_split(module, "\t")

genes <- unlist(module[100])
dummy_fc <- replicate(length(genes), 20)
input_data <- setNames(dummy_fc, genes)

background <- read.table("data/all_genes/transcript/all_genes.txt")
background <- background[[1]]

res <- spia(de = input_data, all = background, organism = "dosa", data.dir = "data/kegg_dosa/SPIA/")

kegg_df <- as.data.frame(res)
write.table(kegg_df, "data/spia_df.txt", sep = "\t", row.names = FALSE, quote = FALSE)
