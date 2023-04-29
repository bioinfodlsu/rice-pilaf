# Data Preparation

Note that all recipes assume that the working directory is `workflow/scripts`.

## Table of Contents
- Mapping OGI and reference-specific accessions
   - Scripts
   - Recipes
      -  Generating the pickled dictionaries mapping the reference-specific accession to their respective OGIs
- Coexpression Network
   - Scripts
   - Recipes
      -  Running FOX community detection algorithm
      -  Running DEMON community detection algorithm

## Mapping OGI and reference-specific accessions

### Scripts

#### 1. `generate-ogi-dicts.py`

This script generates pickled dictionaries that map reference-specific accessions to their respective ortholog gene indices (OGIs), as obtained from the [Rice Gene Index](https://riceome.hzau.edu.cn/download.html).

```
python generate-ogi-dicts.py input_dir output_dir
```

Argument | Description | Note
-- | -- | --
`input_dir` | Directory containing the gene ID mapping from RGI | The OGI files `core.ogi`, `dispensable.ogi`, and `specific.ogi` should be in this directory.
`output_dir` | Output directory for the pickled dictionaries mapping the reference-specific accessions to their respective OGIs | The filename convention for the pickled dictionaries is `<reference>_to_ogi.pickle`, where `reference` is the abbreviation of the reference. For consistency with the app, Nipponbare is abbreviated as `Nb` (not `Nip`, which is the abbreviation in RGI).

### Recipes

#### 1. Generating the pickled dictionaries mapping the reference-specific accession to their respective OGIs

```
python generate-ogi-dicts.py ../../../data/gene_ID_mapping_fromRGI ../../../data/ogi_mapping
```

## Coexpression Network

### Scripts

#### 1. `convert-to-int-edge-list.py`

This script converts an edge list with string node labels to an edge list with integer node labels. The first node in the list is labeled `0` and so on.

```
python convert-to-int-edge-list.py input_edge_list_file output_dir
```

Argument | Description | Note
-- | -- | --
`input_edge_list`| Text file corresponding to the edge list where the node labels are strings | The node labels in each line should be separated by a tab (`\t`).
`output_dir` | Output directory containing (1) the edge list with the node labels converted to integers and (2) a pickled dictionary mapping the integer node labels to their respective string node labels | If `input_edge_list` contains weights, the weights will not be included in the output.

### 3. `restore-node-labels-in-modules.py`

This scripts relabels the nodes in a module list such that the original (string) node labels are restored.

```
python restore-node-labels-in-modules.py module_list_file mapping_file module_list_dir
```

Argument | Description | Note
-- | -- | --
`module_list_file` | Text file corresponding to a module list (where the node labels are integers) | Each line corresponds to a module, and the node labels in each line are separated by a tab (`\t`).
`mapping_file` | Pickled dictionary that maps the integer node labels to the (original) string labels | 
`module_list_dir` | Output directory for the module list where the nodes have been relabeled to their (original) string labels

### Recipes

#### 1. Detecting Modules via FOX
Paper: https://dl.acm.org/doi/10.1145/3404970
Prerequisites:
- Download the `LazyFox` binary from this [repository](https://github.com/TimGarrels/LazyFox) and save it in the working directory `workflow/scripts`

To run this algorithm, download the . As mentioned in the LazyFox [paper](https://peerj.com/articles/cs-1291/), running LazyFox with a queue size of 1 and a thread count of 1 is equivalent to running the original FOX algorithm.

```
python convert-to-int-edge-list.py ../../../data/networks/OS-CX.txt ../../../data/networks-modules/OS-CX
./LazyFox --input-graph ../../../data/networks-modules/OS-CX/int-edge-list.txt --output-dir temp --queue-size 1 --thread-count 1 --disable-dumping
mv temp/CPP*/iterations/*.txt ../../../data/networks-modules/OS-CX/int-module-list.txt
rm -r temp
python restore-node-labels-in-modules.py ../../../data/networks-modules/OS-CX/int-module-list.txt ../../../data/networks-modules/OS-CX/node-mapping.pickle ../../../data/networks-modules/OS-CX
```
