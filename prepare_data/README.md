# Data Preparation

Note that all recipes assume that the working directory is `workflow/scripts`.

## Table of Contents

-   [Mapping OGI and reference-specific accessions](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#mapping-ogi-and-reference-specific-accessions)
    -   [Generating the pickled dictionaries mapping the reference-specific accession to their respective OGIs](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#1-generating-the-pickled-dictionaries-mapping-the-reference-specific-accession-to-their-respective-ogis)
-   [Coexpression Network](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#coexpression-network)
    -   [Detecting modules via FOX](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#1-detecting-modules-via-fox)
    -   [Detecting modules via DEMON](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#2-detecting-modules-via-demon)
    -   [Detecting modules via COACH](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#3-detecting-modules-via-coach)
    -   [Detecting modules via ClusterONE](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#4-detecting-modules-via-clusterone)
    -   [Getting the Genes in the Coexpression Network](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#5-getting-the-genes-in-the-coexpression-network)

## Mapping OGI and reference-specific accessions

### 1. Generating the pickled dictionaries mapping the reference-specific accession to their respective OGIs

```
python generate-ogi-dicts.py ../../../static/gene_ID_mapping_fromRGI ../../../static/ogi_mapping
```

Output: `ARC_to_ogi.pickle`, `Azu_to_ogi.pickle`, etc. in `../../../static/ogi_mapping`.

## Coexpression Network

### 1. Detecting Modules via FOX

Paper: https://dl.acm.org/doi/10.1145/3404970

Prerequisites:

-   Download the `LazyFox` binary from this [repository](https://github.com/TimGarrels/LazyFox), and save it in the directory `workflow/scripts/module_detection`.

As mentioned in the LazyFox [paper](https://peerj.com/articles/cs-1291/), running LazyFox with a queue size of 1 and a thread count of 1 is equivalent to running the original FOX algorithm.

```
python network_util/convert-to-int-edge-list.py ../../../static/networks/OS-CX.txt ../../../static/networks_modules/OS-CX/mapping
./LazyFox --input-graph ../../../static/networks_modules/OS-CX/mapping/int-edge-list.txt --output-dir temp --queue-size 1 --thread-count 1 --disable-dumping
mkdir -p ../../../static/networks_modules/OS-CX/temp
mv temp/CPP*/iterations/*.txt ../../../static/networks_modules/OS-CX/temp/fox-int-module-list.txt
rm -r temp
python module_util/restore-node-labels-in-modules.py ../../../static/networks_modules/OS-CX/temp/fox-int-module-list.txt ../../../static/networks_modules/OS-CX/mapping/int-edge-list-node-mapping.pickle ../../../static/networks_modules/OS-CX/module_list fox
```

Output: `fox-module-list.tsv` in `../../../static/networks_modules/OS-CX/module_list`

### 2. Detecting Modules via DEMON

Paper: https://dl.acm.org/doi/10.1145/2339530.2339630

Prerequisites:

-   Install `cdlib`. Instructions can be found [here](https://cdlib.readthedocs.io/en/latest/installing.html).

```
python network_util/convert-to-int-edge-list.py ../../../static/networks/OS-CX.txt ../../../static/networks_modules/OS-CX/mapping
python module_util/generate-mapping-from-networkx-int-edge-graph.py ../../../static/networks_modules/OS-CX/mapping/int-edge-list.txt ../../../static/networks_modules/OS-CX/mapping/int-edge-list-node-mapping.pickle ../../../static/networks_modules/OS-CX/mapping
python module_detection/detect-modules-via-demon.py ../../../static/networks_modules/OS-CX/mapping/int-edge-list.txt ../../../static/networks_modules/OS-CX/temp
python module_util/restore-node-labels-in-modules.py ../../../static/networks_modules/OS-CX/temp/demon-int-module-list.csv ../../../static/networks_modules/OS-CX/mapping/networkx-node-mapping.pickle ../../../static/networks_modules/OS-CX/module_list demon
```

Output: `demon-module-list.tsv` in `../../../static/networks_modules/OS-CX/module_list`

### 3. Detecting Modules via COACH

Paper: https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-10-169

Prerequisites:

-   Install `cdlib`. Instructions can be found [here](https://cdlib.readthedocs.io/en/latest/installing.html).

```
python network_util/convert-to-int-edge-list.py ../../../static/networks/OS-CX.txt ../../../static/networks_modules/OS-CX/mapping
python module_util/generate-mapping-from-networkx-int-edge-graph.py ../../../static/networks_modules/OS-CX/mapping/int-edge-list.txt ../../../static/networks_modules/OS-CX/mapping/int-edge-list-node-mapping.pickle ../../../static/networks_modules/OS-CX/mapping
python module_detection/detect-modules-via-coach.py ../../../static/networks_modules/OS-CX/mapping/int-edge-list.txt ../../../static/networks_modules/OS-CX/temp
python module_util/restore-node-labels-in-modules.py ../../../static/networks_modules/OS-CX/temp/coach-int-module-list.csv ../../../static/networks_modules/OS-CX/mapping/networkx-node-mapping.pickle ../../../static/networks_modules/OS-CX/module_list coach
```

Output: `coach-module-list.tsv` in `../../../static/networks_modules/OS-CX/module_list`

### 4. Detecting Modules via ClusterONE

Paper: https://www.nature.com/articles/nmeth.1938

Prerequisites:

-   Download the ClusterONE JAR file from this [link](https://paccanarolab.org/static_content/clusterone/cluster_one-1.0.jar), and save it in the directory `workflow/scripts/module_detection`.

-   The source code of ClusterONE is also hosted at [GitHub](https://github.com/ntamas/cl1).

```
mkdir -p ../../../static/networks_modules/OS-CX/temp
java -jar cluster_one-1.0.jar --output-format csv ../../../static/networks/OS-CX.txt > ../../../static/networks_modules/OS-CX/temp/clusterone-results.csv
python module_util/get-modules-from-clusterone-results.py ../../../static/networks_modules/OS-CX/temp/clusterone-results.csv ../../../static/networks_modules/OS-CX/module_list
```

Output: `clusterone-module-list.tsv` in `../../../static/networks_modules/OS-CX/module_list`

### 5. Getting the Genes in the Coexpression Network

```
python network_util/get-nodes-from-network.py ../../../static/networks/OS-CX.txt ../../../static/networks_modules/OS-CX
```

Output: `all-genes.txt` in `../../../static/networks_modules/OS-CX`

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

#### c. Plant Ontology Enrichment Analysis

Prerequisites:

-   Install the following R libraries:
    -   [`clusterProfiler`](https://bioconductor.org/packages/release/bioc/html/clusterProfiler.html)

This recipe assumes that the module of interest is the first module (as specified using the `-i` parameter):

```
Rscript --vanilla ontology_enrichment/po-enrichment.r -g ../static/networks_modules/OS-CX/module_list/clusterone-module-list.tsv -i 1 -b ../static/networks_modules/OS-CX/all-genes.txt -m data/po/po-annotations.tsv -t data/po/po-id-to-name.tsv -o data/output/ontology_enrichment/po
```

Output: Results table and dot plot in `output/ontology_enrichment/po`

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

Paper: https://genome.cshlp.org/content/17/10/1537.long

Prerequisites:

-   Install the following R libraries:
    -   [`ROntoTools`](https://bioconductor.org/packages/release/bioc/html/ROntoTools.html)

This recipe assumes that the module of interest is the 100<sup>th</sup> module (as specified using the `-i` parameter):

```
Rscript --vanilla pathway_enrichment/pe-enrichment.r -g data/modules/clusterone/transcript/clusterone-module-list.tsv -i 100 -b data/all_genes/transcript/all-genes.tsv -o data/output/pathway_enrichment/pe
```

Output: Results table in `output/pathway_enrichment/pe`

#### c. Topology-Based Analysis via SPIA

Paper: https://academic.oup.com/bioinformatics/article/25/1/75/302846

Prerequisites:

-   Install the following R libraries:
    -   [`SPIA`](https://bioconductor.org/packages/release/bioc/html/SPIA.html)

This recipe assumes that the module of interest is the 100<sup>th</sup> module (as specified using the `-i` parameter) and uses the `dosaSPIA.RData` file generated from by SPIA from the KEGG pathway data files for the organism `dosa` (downloaded on May 11, 2023):

```
Rscript --vanilla pathway_enrichment/spia-enrichment.r -g data/modules/clusterone/transcript/clusterone-module-list.tsv -i 100 -b data/all_genes/transcript/all-genes.tsv -s data/kegg_dosa/SPIA -o data/output/pathway_enrichment/spia
```

If you would like to generate `dosaSPIA.RData` yourself, the recipe is given below. Note, however, that you have to supply the KEGG pathway data files for the organism `dosa`; we do not distribute them in compliance with KEGG's licensing restrictions.

```
Rscript --vanilla pathway_enrichment/spia-enrichment.r -g data/modules/clusterone/transcript/clusterone-module-list.tsv -i 100 -b data/all_genes/transcript/all-genes.tsv -p data/kegg_dosa/XML -s data/kegg_dosa/SPIA -o data/output/pathway_enrichment/spia
```

Output: Results table in `output/pathway_enrichment/spia`

