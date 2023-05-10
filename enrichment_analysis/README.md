# Enrichment Analysis Scripts

Note that running the R scripts from the terminal require the `optparse` library. It can be installed by running the following command:

```
RScript -e "install.packages('optparse', repos ='https://cran.rstudio.com/')"
```

```
Rscript util/ricegeneid-msu-to-transcript-id.r -g ../static/networks_modules/OS-CX/all_genes.txt -o data/temp
python util/msu-to-transcript-id.py data/temp/all-transcript-id.txt data/temp/all-na-transcript-id.txt data/rap_db/RAP-MSU_2023-03-15.txt data/rap_db/IRGSP-1.0_representative_annotation_2023-03-15.tsv data/mapping
```
