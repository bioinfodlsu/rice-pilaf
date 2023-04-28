# Data Preparation Scripts

## Mapping OGI and reference-specific accessions

### `generate-ogi-dicts.py`

This script generates pickled dictionaries that map reference-specific accessions to their respective ortholog gene indices (OGIs), as obtained from the [Rice Gene Index](https://riceome.hzau.edu.cn/download.html).

The command to run the script is as follows:

```
python generate-ogi-dicts.py input_dir output_dir
```

-   `input_dir` is the directory containing the gene ID mapping from RGI. The OGI files `core.ogi`, `dispensable.ogi`, and `specific.ogi` should be in this directory.
-   `output_dir` is the output directory for the pickled dictionries mapping the reference-specific accessions to their respective OGIs. The filename convention for the pickled dictionaries is as follows: `<reference>_to_ogi.pickle`, where `reference` is the abbreviation of the reference. Note that, for consistency with the app:
    -   Nipponbare is abbreviated as `Nb` (not `Nip`, which is the abbreviation in RGI)
    -   CHAO MEO::IRGC 80273-1 is abbreviated as `CHAO` (not `CMeo`, which is the abbreviation in RGI)

Relative to the directory where `generate-ogi-dicts.py` is saved, the command to run it is as follows:

```
python generate-ogi-dicts.py ../../../data/gene_ID_mapping_fromRGI  ../../../data/ogi_mapping
```
