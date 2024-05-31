install.packages("devtools", repos = "http://cran.rstudio.com")
install.packages("BiocManager", repos = "http://cran.rstudio.com")

library(devtools)
library(BiocManager)

packages <- c(
    "optparse",
    "ggplot2",
    "clusterProfiler",
    "GO.db",
    "graphite",
    "ROntoTools",
    "SPIA"
)

for (package in packages) {
    package_dir <- paste0("/app/dependencies/temp/", package)
    devtools::install(
        package_dir, dependencies = TRUE, repos = BiocManager::repositories()
    )
}