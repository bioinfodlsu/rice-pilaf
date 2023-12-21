install.packages("optparse", repos = "http://cran.us.r-project.org")
install.packages("ggplot2", repos = "http://cran.us.r-project.org")

install.packages("BiocManager", repos = "http://cran.us.r-project.org")
library(BiocManager)
BiocManager::install(version = "3.17", ask = FALSE)
BiocManager::install("clusterProfiler", version = "3.17", ask = FALSE)
BiocManager::install("GO.db", version = "3.17", ask = FALSE)

BiocManager::install("graphite", version = "3.17", ask = FALSE)
BiocManager::install("ROntoTools", version = "3.17", ask = FALSE)
BiocManager::install("SPIA", version = "3.17", ask = FALSE)
