#!/bin/bash -e

# Create temporary folder for storing package tarballs
temp="dependencies/temp"
mkdir -p "$temp"

# Download tarballs of R packages
wget https://cran.r-project.org/src/contrib/Archive/optparse/optparse_1.7.3.tar.gz -P "$temp"
wget https://cran.r-project.org/src/contrib/Archive/ggplot2/ggplot2_3.4.2.tar.gz -P "$temp"

wget https://bioconductor.org/packages/3.17/bioc/src/contrib/clusterProfiler_4.8.3.tar.gz -P "$temp"
wget https://www.bioconductor.org/packages/3.17/data/annotation/src/contrib/GO.db_3.17.0.tar.gz -P "$temp"
wget https://bioconductor.org/packages/3.17/bioc/src/contrib/graphite_1.46.0.tar.gz -P "$temp"
wget https://bioconductor.org/packages/3.17/bioc/src/contrib/ROntoTools_2.28.0.tar.gz -P "$temp"
wget https://bioconductor.org/packages/3.17/bioc/src/contrib/SPIA_2.52.0.tar.gz -P "$temp"

# Install R packages from source
Rscript --vanilla dependencies/install-r-packages-workflow.r

# Delete temporary folder for storing package tarballs
rm -rf "$temp"