import pandas as pd
from ..constants import Constants
from ..general_util import *
from ..links_util import *
import regex as re
import ftfy
import rapidfuzz

from ..file_util import *


COLNAMES = ['Gene', 'PMID', 'Title', 'Sentence', 'Score']
SIMILARITY_CUTOFF = 75
MAX_NUM_RESULTS = 5000


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


def addl_sanitize_for_bold(text):
    text = re.sub(r'</b$', '</b>', text)
    text = re.sub(r'<</b>\s+/\s+i>', '</b></i>', text)

    return text


def find_index_space_before(index, text):
    while index > 0 and text[index] != ' ':
        index -= 1

    return index


def find_index_space_after(index, text):
    while index < len(text) - 1 and text[index] != ' ':
        index += 1

    return index


def text_mining_query_search(query_string):
    # Make case-insensitive and remove starting and trailing spaces
    query_string = query_string.lower().strip()

    text_mining_path = get_path_to_text_mining_temp(Constants.TEMP_TEXT_MINING)
    make_dir(text_mining_path)

    text_mining_path = f'{text_mining_path}/{shorten_name(query_string)}.csv'

    if path_exists(text_mining_path):
        return pd.read_csv(text_mining_path)

    df = pd.DataFrame(columns=COLNAMES)
    pubmed_matches = set()

    with open(Constants.TEXT_MINING_ANNOTATED_ABSTRACTS, 'r', encoding='utf8') as f:
        for line in f:
            similarity = rapidfuzz.fuzz.partial_ratio_alignment(
                query_string, line.lower(), score_cutoff=SIMILARITY_CUTOFF)

            try:
                # Display the matching substring in bold
                before_match = line[:find_index_space_before(
                    similarity.dest_start, line)]
                match = line[find_index_space_before(
                    similarity.dest_start, line):find_index_space_after(similarity.dest_end, line)]
                after_match = line[find_index_space_after(
                    similarity.dest_end, line):]

                line = before_match
                if before_match[:-1] == ' ' or match[0] == ' ':
                    line += ' '
                line += f'<b>{match}</b>'
                if after_match[0] == ' ':
                    line += ' '
                line += after_match

                if similarity.score > 0:
                    try:
                        PMID, Title, Sentence, _, Entity, _, Type, _, _, _ = map(
                            sanitize_text, line.split('\t'))

                    except Exception as e:
                        while True:
                            # Sometimes there is a newline in the abstract, which causes a literal line break
                            # in the CSV file
                            prev_line = line
                            try:
                                next_line = next(f)
                                line = prev_line.strip() + ' ' + next_line.strip()
                            except StopIteration:
                                break

                            try:
                                PMID, Title, Sentence, _, Entity, _, Type, _, _, _ = map(
                                    sanitize_text, line.split('\t'))

                                break
                            except:
                                pass

                    if PMID in pubmed_matches:
                        continue

                    Entity = addl_sanitize_gene(Entity)
                    Title = Title[:-1]

                    PMID = addl_sanitize_for_bold(PMID)
                    Title = addl_sanitize_for_bold(Title)
                    Sentence = addl_sanitize_for_bold(Sentence)
                    Entity = addl_sanitize_for_bold(Entity)
                    Type = addl_sanitize_for_bold(Type)

                    if PMID == '34199720':
                        print(Sentence)

                    if Type == 'Gene':
                        if Sentence == 'None':
                            Sentence = Title

                        pubmed_matches.add(PMID)
                        df.loc[len(df.index)] = [Entity, PMID,
                                                 Title, Sentence, similarity.score]

                        if df.shape[0] == MAX_NUM_RESULTS:
                            break
            except:
                pass

    df['PMID'] = get_pubmed_link(df, 'PMID')
    df = df.sort_values('Score', ascending=False)
    df = df.drop(columns=['Score'])

    if len(df.index) == 0:
        df = create_empty_df_with_cols(COLNAMES)
        df = df.drop(columns=['Score'])

    df.to_csv(f'{text_mining_path}', index=False)

    return df


def is_error(input):
    try:
        if len(input.strip()) == 0:
            return True, 'Please enter a query trait/phenotype.'
    except:
        pass

    return False, None
