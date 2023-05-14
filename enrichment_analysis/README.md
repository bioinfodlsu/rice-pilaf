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

Output: TSV files containing Entrez and KEGG transcript IDs in `data/all_genes` and `data/modules/clusterone`

This recipe prepares the data needed for gene ontology enrichment analysis:

```
python util/aggregate-go-annotations.py data/go/agrigo.tsv data/go/OryzabaseGeneListAll_20230322010000.txt data/rap_db/IRGSP-1.0_representative_annotation_2023-03-15.tsv data/all_genes/transcript/all-genes.tsv data/mapping/msu-to-transcript-id.pickle data/go
```

Output: `go-annotations.tsv` in `data/go`

This recipe prepares the data needed for trait ontology enrichment analysis:

```
python util/aggregate-to-annotations.py data/go/OryzabaseGeneListAll_20230322010000.txt data/to
```

Output: `to-annotations.tsv` and `to-id-to-name.tsv` in `data/to`

This recipe prepares the data needed for plant ontology enrichment analysis:

```
python util/aggregate-po-annotations.py data/go/OryzabaseGeneListAll_20230322010000.txt data/po
```

Output: `po-annotations.tsv` and `po-id-to-name.tsv` in `data/po`

### 2. Ontology Enrichment Analysis

#### a. Gene Ontology Enrichment Analysis

Prerequisites:

-   Install the following R libraries:
    -   [`GO.db`](https://bioconductor.org/packages/release/data/annotation/html/GO.db.html)
    -   [`clusterProfiler`](https://bioconductor.org/packages/release/bioc/html/clusterProfiler.html)

This recipe assumes that the module of interest is the first module (as specified using the `-i` parameter):

```
Rscript --vanilla ontology_enrichment/go-enrichment.r -g ../static/networks_modules/OS-CX/module_list/clusterone-module-list.tsv -i 1 -b ../static/networks_modules/OS-CX/all-genes.txt -m data/go/go-annotations.tsv -o data/output/ontology_enrichment/go
```

Output: Results table and dot plot in `output/ontology_enrichment/go`

#### b. Trait Ontology Enrichment Analysis

Prerequisites:

-   Install the following R libraries:
    -   [`clusterProfiler`](https://bioconductor.org/packages/release/bioc/html/clusterProfiler.html)

This recipe assumes that the module of interest is the first module (as specified using the `-i` parameter):

```
Rscript --vanilla ontology_enrichment/to-enrichment.r -g ../static/networks_modules/OS-CX/module_list/clusterone-module-list.tsv -i 1 -b ../static/networks_modules/OS-CX/all-genes.txt -m data/to/to-annotations.tsv -t data/to/to-id-to-name.tsv -o data/output/ontology_enrichment/to
```

Output: Results table and dot plot in `output/ontology_enrichment/to`

#### b. Plant Ontology Enrichment Analysis

Prerequisites:

-   Install the following R libraries:
    -   [`clusterProfiler`](https://bioconductor.org/packages/release/bioc/html/clusterProfiler.html)

This recipe assumes that the module of interest is the first module (as specified using the `-i` parameter):

```
Rscript --vanilla ontology_enrichment/po-enrichment.r -g ../static/networks_modules/OS-CX/module_list/clusterone-module-list.tsv -i 1 -b ../static/networks_modules/OS-CX/all-genes.txt -m data/po/po-annotations.tsv -t data/po/po-id-to-name.tsv -o data/output/ontology_enrichment/po
```

Output: Results table and dot plot in `output/ontology_enrichment/to`

### 3. Pathway Enrichment Analysis

#### a. Overrepresentation Analysis via clusterProfiler

Prerequisites:

-   Install the following R libraries:
    -   [`clusterProfiler`](https://bioconductor.org/packages/release/bioc/html/clusterProfiler.html)

This recipe assumes that the module of interest is the first module (as specified using the `-i` parameter):

```
Rscript --vanilla pathway_enrichment/ora-enrichment.r -g data/modules/clusterone/transcript/clusterone-module-list.tsv -i 1 -b data/all_genes/transcript/all-genes.tsv -o data/output/pathway_enrichment/ora
```

Output: Results table and dot plot in `output/pathway_enrichment/ora`

#### b. Topology-Based Analysis via Pathway-Express

Paper: https://pubmed.ncbi.nlm.nih.gov/17785539/

Prerequisites:

-   Install the following R libraries:
    -   [`ROntoTools`](https://bioconductor.org/packages/release/bioc/html/ROntoTools.html)

This recipe assumes that the module of interest is the 100<sup>th</sup> module (as specified using the `-i` parameter):

```
Rscript --vanilla pathway_enrichment/pe-enrichment.r -g data/modules/clusterone/transcript/clusterone-module-list.tsv -i 100 -b data/all_genes/transcript/all-genes.tsv -o data/output/pathway_enrichment/pe
```

Output: Results table in `output/pathway_enrichment/pe`

#### c. Topology-Based Analysis via SPIA

Paper: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2732297/

Prerequisites:

-   Install the following R libraries:
    -   [`SPIA`](https://bioconductor.org/packages/release/bioc/html/SPIA.html)

This recipe assumes that the module of interest is the 100<sup>th</sup> module (as specified using the `-i` parameter):

Output: Results table in `output/pathway_enrichment/spia`
