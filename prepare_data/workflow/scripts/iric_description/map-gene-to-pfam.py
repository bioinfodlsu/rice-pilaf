import pandas as pd
from collections import defaultdict
import json
import os
import pickle


def convert_default_to_vanilla_dict(d):
    """
    Lifted from https://stackoverflow.com/questions/26496831/how-to-convert-defaultdict-of-defaultdicts-of-defaultdicts-to-dict-of-dicts-o
    """
    if isinstance(d, defaultdict):
        d = {k: convert_default_to_vanilla_dict(v) for k, v in d.items()}
    return d


def map_interpro_to_name(pfam_to_name_file, accession_query):
    with open(pfam_to_name_file) as f:
        mapping = json.load(f)
        for entry in mapping:
            if entry["metadata"]["accession"] == accession_query:
                return entry["metadata"]["name"]


def generate_dict(iric_data_file, interpro_to_name_file):
    mapping_dict = defaultdict(set)

    df = pd.read_pickle(iric_data_file)
    idx = 0
    DISPLAY_PROGRESS = 1000
    for _, row in df.iterrows():
        if row["KNETMINER_RICE"] and row["Pfam"]:
            for accession in row["KNETMINER_RICE"]:
                for term in row["Pfam"]:
                    mapping_dict[accession].add(
                        (term, map_interpro_to_name(interpro_to_name_file, term))
                    )

        if idx % DISPLAY_PROGRESS == 0:
            print("Processed", idx + 1, "entries")
        idx += 1

    print("Generated dictionary from IRIC annotation file")

    return convert_default_to_vanilla_dict(mapping_dict)


def export_mapping(mapping, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f"{output_dir}/pfam.pickle", "wb") as handle:
        pickle.dump(mapping, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"Generated {output_dir}/pfam.pickle")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("iric_data_file", help="Pfam annotation file from IRIC")
    parser.add_argument(
        "pfam_to_name_file",
        help="text file mapping Pfam accessions to their respective names",
    )
    parser.add_argument(
        "output_dir",
        help="output directory for the pickled accession-to-Pfam annotation dictionary",
    )

    args = parser.parse_args()

    mapping_dict = generate_dict(args.iric_data_file, args.pfam_to_name_file)
    export_mapping(mapping_dict, args.output_dir)
