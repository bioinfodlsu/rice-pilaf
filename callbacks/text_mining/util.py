import pandas as pd
from ..constants import Constants
from ..general_util import *
from ..links_util import *
import regex as re
import ftfy


COLNAMES = ['Gene', 'PMID', 'Title', 'Sentence', 'Score']


def sanitize_text(text):
    # Sanitization of HTML tags should come first
    text = re.sub(r'<\s+', '<', text)
    text = re.sub(r'\s+>', '>', text)
    text = re.sub(r'</\s+', '</', text)
    text = re.sub(r'(?<!</\w+)>\s+', '>', text)

    text = re.sub(r'\s+<su', '<su', text)

    text = re.sub(r'\(\s+', '(', text)
    text = re.sub(r'\s+\)', ')', text)
    text = re.sub(r'\[\s+', '[', text)
    text = re.sub(r'\s+\]', ']', text)

    text = re.sub(r'-\s+', '-', text)
    text = re.sub(r'\s+-', '-', text)

    text = re.sub(r'\s+\.', '.', text)
    text = re.sub(r'\s+,', ',', text)
    text = re.sub(r'\s+:', ':', text)
    text = re.sub(r'\s+;', ';', text)

    text = ftfy.fix_text(text)

    return text


def addl_sanitize_gene(text):
    text = re.sub(r'<$', '', text)

    return text


def text_mining_query_search(query_string):
    df = pd.DataFrame(columns=COLNAMES)
    query_regex = re.compile(query_string, re.IGNORECASE)
    with open(Constants.TEXT_MINING_ANNOTATED_ABSTRACTS, 'r', encoding='utf8') as f:
        for line in f:
            if re.search(query_regex, line):
                PMID, Title, Sentence, IsInTitle, Entity, Annotations, Type, start_pos, end_pos, score = map(sanitize_text, line.split(
                    '\t'))
                Entity = addl_sanitize_gene(Entity)

                if Type == 'Gene':
                    if Sentence == 'None':
                        Sentence = Title
                    df.loc[len(df.index)] = [
                        Entity, PMID, Title, Sentence, score]

    df['PMID'] = get_pubmed_link(df, 'PMID')

    df = df.sort_values('Score', ascending=False)

    display_cols_in_fixed_dec_places(df, ['Score'])

    if len(df.index) == 0:
        return create_empty_df_with_cols(COLNAMES, html_markdown=True)

    return df


def is_error(input):
    try:
        if len(input.strip()) == 0:
            return True, 'Please enter a query trait/phenotype.'
    except:
        pass

    return False, None
