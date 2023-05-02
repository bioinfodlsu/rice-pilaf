import dash
import dash_bio as dashbio
from dash.dependencies import Input, Output
from dash import html, dcc


from flask import Flask

server = Flask(__name__, static_folder='static')
dash.register_page(__name__, name="Browse Loci", server=server)

layout = html.Div(id='igv-container', children=[
    # dashbio.Igv(
    #      id='igv-Nipponbare',
    #      genome="GCF_001433935.1",
    #      minimumBases=100,
    # )
    dashbio.Igv(
        id='igv-Nipponbare-local',
        reference={
            "id": "GCF_001433935.1",
            "name": "O. sativa IRGSP-1.0 (GCF_001433935.1)",
            "fastaURL": "static/GCF_001433935.1_IRGSP-1.0_genomic.fna.gz",
            "indexURL": "static/GCF_001433935.1_IRGSP-1.0_genomic.fna.gz.fai",
            "compressedIndexURL": "static/GCF_001433935.1_IRGSP-1.0_genomic.fna.gz.gzi",
            "aliasURL": "static/GCF_001433935.1_chromAlias.tab",
            "tracks": [
                                  {
                                      "name": "MSU V7 genes",
                                      "format": "gff3",
                                      "description": " <a target = \"_blank\" href = \"http://rice.uga.edu/\">Rice Genome Annotation Project</a>",
                                      "url": "static/MSU_V7.gff3",
                                      "displayMode": "EXPANDED",
                                      "height": 200
                                  }
            ]
        },
        locus=['chr1:10000-20000']
    )

]
)
