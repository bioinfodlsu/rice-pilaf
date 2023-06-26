install.packages("optparse", repos = "http://cran.us.r-project.org")
install.packages("ggplot2", repos = "http://cran.us.r-project.org")

install.packages("BiocManager", repos = "http://cran.us.r-project.org")
library(BiocManager)
BiocManager::install("clusterProfiler", ask = FALSE)
BiocManager::install("GO.db", ask = FALSE)

BiocManager::install("graphite", ask = FALSE)
BiocManager::install("ROntoTools", ask = FALSE)
BiocManager::install("SPIA", ask = FALSE)
