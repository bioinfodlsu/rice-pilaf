# Data Preparation

All the recipes below assume that the working directory is `workflow/scripts`.

Running the R scripts from the terminal require the [`optparse`](https://cran.r-project.org/web/packages/optparse/index.html) library. It can be installed by running the following command:

```
Rscript -e "install.packages('optparse', repos ='https://cran.rstudio.com/')"
```


## Table of Contents
- [Mapping OGI and Reference-Specific Accessions](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#mapping-ogi-and-reference-specific-accessions)
- [Coexpression Network](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#mapping-ogi-and-reference-specific-accessions)
- [Enrichment Analysis](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#enrichment-analysis)

## Mapping OGI and Reference-Specific Accessions

### 1. Generating the pickled dictionaries mapping the reference-specific accession to their respective OGIs

```
python ogi_mapping/generate-ogi-dicts.py ../../../static/raw_data/gene_ID_mapping_fromRGI ../../../static/app_data/ogi_mapping
```

Output: `ARC_to_ogi.pickle`, `Azu_to_ogi.pickle`, etc. in `../../../static/app_data/ogi_mapping`.

## Coexpression Network

### 0. Data Preparation

This recipe converts the coexpression network to the respective formats required to run the module detection algorithms and generates the required mapping dictionaries to convert across the different network representation formats.

```
python network_util/convert-to-int-edge-list.py ../../../static/raw_data/networks/OS-CX.txt ../../../static/raw_data/networks_modules/OS-CX/mapping
python module_util/generate-mapping-from-networkx-int-edge-graph.py ../../../static/raw_data/networks_modules/OS-CX/mapping/int-edge-list.txt ../../../static/raw_data/networks_modules/OS-CX/mapping/int-edge-list-node-mapping.pickle ../../../static/raw_data/networks_modules/OS-CX/mapping
mkdir -p ../../../static/raw_data/networks_modules/OS-CX/temp/fox
mkdir -p ../../../static/raw_data/networks_modules/OS-CX/temp/clusterone
```

### 1. Detecting Modules via FOX

Paper: https://dl.acm.org/doi/10.1145/3404970

Prerequisites:

-   Download the `LazyFox` binary from this [repository](https://github.com/TimGarrels/LazyFox), and save it in the directory `workflow/scripts/module_detection`.

As mentioned in the LazyFox [paper](https://peerj.com/articles/cs-1291/), running LazyFox with a queue size of 1 and a thread count of 1 is equivalent to running the original FOX algorithm.

```
./LazyFox --input-graph ../../../static/raw_data/networks_modules/OS-CX/mapping/int-edge-list.txt --output-dir temp --queue-size 1 --thread-count 1 --disable-dumping --wcc-threshold {WCC_THRESHOLD}
mv temp/CPP*/iterations/*.txt ../../../static/raw_data/networks_modules/OS-CX/temp/fox/fox-int-module-list-{WCC_THRESHOLD * 100}.txt
rm -r temp
python module_util/restore-node-labels-in-modules.py ../../../static/raw_data/networks_modules/OS-CX/temp/fox/fox-int-module-list-{WCC_THRESHOLD * 100}.txt ../../../static/raw_data/networks_modules/OS-CX/mapping/int-edge-list-node-mapping.pickle ../../../static/raw_data/networks_modules/OS-CX/module_list/fox/{WCC_THRESHOLD * 100} fox
```

Replace `{WCC_THRESHOLD}` with the weighted community clustering (WCC) threshold:
- If `{WCC_THRESHOLD}` is 0.01, then `{WCC_THRESHOLD * 100}` is 1. This is just a convention in the app to avoid having decimal points in the directory and file names.

Output: `fox-module-list.tsv` in `../../../static/raw_data/networks_modules/OS-CX/module_list/fox/{WCC_THRESHOLD * 100}`

### 2. Detecting Modules via DEMON

Paper: https://dl.acm.org/doi/10.1145/2339530.2339630

Prerequisites:

-   Install the following Python library: 
    - [`cdlib`](https://cdlib.readthedocs.io/en/latest/installing.html)

```
python module_detection/detect-modules-via-demon.py -epsilon {EPSILON} ../../../static/raw_data/networks_modules/OS-CX/mapping/int-edge-list.txt ../../../static/raw_data/networks_modules/OS-CX/temp/demon
python module_util/restore-node-labels-in-modules.py ../../../static/raw_data/networks_modules/OS-CX/temp/demon/demon-int-module-list-{EPSILON * 100}.csv ../../../static/raw_data/networks_modules/OS-CX/mapping/networkx-node-mapping.pickle ../../../static/raw_data/networks_modules/OS-CX/module_list/demon/{EPSILON * 100} demon
```

Replace `{EPSILON}` with the merging threshold (epsilon):
- If `{EPSILON}` is 0.25, then `{EPSILON * 100}` is 25. This is just a convention in the app to avoid having decimal points in the directory and file names.

Output: `demon-module-list.tsv` in `../../../static/raw_data/networks_modules/OS-CX/module_list/demon/{EPSILON * 100}`

### 3. Detecting Modules via COACH

Paper: https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-10-169

Prerequisites:

-   Install the following Python library: 
    - [`cdlib`](https://cdlib.readthedocs.io/en/latest/installing.html)

```
python module_detection/detect-modules-via-coach.py -affinity_threshold {AFFINITY_THRESHOLD} ../../../static/raw_data/networks_modules/OS-CX/mapping/int-edge-list.txt ../../../static/raw_data/networks_modules/OS-CX/temp/coach
python module_util/restore-node-labels-in-modules.py ../../../static/raw_data/networks_modules/OS-CX/temp/coach/coach-int-module-list-{AFFINITY_THRESHOLD * 1000}.csv ../../../static/raw_data/networks_modules/OS-CX/mapping/networkx-node-mapping.pickle ../../../static/raw_data/networks_modules/OS-CX/module_list/coach/{AFFINITY_THRESHOLD * 1000} coach
```

Replace `{AFFINITY_THRESHOLD}` with the affinity threshold:
- If `{AFFINITY_THRESHOLD}` is 0.125, then `{AFFINITY_THRESHOLD * 1000}` is 125. This is just a convention in the app to avoid having decimal points in the directory and file names.

Output: `coach-module-list.tsv` in `../../../static/raw_data/networks_modules/OS-CX/module_list/coach/{AFFINITY_THRESHOLD * 1000}`

### 4. Detecting Modules via ClusterONE

Paper: https://www.nature.com/articles/nmeth.1938

Prerequisites:

-   Download the ClusterONE JAR file from this [link](https://paccanarolab.org/static_content/clusterone/cluster_one-1.0.jar), and save it in the directory `workflow/scripts/module_detection`.
-   The source code of ClusterONE is also hosted on [GitHub](https://github.com/ntamas/cl1).

```
java -jar cluster_one-1.0.jar --output-format csv --min-density {MIN_DENSITY} ../../../static/raw_data/networks/OS-CX.txt > ../../../static/raw_data/networks_modules/OS-CX/temp/clusterone/clusterone-results-{MIN_DENSITY * 100}.csv
python module_util/get-modules-from-clusterone-results.py ../../../static/raw_data/networks_modules/OS-CX/temp/clusterone/clusterone-results-{MIN_DENSITY * 100}.csv ../../../static/raw_data/networks_modules/OS-CX/module_list/clusterone/{MIN_DENSITY * 100}
```

Replace `{MIN_DENSITY}` with the minimum density:
- If `{MIN_DENSITY}` is 0.3, then `{MIN_DENSITY * 100}` is 30. This is just a convention in the app to avoid having decimal points in the directory and file names.

Output: `clusterone-module-list.tsv` in `../../../static/raw_data/networks_modules/OS-CX/module_list/clusterone/{MIN_DENSITY * 100}`

### 5. Getting the Genes in the Coexpression Network

```
python network_util/get-nodes-from-network.py ../../../static/raw_data/networks/OS-CX.txt ../../../static/app_data/networks_display/OS-CX
```

Output: `all-genes.txt` in `../../../static/app_data/networks_display/OS-CX`

## Enrichment Analysis

### 0. Data Preparation

Prerequisites:

-   Install the following R library:
    -   [`riceidconverter`](https://cran.r-project.org/web/packages/riceidconverter/index.html)

This recipe maps the MSU accessions used in the app to the target IDs required by the pathway enrichment analysis tools.

```
Rscript --vanilla enrichment_analysis/util/ricegeneid-msu-to-transcript-id.r -g ../../../static/app_data/networks_display/OS-CX/all-genes.txt -o ../../../static/raw_data/enrichment_analysis/temp
python enrichment_analysis/util/msu-to-transcript-id.py ../../../static/raw_data/enrichment_analysis/temp/all-transcript-id.txt ../../../static/raw_data/enrichment_analysis/temp/all-na-transcript-id.txt ../../../static/raw_data/enrichment_analysis/rap_db/RAP-MSU_2023-03-15.txt ../../../static/raw_data/enrichment_analysis/rap_db/IRGSP-1.0_representative_annotation_2023-03-15.tsv data/mapping
python enrichment_analysis/util/transcript-to-msu-id.py ../../../static/raw_data/enrichment_analysis/mapping/msu-to-transcript-id.pickle ../../../static/app_data/enrichment_analysis/mapping
python enrichment_analysis/util/file-convert-msu.py ../../../static/app_data/networks_display/OS-CX/all-genes.txt ../../../static/raw_data/enrichment_analysis/mapping/msu-to-transcript-id.pickle ../../../static/raw_data/enrichment_analysis/all_genes transcript --skip_no_matches
python enrichment_analysis/util/file-convert-msu.py ../../../static/raw_data/networks_modules/OS-CX/module_list/{ALGO}/{PARAM}-module-list.tsv ../../../static/raw_data/enrichment_analysis/mapping/msu-to-transcript-id.pickle ../../../static/app_data/enrichment_analysis/modules/{ALGO}/{PARAM} transcript
```

Replace `algo` with the algorithm (`fox`, `demon`, `coach`, or `clusterone`) and `param` with the name of the directory containing the module list after running the algorithm with the specified parameter:
- For example, if `algo` is `clusterone` and the parameter (minimum density) is 0.3, then `param` is `30`.

Output: 
- TSV files containing KEGG transcript IDs in `../../../static/raw_data/enrichment_analysis/all_genes` and `../../../static/app_data/enrichment_analysis/modules/{ALGO}/{PARAM}/transcript`
- `transcript-to-msu-id.pickle` in `../../../static/app_data/enrichment_analysis/mapping`

This recipe prepares the data needed for gene ontology enrichment analysis:

```
python enrichment_analysis/util/aggregate-go-annotations.py ../../../static/raw_data/enrichment_analysis/go/agrigo.tsv ../../../static/raw_data/enrichment_analysis/go/OryzabaseGeneListAll_20230322010000.txt ../../../static/raw_data/enrichment_analysis/rap_db/IRGSP-1.0_representative_annotation_2023-03-15.tsv ../../../static/raw_data/enrichment_analysis/all_genes/transcript/all-genes.tsv ../../../static/raw_data/mapping/msu-to-transcript-id.pickle ../../../static/raw_data/enrichment_analysis/go
```

Output: `go-annotations.tsv` in `../../../static/raw_data/enrichment_analysis/go`

This recipe prepares the data needed for trait ontology enrichment analysis:

```
python enrichment_analysis/util/aggregate-to-annotations.py ../../../static/raw_data/enrichment_analysis/go/OryzabaseGeneListAll_20230322010000.txt ../../../static/raw_data/enrichment_analysis/to
```

Output: `to-annotations.tsv` and `to-id-to-name.tsv` in `../../../static/raw_data/enrichment_analysis/to`

This recipe prepares the data needed for plant ontology enrichment analysis:

```
python enrichment_analysis/util/aggregate-po-annotations.py ../../../static/raw_data/enrichment_analysis/go/OryzabaseGeneListAll_20230322010000.txt ../../../static/raw_data/enrichment_analysis/po
```

Output: `po-annotations.tsv` and `po-id-to-name.tsv` in `../../../static/raw_data/enrichment_analysis/po`

### 1. Ontology Enrichment Analysis

#### a. Gene Ontology Enrichment Analysis

Prerequisites:

-   Install the following R libraries:
    -   [`GO.db`](https://bioconductor.org/packages/release/data/annotation/html/GO.db.html)
    -   [`clusterProfiler`](https://bioconductor.org/packages/release/bioc/html/clusterProfiler.html)

This recipe assumes that the module of interest is the first module (as specified using the `-i` parameter):

```
Rscript --vanilla enrichment_analysis/ontology_enrichment/go-enrichment.r -g ../../../static/raw_data/networks_modules/OS-CX/module_list/clusterone-module-list.tsv -i 1 -b ../../../static/app_data/networks_display/OS-CX/all-genes.txt -m ../../../static/raw_data/enrichment_analysis/go/go-annotations.tsv -o ../../../static/app_data/enrichment_analysis/output/ontology_enrichment/go
```

Output: Results table and dot plot in `../../../static/app_data/enrichment_analysis/output/ontology_enrichment/go`

#### b. Trait Ontology Enrichment Analysis

Prerequisites:

-   Install the following R library:
    -   [`clusterProfiler`](https://bioconductor.org/packages/release/bioc/html/clusterProfiler.html)

This recipe assumes that the module of interest is the first module (as specified using the `-i` parameter):

```
Rscript --vanilla enrichment_analysis/ontology_enrichment/to-enrichment.r -g ../../../static/raw_data/networks_modules/OS-CX/module_list/clusterone-module-list.tsv -i 1 -b ../../../static/app_data/networks_display/OS-CX/all-genes.txt -m ../../../static/raw_data/enrichment_analysis/to/to-annotations.tsv -t ../../../static/raw_data/enrichment_analysis/to/to-id-to-name.tsv -o ../../../static/app_data/enrichment_analysis/output/ontology_enrichment/to
```

Output: Results table and dot plot in `../../../static/app_data/enrichment_analysis/output/ontology_enrichment/to`

#### c. Plant Ontology Enrichment Analysis

Prerequisites:

-   Install the following R library:
    -   [`clusterProfiler`](https://bioconductor.org/packages/release/bioc/html/clusterProfiler.html)

This recipe assumes that the module of interest is the first module (as specified using the `-i` parameter):

```
Rscript --vanilla enrichment_analysis/ontology_enrichment/po-enrichment.r -g ../../../static/raw_data/networks_modules/OS-CX/module_list/clusterone-module-list.tsv -i 1 -b ../../../static/app_data/networks_display/OS-CX/all-genes.txt -m ../../../static/raw_data/enrichment_analysis/po/po-annotations.tsv -t ../../../static/raw_data/enrichment_analysis/po/po-id-to-name.tsv -o ../../../static/app_data/enrichment_analysis/output/ontology_enrichment/po
```

Output: Results table and dot plot in `../../../static/app_data/enrichment_analysis/output/ontology_enrichment/po`

### 2. Pathway Enrichment Analysis

#### a. Overrepresentation Analysis via clusterProfiler

Prerequisites:

-   Install the following R library:
    -   [`clusterProfiler`](https://bioconductor.org/packages/release/bioc/html/clusterProfiler.html)

This recipe assumes that the module of interest is the first module (as specified using the `-i` parameter):

```
Rscript --vanilla enrichment_analysis/pathway_enrichment/ora-enrichment.r -g ../../../static/raw_data/enrichment_analysis/modules/clusterone/transcript/clusterone-module-list.tsv -i 1 -b ../../../static/raw_data/enrichment_analysis/all_genes/transcript/all-genes.tsv -o ../../../static/app_data/enrichment_analysis/output/pathway_enrichment/ora
```

Output: Results table and dot plot in `../../../static/app_data/enrichment_analysis/output/pathway_enrichment/ora`

#### b. Topology-Based Analysis via Pathway-Express

Paper: https://genome.cshlp.org/content/17/10/1537.long

Prerequisites:

-   Install the following R library:
    -   [`ROntoTools`](https://bioconductor.org/packages/release/bioc/html/ROntoTools.html)

This recipe assumes that the module of interest is the 100<sup>th</sup> module (as specified using the `-i` parameter):

```
Rscript --vanilla enrichment_analysis/pathway_enrichment/pe-enrichment.r -g ../../../static/raw_data/enrichment_analysis/modules/clusterone/transcript/clusterone-module-list.tsv -i 100 -b ../../../static/raw_data/enrichment_analysis/all_genes/transcript/all-genes.tsv -o ../../../static/app_data/enrichment_analysis/output/pathway_enrichment/pe
```

Output: Results table in `../../../static/app_data/enrichment_analysis/output/pathway_enrichment/pe`

This recipe generates additional files needed for the user-facing display of the results on the app:

```
Rscript enrichment_analysis/util/get-genes-in-pathway.r -o ../../../static/raw_data/enrichment_analysis/kegg_dosa/geneset
python enrichment_analysis/util/get-genes-in-pathway-dict.py ../../../static/raw_data/enrichment_analysis/kegg_dosa/geneset/kegg-dosa-geneset.tsv ../../../static/app_data/enrichment_analysis/mapping
wget -O ../../../static/app_data/enrichment_analysis/mapping/kegg-dosa-pathway-names.tsv https://rest.kegg.jp/list/pathway/dosa
```

Output: `kegg-dosa-geneset.pickle` and `kega-dosa-pathway-names.tsv` in `../../../static/app_data/enrichment_analysis/mapping`


#### c. Topology-Based Analysis via SPIA

Paper: https://academic.oup.com/bioinformatics/article/25/1/75/302846

Prerequisites:

-   Install the following R library:
    -   [`SPIA`](https://bioconductor.org/packages/release/bioc/html/SPIA.html)

This recipe assumes that the module of interest is the 100<sup>th</sup> module (as specified using the `-i` parameter) and uses the `dosaSPIA.RData` file generated from by SPIA from the KEGG pathway data files for the organism `dosa` (downloaded on May 11, 2023):

```
Rscript --vanilla enrichment_analysis/pathway_enrichment/spia-enrichment.r -g ../../../static/raw_data/enrichment_analysis/modules/clusterone/transcript/clusterone-module-list.tsv -i 100 -b ../../../static/raw_data/enrichment_analysis/all_genes/transcript/all-genes.tsv -s ../../../static/raw_data/enrichment_analysis/kegg_dosa/SPIA -o ../../../static/app_data/enrichment_analysis/output/pathway_enrichment/spia
```

If you would like to generate `dosaSPIA.RData` yourself, the recipe is given below. Note, however, that you have to supply the KEGG pathway data files for the organism `dosa`; we do not distribute them in compliance with KEGG's licensing restrictions.

```
Rscript --vanilla enrichment_analysis/pathway_enrichment/spia-enrichment.r -g ../../../static/raw_data/enrichment_analysis/modules/clusterone/transcript/clusterone-module-list.tsv -i 100 -b ../../../static/raw_data/enrichment_analysis/all_genes/transcript/all-genes.tsv -p ../../../static/raw_data/enrichment_analysis/kegg_dosa/XML -s ../../../static/raw_data/enrichment_analysis/kegg_dosa/SPIA -o ../../../static/app_data/enrichment_analysis/output/pathway_enrichment/spia
```

Output: Results table in `../../../static/app_data/enrichment_analysis/output/pathway_enrichment/spia`
