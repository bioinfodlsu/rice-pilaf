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
