import pandas as pd
from ..constants import Constants
import re

COLNAMES = ['Gene','PMID','Title','Sentence','Score']

def text_mining_query_search(query_string):
    df = pd.DataFrame(columns=COLNAMES)
    query_regex = re.compile(query_string,re.IGNORECASE)
    with open(Constants.TEXT_MINING_ANNOTATED_ABSTRACTS,'r') as f:
        for line in f:
            if re.search(query_regex,line):
                PMID, Title, Sentence, IsInTitle, Entity, Annotations, Type, start_pos, end_pos, score = line.split(
                    "\t")

                if Type == 'Gene':
                    if Sentence == 'None':
                        Sentence = Title
                    df.loc[len(df.index)] = [Entity,PMID,Title,Sentence,score]

    if len(df.index) > 0:
        return df
    else:
        df.loc[len(df.index)] = ['-']*len(COLNAMES)
        return df
