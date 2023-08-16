install.packages("optparse", repos = "http://cran.us.r-project.org")

install.packages("BiocManager", repos = "http://cran.us.r-project.org")
library(BiocManager)
BiocManager::install("clusterProfiler", version = "3.17", ask = FALSE)
