# Data Preparation

Note that all recipes assume that the working directory is `workflow/scripts`.

## Table of Contents

-   [Mapping OGI and reference-specific accessions](https://github.com/bioinfodlsu/rice-pilaf/blob/main/prepare_data/README.md#mapping-ogi-and-reference-specific-accessions)
    -   [Scripts](https://github.com/bioinfodlsu/rice-pilaf/blob/main/prepare_data/README.md#scripts)
    -   [Recipes](https://github.com/bioinfodlsu/rice-pilaf/blob/main/prepare_data/README.md#recipes)
        -   [Generating the pickled dictionaries mapping the reference-specific accession to their respective OGIs](https://github.com/bioinfodlsu/rice-pilaf/blob/main/prepare_data/README.md#1-generating-the-pickled-dictionaries-mapping-the-reference-specific-accession-to-their-respective-ogis)
-   [Coexpression Network](https://github.com/bioinfodlsu/rice-pilaf/blob/main/prepare_data/README.md#coexpression-network)
    -   [Scripts](https://github.com/bioinfodlsu/rice-pilaf/blob/main/prepare_data/README.md#scripts-1)
    -   [Recipes](https://github.com/bioinfodlsu/rice-pilaf/blob/main/prepare_data/README.md#recipes-1)
        -   [Detecting modules via FOX](https://github.com/bioinfodlsu/rice-pilaf/blob/main/prepare_data/README.md#1-detecting-modules-via-fox)
        -   Detecting modules via DEMON

## Mapping OGI and reference-specific accessions

### Scripts

#### 1. `generate-ogi-dicts.py`

This script generates pickled dictionaries that map reference-specific accessions to their respective ortholog gene indices (OGIs), as obtained from the [Rice Gene Index](https://riceome.hzau.edu.cn/download.html).

```
python generate-ogi-dicts.py input_dir output_dir
```

| Argument     | Description                                                                                                      | Note                                                                                                                                                                                                                                                        |
| ------------ | ---------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `input_dir`  | Directory containing the gene ID mapping from RGI                                                                | The OGI files `core.ogi`, `dispensable.ogi`, and `specific.ogi` should be in this directory.                                                                                                                                                                |
| `output_dir` | Output directory for the pickled dictionaries mapping the reference-specific accessions to their respective OGIs | The filename convention for the pickled dictionaries is `<reference>_to_ogi.pickle`, where `reference` is the abbreviation of the reference. For consistency with the app, Nipponbare is abbreviated as `Nb` (not `Nip`, which is the abbreviation in RGI). |

### Recipes

#### 1. Generating the pickled dictionaries mapping the reference-specific accession to their respective OGIs

```
python generate-ogi-dicts.py ../../../data/gene_ID_mapping_fromRGI ../../../data/ogi_mapping
```

Output: `ARC_to_ogi.pickle`, `Azu_to_ogi.pickle`, etc. in `../../../data/ogi_mapping`.

## Coexpression Network

### Scripts

#### 1. `convert-to-int-edge-list.py`

This script converts an edge list with string node labels to an edge list with integer node labels. The first node in the list is labeled `0` and so on.

```
python convert-to-int-edge-list.py input_edge_list_file output_dir
```

| Argument          | Description                                                                                                                                                                                  | Note                                                                                   |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `input_edge_list` | Text file corresponding to the edge list where the node labels are strings                                                                                                                   | The node labels in each line should be separated by a tab (`\t`).                      |
| `output_dir`      | Output directory containing (1) the edge list with the node labels converted to integers and (2) a pickled dictionary mapping the integer node labels to their respective string node labels | If `input_edge_list` contains weights, the weights will not be included in the output. |

#### 3. `restore-node-labels-in-modules.py`

This scripts relabels the nodes in a module list such that the original (string) node labels are restored.

```
python restore-node-labels-in-modules.py module_list_file mapping_file module_list_dir
```

| Argument           | Description                                                                                                | Note                                                                                               |
| ------------------ | ---------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `module_list_file` | Text file corresponding to a module list (where the node labels are integers)                              | Each line corresponds to a module, and the node labels in each line are separated by a tab (`\t`). |
| `mapping_file`     | Pickled dictionary that maps the integer node labels to the (original) string labels                       |
| `module_list_dir`  | Output directory for the module list where the nodes have been relabeled to their (original) string labels |
| `algo`             | Name of community detection algorithm used to detect the modules                                           | This will be reflected in the filename of the output file.                                         |

### Recipes

#### 1. Detecting Modules via FOX

Paper: https://dl.acm.org/doi/10.1145/3404970

Prerequisites:

-   Download the `LazyFox` binary from this [repository](https://github.com/TimGarrels/LazyFox) and save it in the working directory `workflow/scripts`

As mentioned in the LazyFox [paper](https://peerj.com/articles/cs-1291/), running LazyFox with a queue size of 1 and a thread count of 1 is equivalent to running the original FOX algorithm.

```
python convert-to-int-edge-list.py ../../../data/networks/OS-CX.txt ../../../data/networks-modules/OS-CX
./LazyFox --input-graph ../../../data/networks-modules/OS-CX/int-edge-list.txt --output-dir temp --queue-size 1 --thread-count 1 --disable-dumping
mv temp/CPP*/iterations/*.txt ../../../data/networks-modules/OS-CX/fox-int-module-list.txt
rm -r temp
python restore-node-labels-in-modules.py ../../../data/networks-modules/OS-CX/fox-int-module-list.txt ../../../data/networks-modules/OS-CX/int-edge-list-node-mapping.pickle ../../../data/networks-modules/OS-CX fox
```

Output: `fox-module-list.txt` in `../../../data/networks-modules/OS-CX`
