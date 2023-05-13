# Data and resources used in this app
## Genome and annotations
Reference genome assembly and genome annotations of the Nipponbare and other populations were obtained
from [Rice Gene Index](https://riceome.hzau.edu.cn/download.html)

## Genome alignments for lift-over
Whole-genome pairwise alignment between Nippbonbare and another reference was computed using [LAST version 1449](https://gitlab.com/mcfrith/last) 
using the following recipe. 
```
lastdb -P4 -uNEAR Nipponbare_db Nipponbare.fasta.gz
last-train -P8 --revsym -E0.05 -C2 --sample-number=500 Nibbonbare_db otherref.fasta.gz > Nipponbare_otherref.train
lastal -P4 -D1e8 -m20 -C2 --split-f=MAF+ -p Nipponbare_otherref.train Nipponbare_db otherref.fasta.gz > Nipponbare_otherref.maf
last-split -r -m1e-5 Nipponbare_otherref.maf > Nipponbare_otherref.1to1.maf
maf-conver gff Nipponbare_otherref.1to1.maf > Nipponbare_otherref.gff
```
Briefly, the commands perform the following.
`lastdb` constructs an index. 
`last-train` computes alignment scoring parameters suitable for the genome pair being aligned.
`lastal` finds local alignments between Nipponbare and the other reference. 
At this point a segment in Nipponbare may be aligned to multiple segments in the other reference, 
although a segment in the other reference is aligned to at most one segment in Nipponbare.
`last-split` computes takes the alignments from above and finds one best alignment for each segment of Nipponbare,
resulting in a 1-to-1 alignments between the reference pairs.
Finally, `maf-convert` converts the maf alignments into GFF format.

## Co-expression network
Rice gene co-expression network was obtained from [RiceNet](https://www.inetbio.org/ricenet/dl.php?f=OS-CX)

## Enrichment Analysis

### Mapping MSU accessions to KEGG Transcript IDs

MSU accessions are mapped to their respective KEGG transcript IDs using the R package [`riceidconverter`](https://cran.r-project.org/web/packages/riceidconverter/index.html).

For MSU accessions that cannot be mapped by `riceidconverter`, a two-step approach of (a) mapping them to their respective RAP-DB accessions and (b) mapping the RAP-DB accessions to their respective KEGG transcript IDs is followed. The pertinent files were downloaded from the Rice Annotation Project Database (RAP-DB):
- [Mapping MSU accessions to their respective RAP-DB accessions](https://rapdb.dna.affrc.go.jp/download/archive/RAP-MSU_2023-03-15.txt.gz)
- [Mapping RAP-DB accessions to their respective KEGG transcript IDs](https://rapdb.dna.affrc.go.jp/download/archive/irgsp1/IRGSP-1.0_representative_annotation_2023-03-15.tsv.gz)

The files were saved in `../enrichment_analysis/data/rap_db`. This recipe was used to unzip them (assume that the working directory is `../enrichment_analysis`):

```
gzip -dv data/rap_db/RAP-MSU_2023-03-15.txt.gz
gzip -dv data/rap_db/IRGSP-1.0_representative_annotation_2023-03-15.tsv.gz
```

### Mapping MSU accessions to Entrez IDs

The file for mapping MSU accessions to their respective Entrez IDs was obtained from the [Bioinformatics Lab of Fujian Agriculture and Forestry University](https://bioinformatics.fafu.edu.cn/riceidtable/) and saved in `../enrichment_analysis/data/to_entrez`.

### Gene Ontology Annotations

Gene ontology annotations were obtained from three sources:
1. [agriGO v2.0](http://systemsbiology.cau.edu.cn/agriGOv2/download/871_slimGO) – Saved as `../enrichment_analysis/data/go/agrigo.tsv`
2. [RAP-DB](https://rapdb.dna.affrc.go.jp/download/archive/irgsp1/IRGSP-1.0_representative_annotation_2023-03-15.tsv.gz) – Same file used in mapping RAP-DB accessions to their respective KEGG transcript IDs
3. [OryzaBase](https://shigen.nig.ac.jp/rice/oryzabase/gene/download?classtag=GENE_LIST)

The approach of merging the last two data sources (namely RAP-DB and OryzaBase) follows the idea in this [protocol](https://bio-protocol.org/exchange/protocoldetail?id=4446&type=1).

Except for the gene ontology from RAP-DB (saved in `../enrichment_analysis/data/rap_db`), the files were saved in `../enrichment_analysis/data/go`.

### Trait and Plant Ontology Annotations

Trait and plant ontology annotations were obtained from [OryzaBase](https://shigen.nig.ac.jp/rice/oryzabase/gene/download?classtag=GENE_LIST) (same file from which the gene ontology annotations were obtained). 

### KEGG Pathway Data

KGML pathway data files for the organism [`dosa`](https://www.genome.jp/kegg-bin/show_organism?org=dosa) were obtained from KEGG and saved in `..enrichment_analysis/data/kegg_dosa/XML`.
