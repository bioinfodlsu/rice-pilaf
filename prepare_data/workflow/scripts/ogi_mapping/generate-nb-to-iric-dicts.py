import csv
import os
import pickle


def separate_paralogs(genes):
    if "," in genes:
        paralogs = genes.split(",")
        return paralogs

    return [genes]


def generate_dict(ogi_file, mapping_dict):
    with open(ogi_file) as f:
        csv_reader = csv.reader(f, delimiter="\t")

        # Skip header row
        next(csv_reader, None)

        for row in csv_reader:
            MSU_ACCESSION = 1
            IRIC_ACCESSION = 2

            msu = row[MSU_ACCESSION].strip()
            iric = row[IRIC_ACCESSION].strip()

            if msu != "." and iric != ".":
                for msu_id, iric_id in zip(
                    separate_paralogs(msu), separate_paralogs(iric)
                ):
                    if msu_id != "" and iric_id != "":
                        mapping_dict[msu_id] = iric_id


def export_mapping_dict(mapping_dict, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f"{output_dir}/msu_to_iric.pickle", "wb") as f:
        pickle.dump(mapping_dict, f, protocol=pickle.HIGHEST_PROTOCOL)


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

    mapping_dict = {}
    for file in os.listdir(args.input_dir):
        generate_dict(f"{args.input_dir}/{file}", mapping_dict)
        print(f"Generated dictionary for {args.input_dir}/{file}")

    export_mapping_dict(mapping_dict, args.output_dir)
