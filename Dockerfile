FROM rocker/r-ver:4.3.0

RUN mkdir -p /app
COPY requirements.txt /app
COPY install-libraries.r /app
WORKDIR /app

RUN set -ex

RUN apt-get update
RUN apt-get install -y build-essential libssl-dev libcurl4-openssl-dev libfontconfig1-dev libxml2-dev libffi-dev python3-dev

RUN apt-get install -y python3-pip
RUN pip3 install -r requirements.txt

RUN Rscript --vanilla install-libraries.r

COPY . /app

EXPOSE 8050
CMD ["python3", "Homepage_dash.py"]
