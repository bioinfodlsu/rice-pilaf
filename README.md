# Rice Pilaf
Welcome to Rice Pilaf, a post-GWAS analysis dashboard for rice genomes.

Rice-pilaf takes as input GWAS loci, defined here as genomic intervals obtained from LD-based clumping e.g. using [PLINK](https://zzz.bwh.harvard.edu/plink/clump.shtml).

It infers possible biological mechanisms by evaluating the enrichment of the loci in co-expression modules and in transcription factors.

To do this, it collates (1) pan-genomic, (2) co-expression, (3) epigenomic, and (4) regulatory information from various sources.

## Demo
A demo version can be seen [here](http://165.22.55.49/).

## Running the App Locally

Start by creating a copy of this repository:
- If [git](https://git-scm.com/) is installed, run the following command:
   ```
   git clone https://github.com/bioinfodlsu/rice-pilaf
   ```

- If git is not installed, click the green `Code` button near the top right of the repository and choose [`Download ZIP`](https://github.com/bioinfodlsu/rice-pilaf/archive/refs/heads/main.zip). Once the zipped folder has been downloaded, extract its contents.

### [Recommended] Using the Image Published on GitHub Packages
1. Download [Docker](https://www.docker.com/), a platform for building and running containerized apps.
2. Start the Docker daemon:
   - If you are using Windows, open Docker Desktop to start the daemon.
   - If you are using Ubuntu or Debian, follow the instructions [here](https://docs.docker.com/config/daemon/start/).
3. Pull the Docker image from GitHub's Container registry by running the following command:
   ```
   docker pull ghcr.io/bioinfodlsu/rice-pilaf/app:main
   ```

4. Spin up a container from the Docker image by running the following command:
   ```
   docker run -v path/to/static/in/local:/app/static -p 8050:8050 ghcr.io/bioinfodlsu/rice-pilaf/app:main
   ```

   Replace `path/to/static/in/local` with the path to the `static` folder (i.e., the folder containing the data) in your local machine. It may be more convenient to use the absolute path. If you are using Windows, make sure to replace the backward slashes (`\`) in the path with forward slashes (`/`).
   
5. Open the app by accessing the following URL on your browser:
   ```
   http://localhost:8050/
   ```
   
### Building the Image Locally
1. Download [Docker](https://www.docker.com/), a platform for building and running containerized apps.
2. Start the Docker daemon:
   - If you are using Windows, open Docker Desktop to start the daemon.
   - If you are using Ubuntu or Debian, follow the instructions [here](https://docs.docker.com/config/daemon/start/).
3. Build the Docker image by running the following command on the root of the cloned repository:
   ```
   docker build -t rice-pilaf -f Dockerfile-app .
   ``` 
   
   Note that building the image may take up to 30 minutes in a machine with a 32 GB RAM and 8-core CPU @ 2.30 GHz. 

4. Spin up a container from the Docker image by running the following command:
   ```
   docker run -v path/to/static/in/local:/app/static -p 8050:8050 rice-pilaf
   ```

   Replace `path/to/static/in/local` with the path to the `static` folder (i.e., the folder containing the data) in your local machine. It may be more convenient to use the absolute path. If you are using Windows, make sure to replace the backward slashes (`\`) in the path with forward slashes (`/`).
   
5. Open the app by accessing the following URL on your browser:
   ```
   http://localhost:8050/
   ```

### Running Without Docker
1. Install the necessary Python libraries by running the following command:
   ```
   python -m pip install -r requirements.txt
   ```

2. Install the necessary R libraries by running [`install-libraries-app.r`](https://github.com/bioinfodlsu/rice-pilaf/blob/main/install-libraries-app.r).

3. Run the following command to start the server:
   ```
   python Homepage_dash.py
   ```
   
4. Open the app by accessing the following URL on your browser:
   ```
   http://localhost:8050/
   ```

## Contact
If you have issues, concerns, questions, please contact: Anish Shrestha (anish.shrestha --atmark-- dlsu.edu.ph)
