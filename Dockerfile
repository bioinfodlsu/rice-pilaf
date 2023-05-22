FROM python:3.8

COPY . /app
WORKDIR /app
RUN set -ex && \
    pip install -r requirements.txt
EXPOSE 8050
CMD ["python", "Homepage_dash.py"]