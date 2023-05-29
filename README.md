# Rice Pilaf
Welcome to Rice Pilaf, a post-GWAS analysis dashboard for rice genomes.

Rice-pilaf takes as input GWAS loci, defined here as genomic intervals obtained from LD-based clumping e.g. using [PLINK](https://zzz.bwh.harvard.edu/plink/clump.shtml).

It infers possible biological mechanisms by evaluating the enrichment of the loci in co-expression modules and in transcription factors.

To do this, it collates (1) pan-genomic, (2) co-expression, (3) epigenomic, and (4) regulatory information from various sources.

## Installation
Write me

## Demo
A demo version can be seen [here](http://165.22.55.49/).

## Running the App Locally

**[Optional]** Build the Docker image by running the following command (note that this takes around 30 minutes):
```
docker build -t rice-pilaf .
```

Spin up a container from the Docker image by running the following command:
```
docker run -v path/to/static/in/local:/app/static -p 8050:8050 rice-pilaf
```

Replace `path/to/static/in/local` with the path to the `static` folder (i.e., the folder containing the data) in your local machine. It may be more convenient to use the absolute path.

## Contact
If you have issues, concerns, questions, please contact: Anish Shrestha (anish.shrestha --atmark-- dlsu.edu.ph)
