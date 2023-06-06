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

### [Recommended] Using the Image Published on GitHub Packages
1. Pull the Docker image from GitHub's Container registry by running the following command:
   ```
   docker pull ghcr.io/bioinfodlsu/rice-pilaf:main
   ```

2. Spin up a container from the Docker image by running the following command:
   ```
   docker run -v path/to/static/in/local:/app/static -p 8050:8050 ghcr.io/bioinfodlsu/rice-pilaf:main
   ```

   Replace `path/to/static/in/local` with the path to the `static` folder (i.e., the folder containing the data) in your local machine. It may be more convenient to use the absolute path. If you are using Windows, make sure to replace the backward slashes (`\`) in the path with forward slashes (`/`).
   
### Building the Image Locally
1. Build the Docker image by running the following command on the root of the cloned repository:
   ```
   docker build -t rice-pilaf .
   ``` 
   
   Note that building the image may take up to 30 minutes in a machine with a 32 GB RAM and 8-core CPU @ 2.30 GHz. 

2. Spin up a container from the Docker image by running the following command:
   ```
   docker run -v path/to/static/in/local:/app/static -p 8050:8050 rice-pilaf
   ```

   Replace `path/to/static/in/local` with the path to the `static` folder (i.e., the folder containing the data) in your local machine. It may be more convenient to use the absolute path. If you are using Windows, make sure to replace the backward slashes (`\`) in the path with forward slashes (`/`).

## Contact
If you have issues, concerns, questions, please contact: Anish Shrestha (anish.shrestha --atmark-- dlsu.edu.ph)
