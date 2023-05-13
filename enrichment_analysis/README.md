# Enrichment Analysis Scripts

Running the R scripts from the terminal require the [`optparse`](https://cran.r-project.org/web/packages/optparse/index.html) library. It can be installed by running the following command:

```
RScript -e "install.packages('optparse', repos ='https://cran.rstudio.com/')"
```

Note that all recipes assume that the working directory is the directory containing this `README`.

## Scripts

## Recipes

Download all the necessary data following the instructions [here](https://github.com/bioinfodlsu/rice-pilaf/blob/main/docs/Data_sources.md#enrichment-analysis).

### 1. Data Preparation

This recipe maps the MSU accessions used in the app to the target IDs required by the pathway enrichment tools:
```
Rscript util/ricegeneid-msu-to-transcript-id.r -g ../static/networks_modules/OS-CX/all-genes.txt -o data/temp
python util/msu-to-transcript-id.py data/temp/all-transcript-id.txt data/temp/all-na-transcript-id.txt data/rap_db/RAP-MSU_2023-03-15.txt data/rap_db/IRGSP-1.0_representative_annotation_2023-03-15.tsv data/mapping
python util/msu-to-entrez-id.py data/to_entrez/riceIDtable.csv data/mapping
```

This recipe maps the gene ontology term IDs to their respective gene ontology term names:
```
Rscript util/prepare-go.r -o data/go
```

### 2. Gene Ontology (GO) Enrichment Analysis

### 3. Pathway Enrichment Analysis

#### a. Overrepresentation Analysis via clusterProfiler

#### b. Topology-Based Analysis via Pathway-Express

#### c. Topology-Based Analysis via SPIA
