# Data Preparation Scripts

## Mapping OGI and reference-specific accessions

### `generate-ogi-dicts.py`

This script generates pickled dictionaries that map reference-specific accessions to their respective ortholog gene indices (OGIs), as obtained from the [Rice Gene Index](https://riceome.hzau.edu.cn/download.html).

This script assumes that the OGI files (`core.ogi`, `dispensable.ogi`, and `specific.ogi`) are in the directory `gene_ID_mapping_fromRGI`. The output dictionaries are saved in the directory `data/ogi_mapping` following this file name convention: `<reference>_to_ogi.pickle`, where `reference` is the abbreviation of the reference. Note that, for consistency with the app, Nipponbare is abbreviated as `Nb` (not `Nip`, which is the abbreviation in RGI).
