packages <- c(
    "optparse_1.7.3.tar.gz",
    "ggplot2_3.4.2.tar.gz",
    "clusterProfiler_4.8.3.tar.gz",
    "GO.db_3.17.0.tar.gz",
    "graphite_1.46.0.tar.gz",
    "ROntoTools_2.28.0.tar.gz",
    "SPIA_2.52.0.tar.gz"
)

for (i in seq_along(packages)) {
    packages[i] <- paste0("/app/dependencies/temp/", packages[i])
}

install.packages(packages, repos = NULL, type = "source")