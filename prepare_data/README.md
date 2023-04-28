# Data Preparation Scripts

## Mapping OGI and reference-specific accessions

### 1. `generate-ogi-dicts.py`

This script generates pickled dictionaries that map reference-specific accessions to their respective ortholog gene indices (OGIs), as obtained from the [Rice Gene Index](https://riceome.hzau.edu.cn/download.html).

The command to run the script is as follows:

```
python generate-ogi-dicts.py input_dir output_dir
```

-   `input_dir` is the directory containing the gene ID mapping from RGI. The OGI files `core.ogi`, `dispensable.ogi`, and `specific.ogi` should be in this directory.
-   `output_dir` is the output directory for the pickled dictionaries mapping the reference-specific accessions to their respective OGIs. The filename convention for the pickled dictionaries is as follows: `<reference>_to_ogi.pickle`, where `reference` is the abbreviation of the reference. Note that, for consistency with the app, some of the abbreviations deviate from those in RGI:
    -   Nipponbare is abbreviated as `Nb` (not `Nip`)
    -   CHAO MEO::IRGC 80273-1 is abbreviated as `CHAO` (not `CMeo`)

💡 Assuming that the working directory is `workflow/scripts`, the command to run it is as follows:

```
python generate-ogi-dicts.py ../../../data/gene_ID_mapping_fromRGI ../../../data/ogi_mapping
```

## Coexpression Network

⚠️ **IMPORTANT**: The recipes here should be executed sequentially.

### 1. `convert-to-int-edge-list.py`

This script converts an edge list with string node labels to an edge list with integer node labels. The first node in the list is labeled `0` and so on.

The command to run the script is as follows:

```
python convert-to-int-edge-list.py input_edge_list_file output_dir
```

-   `input_edge_list` is the text file corresponding to the edge list where the node labels are strings. The node labels in each line should be separated by a tab (`\t`).
-   `output_dir` is the output directory containing the following:
    -   The edge list with the node labels converted to integers. Note that, if `input_edge_list` contains weights, the weights will not be included in the output
    -   A pickled dictionary mapping the integer node labels to their respective string node labels

💡 Assuming that the working directory is `workflow/scripts`, the command to run it is as follows:

```
python convert-to-int-edge-list.py ../../../data/networks/OS-CX.txt ../../../data/networks-modules/OS-CX
```

### 2. Detecting Modules via FOX

This app uses the overlapping community detection algorithm [FOX](https://dl.acm.org/doi/10.1145/3404970) to detect modules in the coexpression network. To run this algorithm, download the `LazyFox` binary from this [repository](https://github.com/TimGarrels/LazyFox). As mentioned in the LazyFox [paper](https://peerj.com/articles/cs-1291/), running LazyFox with a queue size of 1 and a thread count of 1 is equivalent to running the original FOX algorithm.

Note that:

-   Running the `LazyFox` binary requires a Linux operating system.
-   The input should be an edge list with integer node labels.

💡 Assuming that the `LazyFox` binary is saved in `workflow/scripts` (together with the Python scripts for data preparation) and the working directory is also `workflow/scripts`, the recipe to run it is as follows:

```
./LazyFox --input-graph ../../../data/networks-modules/OS-CX/int-edge-list.txt --output-dir temp --queue-size 1 --thread-count 1 --disable-dumping
mv temp/CPP*/iterations/*.txt ../../../data/networks-modules/OS-CX/int-module-list.txt
rm -r temp
```

### 3. `restore-node-labels-in-modules.py`

This scripts relabels the nodes in the module list generated via FOX such that the original (string) node labels are restored.

The command to run the script is as follows:

```
python restore-node-labels-in-modules.py module_list_file mapping_file module_list_dir
```

-   `module_list_file` is the text file corresponding to the module list generated via FOX (where the node labels are integers). Each line corresponds to a module, and the node labels in each line are separated by a tab (`\t`).
-   `mapping_file` is the pickled dictionary that maps the integer node labels to the (original) string labels
-   `module_list_dir` is the output directory for the module list where the nodes have been relabeled to their (original) string labels

💡 Assuming that the working directory is `workflow/scripts`, the command to run it is as follows:

```
python restore-node-labels-in-modules.py ../../../data/networks-modules/OS-CX/int-module-list.txt ../../../data/networks-modules/OS-CX/node-mapping.pickle ../../../data/networks-modules/OS-CX
```
