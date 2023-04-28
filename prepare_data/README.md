# Data Preparation Scripts

## Mapping OGI and reference-specific accessions

### `generate-ogi-dicts.py`

This script generates pickled dictionaries that map reference-specific accessions to their respective ortholog gene indices (OGIs), as obtained from the [Rice Gene Index](https://riceome.hzau.edu.cn/download.html).

The command to run the script is as follows:

```
python generate-ogi-dicts.py input_dir output_dir
```

-   `input_dir` is the directory containing the gene ID mapping from RGI. The OGI files `core.ogi`, `dispensable.ogi`, and `specific.ogi` should be in this directory.
-   `output_dir` is the output directory for the pickled dictionaries mapping the reference-specific accessions to their respective OGIs. The filename convention for the pickled dictionaries is as follows: `<reference>_to_ogi.pickle`, where `reference` is the abbreviation of the reference. Note that, for consistency with the app, some of the abbreviations deviate from those in RGI:
    -   Nipponbare is abbreviated as `Nb` (not `Nip`)
    -   CHAO MEO::IRGC 80273-1 is abbreviated as `CHAO` (not `CMeo`)

Relative to the directory where `generate-ogi-dicts.py` is saved, the command to run it is as follows:

```
python generate-ogi-dicts.py ../../../data/gene_ID_mapping_fromRGI  ../../../data/ogi_mapping
```

## Coexpression Network

### `convert-to-int-edge-list.py`

This script converts an edge list with string node labels to an edge list with integer node labels. The first node in the list is labeled `0` and so on.

The command to run the script is as follows:

```
python convert-to-int-edge-list.py input_edge_list_file output_dir
```

-   `input_edge_list` is the text file corresponding to the edge list where the node labels are strings. The node labels in each line should be separated by a tab (`\t`).
-   `output_dir` is the output directory containing the following:
    -   The edge list with the node labels converted to integers. Note that, if `input_edge_list` contains weights, the weights will not be included in the output
    -   A pickled dictionary mapping the string node labels to their respective integer node labels

Relative to the directory where `generate-ogi-dicts.py` is saved, the command to run it is as follows:

```
python convert-to-int-edge-list.py ../../../data/networks/OS-CX.txt ../../../data/networks-modules/OS-CX
```
