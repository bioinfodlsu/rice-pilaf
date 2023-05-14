library(data.table)
library(ggplot2)
library(riceidconverter)
library(SPIA)
library(graphite)
library(tidyverse)
library(ROntoTools)


kpg <- keggPathwayGraphs("dosa")
kpg <- setEdgeWeights(kpg)
kpg <- setNodeWeights(kpg)

print(kpg$`path:dosa03015`@nodes)

module <- readLines("data/clusters/transcript/clusterone-module-list.txt")
module <- str_split(module, "\t")

genes <- paste0("dosa:", unlist(module[100]))
dummy_fc <- replicate(length(genes), 20)
input_data <- setNames(dummy_fc, genes)

background <- readLines("data/all_genes/transcript/all_genes.txt")
background <- str_split(background, "\t")
background <- paste0("dosa:", unlist(background))

peRes <- pe(input_data, graphs = kpg, ref = background, nboot = 2000, verbose = TRUE)
kegg_df <- head(summary(peRes))

write.table(kegg_df, "data/pe.txt", sep = "\t", row.names = TRUE, quote = FALSE)
