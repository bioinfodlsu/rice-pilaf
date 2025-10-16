# ===========
# CORE LOGIC
# ===========

# Go through each symbol associated with gene
# We use the word "symbol" to refer to the different accession IDs and gene symbols.

# - The symbol should not be "sandwiched" between alphanumeric characters
#   - This is to disambiguate PK1 from PK12
#   - This is also so that PK1 in (PK1) can still be matched

# - The symbol should not be after sp. or spp. (or their variants w/o periods)
#   - This is to disambiguate gene symbols from taxonomic nomenclature

# - If the symbol has 2 letters only, make matching case-sensitive
#   - This is to disambiguate go from GO
#   - Otherwise, make matching case-insensitive

# - If the symbol is an English word, make matching case-sensitive
#   - This is to disambiguate coin from COIN (cold inducible zinc finger protein)
#   - We are using the English word corpus from the NLTK (if available)

# - We have to replace some symbols for better disambiguation (based on a manually compiled list)
# - We have to exclude some symbols under certain contexts (based on a manually compiled list)

import csv
import os
import pickle
from collections import defaultdict

import nltk
import pandas as pd
import regex as re

try:
    from nltk.corpus import words as nltk_words  # type: ignore
    try:
        ENG_WORDS = set(nltk_words.words())  # may raise LookupError
    except LookupError:
        ENG_WORDS = set()
except Exception:
    ENG_WORDS = set()

# Globals for the new two-file format
# ABSTRACTS_MAP structure: PMID -> {'title': ..., 'abstract': ...}
ABSTRACTS_MAP = {}
ANNOTATIONS_FILE = None  # path to annotations (per-entity) file
VALIDATE_OFFSETS = False
AUTO_CORRECT_OFFSETS = False
AUTO_CORRECT_DISTANCE = 5  # maximum distance (chars) from annotated start to accept automatic correction


def load_abstracts_file(abstracts_file):
    """
    Load abstracts TSV into a dict mapping PMID -> {'title': str, 'abstract': str}.

    The abstracts file is expected to have at least three columns: PMID, Title, Abstract.
    This function is tolerant to tab- or whitespace-separated formats and will try
    to preserve Title (which may contain spaces) by splitting with maxsplit=2.
    """
    pmid_to_text = {}
    with open(abstracts_file, encoding="utf8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.strip():
                continue
            # Try tab split first
            parts = line.split("\t")
            if len(parts) < 3:
                # Fallback: split on whitespace but keep at most 3 parts (PMID, Title, Abstract)
                parts = line.split(None, 2)

            if len(parts) >= 3:
                pmid = parts[0].strip()
                title = parts[1].strip()
                abstract = parts[2].strip()
                pmid_to_text[pmid] = {"title": title, "abstract": abstract}
    return pmid_to_text


def validate_offsets(annotations_path: str, abstracts_map: dict, max_errors: int = 20):
    """Validate that (start, stop) slices match the 'Entity' text in title/abstract."""
    bad = []
    try:
        with open(annotations_path, encoding="utf-8") as f:
            for i, raw in enumerate(f, 1):
                if not raw.strip():
                    continue
                try:
                    info = parse_annotation_line_info(raw)
                except Exception:
                    continue
                pmid = info.get("PMID", "")
                loc = (info.get("Location") or "").lower()
                text = abstracts_map.get(pmid, {}).get(loc, "")
                s, e = info.get("start", -1), info.get("stop", -1)
                expected = info.get("Entity", "")
                got = text[s:e] if isinstance(s, int) and isinstance(e, int) and 0 <= s <= e <= len(text) else ""
                if got != expected:
                    bad.append((i, pmid, loc, s, e, expected, got))
                    if len(bad) >= max_errors:
                        break
    except FileNotFoundError:
        return [("FILE_NOT_FOUND", annotations_path)]
    return bad


def parse_annotation_line(line):
    """Parse an annotation line and return (PMID, Type, score).

    Supports both the old single-file format (10+ tab-separated columns)
    and the new per-entity annotation format (PMID, Location, Entity, Type, start, stop, score).
    """
    info = parse_annotation_line_info(line)
    return info["PMID"], info.get("Type"), info.get("score")


def parse_annotation_line_info(line):
    """Parse an annotation line and return a dict with keys:
    PMID, Location, Entity, Type, start, stop, score

    Supports the new per-entity annotation format:
      PMID, Location, Entity, Type, start, stop, score [, extra1, extra2]
    If extra trailing empty columns exist, they are ignored.
    """
    parts = line.rstrip("\n").split("\t")
    if len(parts) == 1:
        parts = line.strip().split()
    parts = parts[:9]
    if len(parts) < 7:
        raise ValueError(f"Malformed annotation line (expected >=7 columns): {line!r}")

    pmid, loc, ent, typ, start, stop, score = parts[:7]
    try:
        start_i = int(start)
    except Exception:
        start_i = -1
    try:
        stop_i = int(stop)
    except Exception:
        stop_i = -1
    try:
        score_f = float(score)
    except Exception:
        score_f = 0.0

    return {
        "PMID": (pmid or '').strip(),
        "Location": (loc or '').strip(),
        "Entity": (ent or '').strip(),
        "Type": (typ or '').strip(),
        "start": start_i,
        "stop": stop_i,
        "score": score_f,
    }


COLNAMES = ["Gene", "PMID", "Title", "Sentence", "Score"]

SPECIES_LOOKBEHIND = r"(?<!((spp)|(sp)|(spp\.)|(sp\.))\s+)"
ALPHANUMERIC_LOOKBEHIND = "(?<![a-zA-Z0-9])"
ALPHANUMERIC_LOOKAHEAD = "(?![a-zA-Z0-9])"


def perform_single_query(
    query_string, annotated_abstracts, ignore_case=True, symbol=None
):
    df = pd.DataFrame(columns=COLNAMES)

    query_regex = re.compile(query_string, re.IGNORECASE)
    if not ignore_case:
        query_regex = re.compile(query_string)

    print(query_regex)

    pmid_score = defaultdict(lambda: 0)

    global ANNOTATIONS_FILE, ABSTRACTS_MAP
    annotations_path = ANNOTATIONS_FILE if ANNOTATIONS_FILE else annotated_abstracts

    PMIDs_to_be_skipped = []
    with open(annotations_path, "r", encoding="utf8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                info = parse_annotation_line_info(line)
            except Exception:
                continue

            PMID = info.get("PMID")
            Type = info.get("Type")
            score = info.get("score")

            stored = ABSTRACTS_MAP.get(PMID, {"title": "", "abstract": "", "full": ""})

            text_to_match = stored.get("full", "")
            start = info.get("start")
            stop = info.get("stop")
            location = (info.get("Location") or "").lower()

            if start is not None and stop is not None:
                if "title" in location:
                    source = stored.get("title", "")
                else:
                    source = stored.get("abstract", "")

                if source is None:
                    source = ""
                s = max(0, start)
                e = min(len(source), stop)
                if s < e:
                    text_to_match = source[s:e]
                else:
                    text_to_match = source

                if VALIDATE_OFFSETS:
                    entity = info.get("Entity") or ""

                    def _norm(t):
                        return " ".join(str(t).strip().split()).lower()

                    if entity and _norm(entity) != _norm(text_to_match):
                        full_src = stored.get("full", "") or ""
                        try:
                            fs = max(0, start)
                            fe = min(len(full_src), stop)
                            fallback_extracted = full_src[fs:fe] if fs < fe else full_src
                        except Exception:
                            fallback_extracted = ""

                        if entity and _norm(entity) == _norm(fallback_extracted):
                            text_to_match = fallback_extracted
                            print(
                                f"OFFSET_INTERPRETED_AS_FULL PMID={PMID} loc={location} start={start} stop={stop} entity='{entity}' extracted_from_full='{fallback_extracted[:100]}'"
                            )
                        else:
                            print(
                                f"OFFSET_MISMATCH PMID={PMID} loc={location} start={s} stop={e} entity='{entity}' extracted='{text_to_match[:100]}'"
                            )

                            global AUTO_CORRECT_OFFSETS, AUTO_CORRECT_DISTANCE
                            try:
                                orig_start = int(start)
                            except Exception:
                                orig_start = None

                            if AUTO_CORRECT_OFFSETS and entity and orig_start is not None:
                                src = source or ""
                                full_src = full_src if 'full_src' in locals() else stored.get('full', '') or ""

                                matches = []

                                def find_all(haystack, needle):
                                    res = []
                                    if not haystack or not needle:
                                        return res
                                    h = haystack.lower()
                                    n = needle.lower()
                                    start_pos = 0
                                    while True:
                                        idx = h.find(n, start_pos)
                                        if idx == -1:
                                            break
                                        res.append(idx)
                                        start_pos = idx + 1
                                    return res

                                for idx in find_all(src, entity):
                                    matches.append((idx, 'abstract', src[idx: idx + len(entity)]))

                                for idx in find_all(full_src, entity):
                                    matches.append((idx, 'full', full_src[idx: idx + len(entity)]))

                                if matches:
                                    best = None
                                    best_dist = None
                                    for idx, which, matched_text in matches:
                                        try:
                                            dist = abs(idx - orig_start)
                                        except Exception:
                                            dist = None
                                        if dist is not None and (best_dist is None or dist < best_dist):
                                            best_dist = dist
                                            best = (idx, which, matched_text)

                                    if best is not None and best_dist is not None and best_dist <= AUTO_CORRECT_DISTANCE:
                                        bidx, bwhich, bmatched = best
                                        if bwhich == 'abstract':
                                            text_to_match = src[bidx: bidx + len(entity)]
                                            chosen_info = f"abstract@{bidx}"
                                        else:
                                            text_to_match = full_src[bidx: bidx + len(entity)]
                                            chosen_info = f"full@{bidx}"

                                        print(
                                            f"OFFSET_CORRECTED PMID={PMID} loc={location} orig_start={orig_start} chosen={chosen_info} dist={best_dist} entity='{entity}' corrected='{text_to_match}'"
                                        )

            skip_line = False
            if symbol:
                for context in symbols_to_be_excluded.get(symbol, []):
                    if context.lower() in text_to_match.lower():
                        skip_line = True
                        PMIDs_to_be_skipped.append(PMID)
                        break

            if skip_line:
                continue

            if re.search(query_regex, text_to_match):
                if Type == "Gene" and PMID not in PMIDs_to_be_skipped:
                    try:
                        pmid_score[PMID] = max(pmid_score[PMID], float(score))
                    except Exception:
                        continue

    return pmid_score


def construct_query(gene_symbols):
    query_str_ignore_case = ""
    query_str_with_case = ""

    for symbol in gene_symbols:
        if symbol in symbols_to_be_replaced:
            for replacement_symbol in symbols_to_be_replaced[symbol]:
                if len(replacement_symbol) <= 3:
                    query_str_with_case += (
                        f"({SPECIES_LOOKBEHIND}({re.escape(replacement_symbol)}))|"
                    )
                else:
                    query_str_with_case += f"({re.escape(replacement_symbol)})|"
        else:
            if symbol.lower() in ENG_WORDS or symbol in symbols_to_be_excluded:
                if len(symbol) <= 3:
                    query_str_with_case += (
                        f"({SPECIES_LOOKBEHIND}({re.escape(symbol)}))|"
                    )
                else:
                    query_str_with_case += f"({re.escape(symbol)})|"
            else:
                if len(symbol) != 2:
                    if len(symbol) <= 3:
                        query_str_ignore_case += (
                            f"({SPECIES_LOOKBEHIND}({re.escape(symbol)}))|"
                        )
                    else:
                        query_str_ignore_case += f"({re.escape(symbol)})|"
                else:
                    query_str_with_case += (
                        f"({SPECIES_LOOKBEHIND}({re.escape(symbol)}))|"
                    )

    query_str_ignore_case = query_str_ignore_case[:-1]
    query_str_with_case = query_str_with_case[:-1]

    return query_str_ignore_case, query_str_with_case


def create_pubmed_dict_per_gene(gene_symbols, annotated_abstracts, symbol=None):
    query_str_ignore_case, query_str_with_case = construct_query(gene_symbols)

    pmid_score_ignore_case = None
    pmid_score_with_case = None

    if query_str_ignore_case:
        query_str_ignore_case = f"{ALPHANUMERIC_LOOKBEHIND}({query_str_ignore_case}){ALPHANUMERIC_LOOKAHEAD}"
        pmid_score_ignore_case = perform_single_query(
            query_str_ignore_case, annotated_abstracts, ignore_case=True, symbol=symbol
        )
    if query_str_with_case:
        query_str_with_case = (
            f"{ALPHANUMERIC_LOOKBEHIND}({query_str_with_case}){ALPHANUMERIC_LOOKAHEAD}"
        )
        pmid_score_with_case = perform_single_query(
            query_str_with_case, annotated_abstracts, ignore_case=False, symbol=symbol
        )

    pmid_score = {}
    if pmid_score_ignore_case:
        for pmid, score in pmid_score_ignore_case.items():
            pmid_score[pmid] = score

    if pmid_score_with_case:
        for pmid, score in pmid_score_with_case.items():
            if pmid in pmid_score:
                pmid_score[pmid] = max(pmid_score[pmid], score)
            else:
                pmid_score[pmid] = score

    return pmid_score


def get_pubmed_per_gene(accession, gene_symbols, annotated_abstracts, output_directory):
    pmid_score = create_pubmed_dict_per_gene(gene_symbols, annotated_abstracts)
    # Always write a pickle (possibly empty) so downstream batch runner can mark this accession as processed.
    outpath = f"{output_directory}/{accession}.pickle"
    try:
        with open(outpath, "wb") as f:
            pickle.dump(pmid_score, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception:
        # If writing fails, at least create an empty marker file so the runner can detect the attempt.
        try:
            open(outpath, 'a').close()
        except Exception:
            pass


def get_pubmed_for_all_genes(
    gene_index, continue_from, end_at, annotated_abstracts, output_directory
):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(gene_index, encoding="utf8") as f:
        csv_reader = csv.reader(f, delimiter=",")
        next(csv_reader)

        for line in csv_reader:
            iricname = list(filter(None, line[1].strip().split(",")))
            raprepname = list(filter(None, line[3].strip().split(",")))
            rappredname = list(filter(None, line[4].strip().split(",")))

            accessions = line[2].split(",")
            gene_symbols = line[-1][1:-1].split(",")
            gene_symbols = [
                gene_symbol.replace('"', "").replace("'", "").replace("\\", "").strip()
                for gene_symbol in gene_symbols
            ]

            for idx, gene_symbol in enumerate(gene_symbols):
                if gene_symbol.isdigit():
                    gene_symbols[idx - 1] = gene_symbols[idx - 1] + "," + gene_symbol
                    gene_symbols[idx] = ""

                if len(gene_symbol) == 1:
                    gene_symbols[idx] = ""

            gene_symbols = list(filter(None, gene_symbols))

            for accession in accessions:
                accession = accession.strip()

                if accession:
                    if continue_from is not None and accession < continue_from:
                        print(f"Skipping {accession}")
                        break

                    if end_at is not None and accession > end_at:
                        print(f"Ending before {accession}")
                        return

                    get_pubmed_per_gene(
                        accession,
                        gene_symbols
                        + [accession]
                        + iricname
                        + raprepname
                        + rappredname,
                        annotated_abstracts,
                        output_directory,
                    )

                    print(f"Finished parsing entry for {accession}")

    print(f"Finished populating {output_directory}")


# ================
# POST-PROCESSING
# ================


def handle_english_symbols(
    gene_index, continue_from, end_at, annotated_abstracts, output_directory
):
    with open(gene_index, encoding="utf8") as f:
        csv_reader = csv.reader(f, delimiter=",")
        next(csv_reader)

        for line in csv_reader:
            iricname = list(filter(None, line[1].strip().split(",")))
            raprepname = list(filter(None, line[3].strip().split(",")))
            rappredname = list(filter(None, line[4].strip().split(",")))

            accessions = line[2].split(",")
            gene_symbols = line[-1][1:-1].split(",")
            gene_symbols = [
                gene_symbol.replace('"', "").replace("'", "").replace("\\", "").strip()
                for gene_symbol in gene_symbols
            ]

            is_there_english_symbol = False
            for idx, gene_symbol in enumerate(gene_symbols):
                if gene_symbol.lower() in ENG_WORDS:
                    is_there_english_symbol = True

                if gene_symbol.isdigit():
                    gene_symbols[idx - 1] = gene_symbols[idx - 1] + "," + gene_symbol
                    gene_symbols[idx] = ""

                if len(gene_symbol) == 1:
                    gene_symbols[idx] = ""

            if is_there_english_symbol:
                gene_symbols = list(filter(None, gene_symbols))

                for accession in accessions:
                    accession = accession.strip()
                    if accession:
                        if continue_from is not None and accession < continue_from:
                            print(f"Skipping {accession}")
                            break

                        if end_at is not None and accession > end_at:
                            print(f"Ending before {accession}")
                            return

                        get_pubmed_per_gene(
                            accession,
                            gene_symbols
                            + [accession]
                            + iricname
                            + raprepname
                            + rappredname,
                            annotated_abstracts,
                            output_directory,
                        )

                        print(f"Finished parsing entry for {accession}")

    print(f"Finished post-processing handling English gene symbols")


def handle_symbol_replacement(
    gene_index, continue_from, end_at, annotated_abstracts, output_directory
):
    with open(gene_index, encoding="utf8") as f:
        csv_reader = csv.reader(f, delimiter=",")
        next(csv_reader)

        for line in csv_reader:
            iricname = list(filter(None, line[1].strip().split(",")))
            raprepname = list(filter(None, line[3].strip().split(",")))
            rappredname = list(filter(None, line[4].strip().split(",")))

            accessions = line[2].split(",")
            gene_symbols = line[-1][1:-1].split(",")
            gene_symbols = [
                gene_symbol.replace('"', "").replace("'", "").replace("\\", "").strip()
                for gene_symbol in gene_symbols
            ]

            is_there_symbol_to_be_replaced = False
            for idx, gene_symbol in enumerate(gene_symbols):
                if gene_symbol in symbols_to_be_replaced:
                    is_there_symbol_to_be_replaced = True

                if gene_symbol.isdigit():
                    gene_symbols[idx - 1] = gene_symbols[idx - 1] + "," + gene_symbol
                    gene_symbols[idx] = ""

                if len(gene_symbol) == 1:
                    gene_symbols[idx] = ""

            if is_there_symbol_to_be_replaced:
                gene_symbols = list(filter(None, gene_symbols))

                for accession in accessions:
                    accession = accession.strip()
                    if accession:
                        if accession < continue_from:
                            print(f"Skipping {accession}")
                            break

                        if accession > end_at:
                            print(f"Ending before {accession}")
                            return

                        get_pubmed_per_gene(
                            accession,
                            gene_symbols
                            + [accession]
                            + iricname
                            + raprepname
                            + rappredname,
                            annotated_abstracts,
                            output_directory,
                        )

                        print(f"Finished parsing entry for {accession}")

    print(f"Finished post-processing handling gene symbols to be replaced")


def handle_symbol_exclusion(
    gene_index, continue_from, end_at, annotated_abstracts, output_directory
):
    with open(gene_index, encoding="utf8") as f:
        csv_reader = csv.reader(f, delimiter=",")
        next(csv_reader)

        for line in csv_reader:
            iricname = list(filter(None, line[1].strip().split(",")))
            raprepname = list(filter(None, line[3].strip().split(",")))
            rappredname = list(filter(None, line[4].strip().split(",")))

            # Some entries in the accession column consist of multiple accessions
            accessions = line[2].split(",")
            # Remove the opening and closing brackets
            gene_symbols = line[-1][1:-1].split(",")
            gene_symbols = [
                gene_symbol.replace('"', "").replace("'", "").replace("\\", "").strip()
                for gene_symbol in gene_symbols
            ]

            is_there_symbol_to_be_excluded = False
            for idx, gene_symbol in enumerate(gene_symbols):
                if gene_symbol in symbols_to_be_excluded:
                    is_there_symbol_to_be_excluded = True

                if gene_symbol.isdigit():
                    # Handle cases like \\OsAMT1,2\\
                    gene_symbols[idx - 1] = gene_symbols[idx - 1] + "," + gene_symbol
                    gene_symbols[idx] = ""

                if len(gene_symbol) == 1:
                    gene_symbols[idx] = ""

            if is_there_symbol_to_be_excluded:
                gene_symbols = list(filter(None, gene_symbols))

                for accession in accessions:
                    accession = accession.strip()
                    if accession:
                        if accession < continue_from:
                            print(f"Skipping {accession}")
                            break

                        if accession > end_at:
                            print(f"Ending before {accession}")
                            return

                        get_pubmed_per_gene_with_excluded_symbols(
                            accession,
                            gene_symbols
                            + [accession]
                            + iricname
                            + raprepname
                            + rappredname,
                            annotated_abstracts,
                            output_directory,
                        )

                        print(f"Finished parsing entry for {accession}")

    print(f"Finished post-processing handling gene symbols to be excluded")


def get_pubmed_per_gene_with_excluded_symbols(
    accession, gene_symbols, annotated_abstracts, output_directory
):
    # Iterate through every line in annotated abstracts
    # If line matches query without pertinent gene symbol, then include it
    # Else if line matches query with pertinent gene symbol:
    # - If excluded context is present in that line, then exclude it
    # - If excluded context is not present in that line, then include it

    excluded_gene_symbols = []
    included_gene_symbols = []
    for symbol in gene_symbols:
        if symbol in symbols_to_be_excluded:
            excluded_gene_symbols.append(symbol)
        else:
            included_gene_symbols.append(symbol)

    pmid_scores = []
    pmid_scores.append(
        create_pubmed_dict_per_gene(included_gene_symbols, annotated_abstracts)
    )

    for symbol in excluded_gene_symbols:
        pmid_scores.append(
            create_pubmed_dict_per_gene([symbol], annotated_abstracts, symbol)
        )

    pmid_score = pmid_scores[0]
    for pmid_score_dict in pmid_scores[1:]:
        for pmid, score in pmid_score_dict.items():
            if pmid in pmid_score:
                pmid_score[pmid] = max(pmid_score[pmid], score)
            else:
                pmid_score[pmid] = score

    # Always write a pickle (possibly empty) so downstream batch runner can mark this accession as processed.
    outpath = f"{output_directory}/{accession}.pickle"
    try:
        with open(outpath, "wb") as f:
            pickle.dump(pmid_score, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception:
        try:
            open(outpath, 'a').close()
        except Exception:
            pass


def handle_symbol_after_species(
    gene_index, continue_from, end_at, annotated_abstracts, output_directory
):
    with open(gene_index, encoding="utf8") as f:
        csv_reader = csv.reader(f, delimiter=",")
        next(csv_reader)

        for line in csv_reader:
            iricname = list(filter(None, line[1].strip().split(",")))
            raprepname = list(filter(None, line[3].strip().split(",")))
            rappredname = list(filter(None, line[4].strip().split(",")))

            # Some entries in the accession column consist of multiple accessions
            accessions = line[2].split(",")
            # Remove the opening and closing brackets
            gene_symbols = line[-1][1:-1].split(",")
            gene_symbols = [
                gene_symbol.replace('"', "").replace("'", "").replace("\\", "").strip()
                for gene_symbol in gene_symbols
            ]

            is_there_symbol_to_be_processed = False
            for idx, gene_symbol in enumerate(gene_symbols):
                if 0 < len(gene_symbol.strip()) and len(gene_symbol.strip()) <= 3:
                    is_there_symbol_to_be_processed = True

                if gene_symbol.isdigit():
                    # Handle cases like \\OsAMT1,2\\
                    gene_symbols[idx - 1] = gene_symbols[idx - 1] + "," + gene_symbol
                    gene_symbols[idx] = ""

                if len(gene_symbol) == 1:
                    gene_symbols[idx] = ""

            if is_there_symbol_to_be_processed:
                gene_symbols = list(filter(None, gene_symbols))

                for accession in accessions:
                    accession = accession.strip()
                    if accession:
                        if accession < continue_from:
                            print(f"Skipping {accession}")
                            break

                        if accession > end_at:
                            print(f"Ending before {accession}")
                            return

                        get_pubmed_per_gene(
                            accession,
                            gene_symbols
                            + [accession]
                            + iricname
                            + raprepname
                            + rappredname,
                            annotated_abstracts,
                            output_directory,
                        )

                        print(f"Finished parsing entry for {accession}")

    print(
        f"Finished post-processing handling gene symbols after sp., spp., sp, and spp"
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "gene_index_file", help="file containing gene accessions and their common names"
    )
    parser.add_argument(
        "abstracts_file", help="file containing the abstracts (PMID, Title, Abstract)"
    )
    parser.add_argument(
        "annotations_file",
        help="file containing the per-entity annotations (PMID, Location, Entity, Type, start, stop, score)",
    )
    parser.add_argument(
        "symbol_replacement_file",
        help="file containing the replacement for selected symbols",
    )
    parser.add_argument(
        "symbol_exclusion_file",
        help="file containing the symbols that must be excluded under certain contexts",
    )
    parser.add_argument(
        "output_dir",
        help="output directory for the dictionaries with the PubMed IDs of related articles",
    )
    parser.add_argument(
        "--continue_from", required=False, help="first gene to be processed"
    )
    parser.add_argument("--end_at", required=False, help="last gene to be processed")
    parser.add_argument(
        "--validate_offsets",
        action="store_true",
        help="validate that annotated start/stop span matches the Entity text",
    )
    parser.add_argument(
        "--auto_correct_offsets",
        action="store_true",
        help="automatically correct offsets by finding the nearest occurrence of the Entity in the text",
    )
    parser.add_argument(
        "--auto_correct_distance",
        type=int,
        default=50,
        help="maximum character distance from annotated start to accept automatic correction (default: 50)",
    )

    args = parser.parse_args()

    # Set validation flag if requested
    VALIDATE_OFFSETS = bool(args.validate_offsets)
    AUTO_CORRECT_OFFSETS = bool(args.auto_correct_offsets)
    AUTO_CORRECT_DISTANCE = int(args.auto_correct_distance)

    with open(args.symbol_replacement_file) as f:
        symbols_to_be_replaced = {}
        csv_reader_e = csv.reader(f, delimiter="\t")
        for line in csv_reader_e:
            symbol = line[0]
            replacement = line[1].strip().split(",")
            symbols_to_be_replaced[symbol] = replacement

    with open(args.symbol_exclusion_file) as f:
        symbols_to_be_excluded = {}
        csv_reader_e = csv.reader(f, delimiter="\t")
        for line in csv_reader_e:
            symbol = line[0]
            context = line[1].strip().split(",")
            symbols_to_be_excluded[symbol] = context

    # Load abstracts into memory and set the global annotations path
    ABSTRACTS_MAP = load_abstracts_file(args.abstracts_file)
    ANNOTATIONS_FILE = args.annotations_file

    # Now run the processing and post-processing steps (abstracts are in memory)
    get_pubmed_for_all_genes(
        args.gene_index_file,
        args.continue_from,
        args.end_at,
        args.annotations_file,
        args.output_dir,
    )

    handle_symbol_after_species(
        args.gene_index_file,
        args.continue_from,
        args.end_at,
        args.annotations_file,
        args.output_dir,
    )

    handle_english_symbols(
        args.gene_index_file,
        args.continue_from,
        args.end_at,
        args.annotations_file,
        args.output_dir,
    )

    handle_symbol_replacement(
        args.gene_index_file,
        args.continue_from,
        args.end_at,
        args.annotations_file,
        args.output_dir,
    )

    handle_symbol_exclusion(
        args.gene_index_file,
        args.continue_from,
        args.end_at,
        args.annotations_file,
        args.output_dir,
    )
