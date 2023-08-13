import pandas as pd
from ..constants import Constants
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


def text_mining_query_search(query_string):
    df = pd.DataFrame(columns=COLNAMES)
    query_regex = re.compile(query_string, re.IGNORECASE)
    with open(Constants.TEXT_MINING_ANNOTATED_ABSTRACTS, 'r', encoding='utf8') as f:
        for line in f:
            if re.search(query_regex, line):
                PMID, Title, Sentence, IsInTitle, Entity, Annotations, Type, start_pos, end_pos, score = map(sanitize_text, line.split(
                    '\t'))

                if Type == 'Gene':
                    if Sentence == 'None':
                        Sentence = Title
                    df.loc[len(df.index)] = [
                        Entity, PMID, Title, Sentence, score]

    if len(df.index) > 0:
        return df
    else:
        df.loc[len(df.index)] = ['-'] * len(COLNAMES)
        return df
