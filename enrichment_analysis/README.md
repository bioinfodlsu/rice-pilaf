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

Prerequisites:

-   Install the following R libraries:
    -   [`GO.db`](https://bioconductor.org/packages/release/data/annotation/html/GO.db.html)
    -   [`riceidconverter`](https://cran.r-project.org/web/packages/riceidconverter/index.html)

This recipe maps the MSU accessions used in the app to the target IDs required by the pathway enrichment tools; the last two commands assume that the modules of interest were obtained via the ClusterONE algorithm:

```
Rscript --vanilla util/ricegeneid-msu-to-transcript-id.r -g ../static/networks_modules/OS-CX/all-genes.txt -o data/temp
python util/msu-to-transcript-id.py data/temp/all-transcript-id.txt data/temp/all-na-transcript-id.txt data/rap_db/RAP-MSU_2023-03-15.txt data/rap_db/IRGSP-1.0_representative_annotation_2023-03-15.tsv data/mapping
python util/msu-to-entrez-id.py data/to_entrez/riceIDtable.csv data/mapping
python util/file-convert-msu.py ../static/networks_modules/OS-CX/all-genes.txt data/mapping/msu-to-entrez-id.pickle data/all_genes entrez
python util/file-convert-msu.py ../static/networks_modules/OS-CX/all-genes.txt data/mapping/msu-to-transcript-id.pickle data/all_genes transcript
python util/file-convert-msu.py ../static/networks_modules/OS-CX/module_list/clusterone-module-list.tsv data/mapping/msu-to-entrez-id.pickle data/modules/clusterone entrez
python util/file-convert-msu.py ../static/networks_modules/OS-CX/module_list/clusterone-module-list.tsv data/mapping/msu-to-transcript-id.pickle data/modules/clusterone transcript
```

This recipe prepares the data needed for gene ontology enrichment analysis:

```
python util/aggregate-go-annotations.py data/go/agrigo.tsv data/go/OryzabaseGeneListAll_20230322010000.txt data/rap_db/IRGSP-1.0_representative_annotation_2023-03-15.tsv data/all_genes/transcript/all-genes.tsv data/mapping/msu-to-transcript-id.pickle data/go
```

This recipe prepares the data needed for trait ontology enrichment analysis:

```

```

This recipe prepares the data needed for plant ontology enrichment analysis:

```

```

### 2. Ontology Enrichment Analysis

#### a. Gene Ontology Enrichment Analysis

This recipe assumes that the module of interest is the first module (as specified using the `-i` parameter):

```
Rscript --vanilla go-enrichment.r -g ../static/networks_modules/OS-CX/module_list/clusterone-module-list.tsv -i 1 -b ../static/networks_modules/OS-CX/all-genes.txt -m data/go/go-annotations.tsv -o data/output/go_enrichment
```

#### b. Trait Ontology Enrichment Analysis

#### b. Plant Ontology Enrichment Analysis

### 3. Pathway Enrichment Analysis

#### a. Overrepresentation Analysis via clusterProfiler

#### b. Topology-Based Analysis via Pathway-Express

#### c. Topology-Based Analysis via SPIA
