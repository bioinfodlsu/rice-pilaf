library(data.table)
library(ggplot2)
library(riceidconverter)
library(pathview)
library(SPIA)

BiocManager::install("SPIA")

if (!dir.exists("./data/kegg_dosa/SPIA")) {
  dir.create("./data/kegg_dosa/SPIA")
}

makeSPIAdata(kgml.path = "./data/kegg_dosa/XML", organism = "dosa", out.path = "./data/kegg_dosa/SPIA")

res <- spia(de=DE_Colorectal,all=ALL_Colorectal,organism="hsa",data.dir="./")