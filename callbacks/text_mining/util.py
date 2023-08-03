import pandas as pd
from ..constants import Constants

def create_text_mining_empty_df():
    return pd.DataFrame({
        'PMID': ['-'],
        'Title': ['-'],
        'Blah': ['-']
    })
def text_mining_query_search(query_string):
    return create_text_mining_empty_df()
