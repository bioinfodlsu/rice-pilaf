import pickle

import ftfy
import pandas as pd
import rapidfuzz
import regex as re

from ..constants import Constants
from ..file_util import *
from ..general_util import *
from ..links_util import *

COLNAMES = ["Gene", "MSU ID", "PMID", "Title", "Sentence", "Score"]
SIMILARITY_CUTOFF = 85
MAX_NUM_RESULTS = 100


def get_msu_id(gene, genesymbol_to_msu_mapping):
    try:
        return "<br>".join(
            map(
                get_msu_browser_link_single_str, genesymbol_to_msu_mapping[gene.lower()]
            )
        )
    except KeyError:
        return NULL_PLACEHOLDER


def sanitize_text(text):
    # Sanitization of HTML tags should come first
    text = re.sub(r"<\s+", "<", text)
    text = re.sub(r"\s+>", ">", text)
    text = re.sub(r"</\s+", "</", text)
    text = re.sub(r"(?<!</\w+)>\s+", ">", text)

    text = re.sub(r"\s+<su", "<su", text)

    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    text = re.sub(r"\[\s+", "[", text)
    text = re.sub(r"\s+\]", "]", text)

    text = re.sub(r"-\s+", "-", text)
    text = re.sub(r"\s+-", "-", text)

    text = re.sub(r"\s+\.", ".", text)
    text = re.sub(r"\s+,", ",", text)
    text = re.sub(r"\s+:", ":", text)
    text = re.sub(r"\s+;", ";", text)

    text = ftfy.fix_text(text)

    return text


def addl_sanitize_gene(text):
    text = re.sub(r"<$", "", text)

    return text


def addl_sanitize_for_bold(text):
    text = re.sub(r"</b$", "</b>", text)
    text = re.sub(r"<</b>\s+/\s+i>", "</b></i>", text)

    return text


def find_index_space_before(index, text):
    while index > 0 and text[index] != " ":
        index -= 1

    return index


def find_index_space_after(index, text):
    while index < len(text) - 1 and text[index] != " ":
        index += 1

    return index


def display_aligned_substring_in_bold(text, similarity):
    before_match = text[: find_index_space_before(similarity.dest_start, text)]
    match = text[
        find_index_space_before(similarity.dest_start, text) : find_index_space_after(
            similarity.dest_end, text
        )
    ]
    after_match = text[find_index_space_after(similarity.dest_end, text) :]

    text = before_match
    if before_match[:-1] == " " or match[0] == " ":
        text += " "
    text += f"<b>{match}</b>"
    if after_match[0] == " ":
        text += " "
    text += after_match

    return text


def text_mining_query_search(query_string, genomic_intervals, filter_gene_ids):
    # Make case-insensitive and remove starting and trailing spaces
    query_string = query_string.lower().strip()

    text_mining_path = get_path_to_text_mining_temp(
        Constants.TEMP_TEXT_MINING, shorten_name(query_string)
    )
    make_dir(text_mining_path)

    if filter_gene_ids:
        text_mining_path = f"{text_mining_path}/{shorten_name(convert_text_to_path(genomic_intervals))}.csv"
    else:
        text_mining_path = f"{text_mining_path}/unfiltered.csv"

    if path_exists(text_mining_path):
        return pd.read_csv(text_mining_path)

    df = pd.DataFrame(columns=COLNAMES)
    pubmed_matches = set()
    pubmed_matches_100 = set()

    with open(
        Constants.TEXT_MINING_ANNOTATED_ABSTRACTS, "r", encoding="utf8"
    ) as f, open(f"{Constants.MSU_MAPPING}/genesymbol_to_msu.pickle", "rb") as g:
        genesymbol_mapping = pickle.load(g)

        # Skip header row
        next(f)
        for line in f:
            similarity = rapidfuzz.fuzz.partial_ratio_alignment(
                query_string, line.lower(), score_cutoff=SIMILARITY_CUTOFF
            )

            try:
                # Display the matching substring in bold
                line = display_aligned_substring_in_bold(line, similarity)

                if similarity.score > 0:
                    try:
                        PMID, Title, Sentence, _, Entity, _, Type, _, _, _ = map(
                            sanitize_text, line.split("\t")
                        )

                    except Exception as e:
                        while True:
                            # Sometimes there is a newline in the abstract, which causes a literal line break
                            # in the CSV file
                            prev_line = line
                            try:
                                next_line = next(f)
                                line = prev_line.strip() + " " + next_line.strip()
                            except StopIteration:
                                break

                            try:
                                PMID, Title, Sentence, _, Entity, _, Type, _, _, _ = (
                                    map(sanitize_text, line.split("\t"))
                                )

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

                    if Type == "Gene":
                        if Sentence == "None":
                            Sentence = Title

                        # If the Type is the one containing the aligned substring, then no bold substring is displayed to the user
                        # We resort to parsing the string again, but, this time, excluding the Type
                        if (
                            "<b>" not in Title
                            and "<b>" not in Sentence
                            and "<b>" not in Entity
                        ):
                            title_sim = rapidfuzz.fuzz.partial_ratio_alignment(
                                query_string,
                                Title.lower(),
                                score_cutoff=SIMILARITY_CUTOFF,
                            )
                            sentence_sim = rapidfuzz.fuzz.partial_ratio_alignment(
                                query_string,
                                Sentence.lower(),
                                score_cutoff=SIMILARITY_CUTOFF,
                            )
                            entity_sim = rapidfuzz.fuzz.partial_ratio_alignment(
                                query_string,
                                Entity.lower(),
                                score_cutoff=SIMILARITY_CUTOFF,
                            )

                            max_sim = max(
                                title_sim.score, sentence_sim.score, entity_sim.score
                            )
                            if max_sim == title_sim.score:
                                Title = display_aligned_substring_in_bold(
                                    Title, title_sim
                                )
                            elif max_sim == sentence_sim.score:
                                Sentence = display_aligned_substring_in_bold(
                                    Sentence, sentence_sim
                                )
                            else:
                                Entity = display_aligned_substring_in_bold(
                                    Entity, entity_sim
                                )

                        Gene = get_msu_id(Entity, genesymbol_mapping)

                        pubmed_matches.add(PMID)
                        df.loc[len(df.index)] = [
                            Entity,
                            Gene,
                            PMID,
                            Title,
                            Sentence,
                            similarity.score,
                        ]

                        if similarity.score == 100:
                            pubmed_matches_100.add(PMID)

                        if len(pubmed_matches_100) == MAX_NUM_RESULTS:
                            break

            except:
                pass

    if filter_gene_ids:
        with open(f"{Constants.MSU_MAPPING}/genesymbol_to_msu.pickle", "rb") as f:
            genesymbol_mapping = pickle.load(f)
            filter_gene_ids = list(
                map(get_msu_browser_link_single_str, filter_gene_ids)
            )
            df = df[df["MSU ID"].isin(filter_gene_ids)]

    df["PMID"] = get_pubmed_link(df, "PMID")
    df = df.sort_values("Score", ascending=False)
    df = df.drop(columns=["Score"])

    if len(df.index) == 0:
        df = create_empty_df_with_cols(COLNAMES)
        df = df.drop(columns=["Score"])

    text_mining_path_with_timestamp = append_timestamp_to_filename(text_mining_path)
    df.to_csv(f"{text_mining_path_with_timestamp}", index=False)

    try:
        os.replace(text_mining_path_with_timestamp, text_mining_path)
    except:
        pass

    return df


def is_error(input):
    try:
        if len(input.strip()) == 0:
            return True, "Please enter a query trait/phenotype."
    except:
        pass

    return False, None
