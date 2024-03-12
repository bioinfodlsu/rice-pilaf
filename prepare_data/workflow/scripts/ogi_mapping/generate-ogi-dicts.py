import csv
import os
import pickle


def get_rice_variants(path):
    rice_variants = []

    with open(f"{path}/core.ogi") as f:
        csv_reader = csv.reader(f, delimiter="\t")
        for row in csv_reader:
            rice_variants = row
            break

    for i in range(len(rice_variants)):
        # Remove OS prefix
        if rice_variants[i][: len("Os")] == "Os":
            rice_variants[i] = rice_variants[i][len("OS") :]

        # Nipponbare is abbreviated as 'Nb' in the app but 'Nip' in RGI
        if rice_variants[i] == "Nip":
            rice_variants[i] = "Nb"

        # Remove LOC
        if rice_variants[i] == "LOC":
            rice_variants[i] = ""

    rice_variants = [
        rice_variant for rice_variant in rice_variants if rice_variant != ""
    ]

    return rice_variants


def make_mapping_dicts(rice_variants):
    mapping_dicts = []
    for rice_variant in rice_variants:
        mapping_dicts.append({})

    return mapping_dicts


def separate_paralogs(genes):
    if "," in genes:
        paralogs = genes.split(",")
        return paralogs

    return [genes]


def generate_dict(ogi_file, mapping_dicts):
    with open(ogi_file) as f:
        csv_reader = csv.reader(f, delimiter="\t")

        # Skip header row
        next(csv_reader, None)

        for row in csv_reader:
            NB_ACCESSION = 1
            mapping_dict_idx = 0
            for idx in range(NB_ACCESSION, len(row)):

                # Skip indices 2 and 3. They are also Nipponbare accession numbers.
                # But the app uses the Nipponbare accession at index 1
                if not (2 <= idx and idx <= 3):
                    try:
                        gene_str = row[idx].strip()

                        if gene_str != ".":
                            genes = separate_paralogs(row[idx].strip())
                            for gene in genes:
                                if gene != "":
                                    mapping_dicts[mapping_dict_idx][gene] = row[
                                        0
                                    ].strip()

                    except IndexError:
                        break

                    mapping_dict_idx += 1


def pickle_mapping_dicts(path_mapping_dicts, mapping_dicts):
    if not os.path.exists(path_mapping_dicts):
        os.makedirs(path_mapping_dicts)

    for rice_variant, mapping_dict in zip(rice_variants, mapping_dicts):
        pickle_path = f"{path_mapping_dicts}/{rice_variant}_to_ogi.pickle"
        with open(pickle_path, "wb") as f:
            pickle.dump(mapping_dict, f, protocol=pickle.HIGHEST_PROTOCOL)
            print(f"Generated {path_mapping_dicts}/{rice_variant}_to_ogi.pickle")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_dir", help="directory containing the gene ID mapping from RGI"
    )
    parser.add_argument(
        "output_dir",
        help="output directory for the pickled accession-to-OGI mapping dictionaries",
    )

    args = parser.parse_args()

    rice_variants = get_rice_variants(args.input_dir)
    mapping_dicts = make_mapping_dicts(rice_variants)

    for file in os.listdir(args.input_dir):
        generate_dict(f"{args.input_dir}/{file}", mapping_dicts)
        print(f"Generated dictionary for {args.input_dir}/{file}")

    pickle_mapping_dicts(args.output_dir, mapping_dicts)
