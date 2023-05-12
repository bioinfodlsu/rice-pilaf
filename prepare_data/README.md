# Data Preparation

Note that all recipes assume that the working directory is `workflow/scripts`.

## Table of Contents

-   [Mapping OGI and reference-specific accessions](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#mapping-ogi-and-reference-specific-accessions)
    -   [Scripts](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#scripts)
    -   [Recipes](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#recipes)
        -   [Generating the pickled dictionaries mapping the reference-specific accession to their respective OGIs](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#1-generating-the-pickled-dictionaries-mapping-the-reference-specific-accession-to-their-respective-ogis)
-   [Coexpression Network](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#coexpression-network)
    -   [Scripts](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#scripts-1)
    -   [Recipes](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#recipes-1)
        -   [Detecting modules via FOX](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#1-detecting-modules-via-fox)
        -   [Detecting modules via DEMON](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#2-detecting-modules-via-demon)
        -   [Detecting modules via COACH](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#3-detecting-modules-via-coach)
        -   [Detecting modules via ClusterONE](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#4-detecting-modules-via-clusterone)

## Mapping OGI and reference-specific accessions

### SCRIPTS

#### 1. `generate-ogi-dicts.py`

This script generates pickled dictionaries that map reference-specific accessions to their respective ortholog gene indices (OGIs), as obtained from the [Rice Gene Index](https://riceome.hzau.edu.cn/download.html).

```
python generate-ogi-dicts.py input_dir output_dir
```

| Argument     | Description                                                                                                      | Note                                                                                                                                                                                                                                                        |
| ------------ | ---------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `input_dir`  | Directory containing the gene ID mapping from RGI                                                                | The OGI files `core.ogi`, `dispensable.ogi`, and `specific.ogi` should be in this directory.                                                                                                                                                                |
| `output_dir` | Output directory for the pickled dictionaries mapping the reference-specific accessions to their respective OGIs | The filename convention for the pickled dictionaries is `<reference>_to_ogi.pickle`, where `reference` is the abbreviation of the reference. For consistency with the app, Nipponbare is abbreviated as `Nb` (not `Nip`, which is the abbreviation in RGI). |

### RECIPES

#### 1. Generating the pickled dictionaries mapping the reference-specific accession to their respective OGIs

```
python generate-ogi-dicts.py ../../../static/gene_ID_mapping_fromRGI ../../../static/ogi_mapping
```

Output: `ARC_to_ogi.pickle`, `Azu_to_ogi.pickle`, etc. in `../../../static/ogi_mapping`.

## Coexpression Network

### SCRIPTS

### A. Network Utility Scripts (`network_util`)

#### 1. `network_util/convert-to-int-edge-list.py`

This script converts an edge list with string node labels to an edge list with integer node labels. The first node in the list is labeled `0` and so on.

The [recipe for detecting modules via FOX](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#1-detecting-modules-via-fox) requires the edge list to be in this format.

```
python network_util/convert-to-int-edge-list.py input_edge_list_file output_dir
```

| Argument          | Description                                                                                                                                                                                  | Note                                                                                   |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `input_edge_list` | Text file corresponding to the edge list where the node labels are strings                                                                                                                   | The node labels in each line should be separated by a tab (`\t`).                      |
| `output_dir`      | Output directory containing (1) the edge list with the node labels converted to integers and (2) a pickled dictionary mapping the integer node labels to their respective string node labels | If `input_edge_list` contains weights, the weights will not be included in the output. |

### B. Module Detection Utility Scripts (`module_util`)

#### 1. `module_util/generate-mapping-from-networkx-int-edge-graph.py`

This script generates a pickled dictionary that maps the node labels in the `networkx` integer-indexed graph to their (original) string node labels.

Although the edge list accepted by this script has node labels converted to integers, these node labels are cast to strings when loaded as a `networkx` graph. However, the recipes that use the `cdlib` library to perform module detection (e.g., [detecting modules via DEMON](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#2-detecting-modules-via-demon) and [COACH](https://github.com/bioinfodlsu/rice-pilaf/tree/main/prepare_data#3-detecting-modules-via-coach)) require `networkx` graphs with integer-indexed nodes (constructed via [`networkx.convert_node_labels_to_integers`](https://networkx.org/documentation/stable/reference/generated/networkx.relabel.convert_node_labels_to_integers.html)). These integer indices are the keys of the pickled dictionary generated by this script.

```
python module_util/generate-mapping-from-networkx-int-edge-graph.py edge_list_file int_edge_list_node_mapping_file output_dir
```

| Argument                          | Description                                                                                                | Note |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------- | ---- |
| `edge_list_file`                  | Text file corresponding to the edge list with the node labels converted to integers                        |      |
| `int_edge_list_node_mapping_file` | Pickled dictionary that maps the integer node labels to the (original) string labels                       |
| `output_dir`                      | Output directory for the module list where the nodes have been relabeled to their (original) string labels |

#### 2. `module_util/restore-node-labels-in-modules.py`

This script relabels the nodes in a module list such that the (original) string node labels are restored.

```
python module_util/restore-node-labels-in-modules.py module_list_file mapping_file module_list_dir
```

| Argument           | Description                                                                                                | Note                                                                                               |
| ------------------ | ---------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `module_list_file` | Text file corresponding to a module list (where the node labels are integers)                              | Each line corresponds to a module, and the node labels in each line are separated by a tab (`\t`). |
| `mapping_file`     | Pickled dictionary that maps the integer node labels to the (original) string labels                       |
| `module_list_dir`  | Output directory for the module list where the nodes have been relabeled to their (original) string labels |
| `algo`             | Name of community detection algorithm used to detect the modules                                           | This will be reflected in the filename of the output file.                                         |

#### 3. `get-modules-from-clusterone-results`

This script gets the modules from the CSV file generated when ClusterONE is run. In other words, the additional information included in this CSV file, such as the cluster ID, size, p-value, and quality scores are excluded from the generated output file.

```
python module_util/get-modules-from-clusterone-results.py clusterone_results output_dir
```

| Argument             | Description                                                                         | Note                                                                                    |
| -------------------- | ----------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `clusterone_results` | CSV file corresponding to the results of running ClusterONE                         | This assumes that ClusterONE was run with the `--output-format` parameter set to `csv`. |
| `output_dir`         | Output directory for the text file containing only the modules found via ClusterONE |

### C. Module Detection Scripts (`module_detection`)

#### 1. `detect-modules-via-demon`

This script runs the [DEMON community detection algorithm](https://dl.acm.org/doi/10.1145/2339530.2339630).

```
python module_detection/detect-modules-via-demon.py [-epsilon EPSILON] [-min_com_size MIN_COM_SIZE] edge_list_file module_list_dir
```

| Argument          | Description                              | Note                                                                                                                    |
| ----------------- | ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `edge_list_file`  | Text file corresponding to the edge list |                                                                                                                         |
| `module_list_dir` | Output directory for the module list     |
| `epsilon`         | Merging threshold (default = 0.25)       | The default value is the same as in [CDLib](https://appliednetsci.springeropen.com/articles/10.1007/s41109-019-0165-9). |
| `min_com_size`    | Minimum size of a module (default = 3)   | The default value is the same as in [CDLib](https://appliednetsci.springeropen.com/articles/10.1007/s41109-019-0165-9). |

#### 2. `detect-modules-via-coach`

This script runs the [COACH community detection algorithm](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-10-169).

```
python module_detection/detect-modules-via-coach.py [-density_threshold DENSITY_THRESHOLD] [-affinity_threshold AFFINITY_THRESHOLD] [-closeness_threshold CLOSENESS_THRESHOLD] edge_list_file module_list_dir
```

| Argument              | Description                                | Note                                                                                                                    |
| --------------------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| `edge_list_file`      | Text file corresponding to the edge list   |                                                                                                                         |
| `module_list_dir`     | Output directory for the module list       |
| `density_threshold`   | Minimum core density (default = 0.7)       | The default value is the same as in [CDLib](https://appliednetsci.springeropen.com/articles/10.1007/s41109-019-0165-9). |
| `affinity_threshold`  | Maximum core affinity (default = 0.225)    | The default value is the same as in [CDLib](https://appliednetsci.springeropen.com/articles/10.1007/s41109-019-0165-9). |
| `closeness_threshold` | Minimum neighbor closeness (default = 0.5) | The default value is the same as in [CDLib](https://appliednetsci.springeropen.com/articles/10.1007/s41109-019-0165-9). |

### RECIPES

#### 1. Detecting Modules via FOX

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

Output: `fox-module-list.txt` in `../../../static/networks_modules/OS-CX/module_list`

#### 2. Detecting Modules via DEMON

Paper: https://dl.acm.org/doi/10.1145/2339530.2339630

Prerequisites:

-   Install `cdlib`. Instructions can be found [here](https://cdlib.readthedocs.io/en/latest/installing.html).

```
python network_util/convert-to-int-edge-list.py ../../../static/networks/OS-CX.txt ../../../static/networks_modules/OS-CX/mapping
python module_util/generate-mapping-from-networkx-int-edge-graph.py ../../../static/networks_modules/OS-CX/mapping/int-edge-list.txt ../../../static/networks_modules/OS-CX/mapping/int-edge-list-node-mapping.pickle ../../../static/networks_modules/OS-CX/mapping
python module_detection/detect-modules-via-demon.py ../../../static/networks_modules/OS-CX/mapping/int-edge-list.txt ../../../static/networks_modules/OS-CX/temp
python module_util/restore-node-labels-in-modules.py ../../../static/networks_modules/OS-CX/temp/demon-int-module-list.csv ../../../static/networks_modules/OS-CX/mapping/networkx-node-mapping.pickle ../../../static/networks_modules/OS-CX/module_list demon
```

Output: `demon-module-list.txt` in `../../../static/networks_modules/OS-CX/module_list`

#### 3. Detecting Modules via COACH

Paper: https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-10-169

Prerequisites:

-   Install `cdlib`. Instructions can be found [here](https://cdlib.readthedocs.io/en/latest/installing.html).

```
python network_util/convert-to-int-edge-list.py ../../../static/networks/OS-CX.txt ../../../static/networks_modules/OS-CX/mapping
python module_util/generate-mapping-from-networkx-int-edge-graph.py ../../../static/networks_modules/OS-CX/mapping/int-edge-list.txt ../../../static/networks_modules/OS-CX/mapping/int-edge-list-node-mapping.pickle ../../../static/networks_modules/OS-CX/mapping
python module_detection/detect-modules-via-coach.py ../../../static/networks_modules/OS-CX/mapping/int-edge-list.txt ../../../static/networks_modules/OS-CX/temp
python module_util/restore-node-labels-in-modules.py ../../../static/networks_modules/OS-CX/temp/coach-int-module-list.csv ../../../static/networks_modules/OS-CX/mapping/networkx-node-mapping.pickle ../../../static/networks_modules/OS-CX/module_list coach
```

Output: `coach-module-list.txt` in `../../../static/networks_modules/OS-CX/module_list`

#### 4. Detecting Modules via ClusterONE

Paper: https://www.nature.com/articles/nmeth.1938

Prerequisites:

-   Download the ClusterONE JAR file from this [link](https://paccanarolab.org/static_content/clusterone/cluster_one-1.0.jar), and save it in the directory `workflow/scripts/module_detection`.

-   The source code of ClusterONE is also hosted at [GitHub](https://github.com/ntamas/cl1).

```
mkdir -p ../../../static/networks_modules/OS-CX/temp
java -jar cluster_one-1.0.jar --output-format csv ../../../static/networks/OS-CX.txt > ../../../static/networks_modules/OS-CX/temp/clusterone-results.csv
python module_util/get-modules-from-clusterone-results.py ../../../static/networks_modules/OS-CX/temp/clusterone-results.csv ../../../static/networks_modules/OS-CX/module_list
```

Output: `clusterone-module-list.txt` in `../../../static/networks_modules/OS-CX/module_list`
