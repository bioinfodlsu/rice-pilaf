FROM rocker/r-ver:4.3.0

RUN mkdir -p /app
COPY requirements.txt /app
COPY install-libraries.r /app
WORKDIR /app

RUN set -ex 
RUN apt-get update
RUN apt-get install -y \
  build-essential \
  libcurl4-openssl-dev \
  libffi-dev \
  libfontconfig1-dev \
  libssl-dev \
  libxml2-dev \
  python3-dev \
  python3-pip

RUN Rscript --vanilla install-libraries.r
RUN pip3 install -r requirements.txt

COPY . /app

EXPOSE 8050
CMD ["python3", "Homepage_dash.py"]
