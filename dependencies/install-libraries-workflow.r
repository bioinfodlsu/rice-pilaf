install.packages("optparse", repos = "http://cran.us.r-project.org")
install.packages("ggplot2", repos = "http://cran.us.r-project.org")

bioconductor_packages <- c(
    "clusterProfiler_4.8.3.tar.gz",
    "GO.db_3.17.0.tar.gz",
    "graphite_1.46.0.tar.gz",
    "ROntoTools_2.28.0.tar.gz",
    "SPIA_2.52.0.tar.gz"
)

for (i in seq_along(bioconductor_packages)) {
    bioconductor_packages[i] <- paste0("/app/dependencies/temp/", bioconductor_packages[i])
    print(bioconductor_packages[i])
}

install.packages(bioconductor_packages, repos = null, type = "source")