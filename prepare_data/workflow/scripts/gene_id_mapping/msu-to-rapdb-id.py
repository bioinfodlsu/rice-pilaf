import os
import pickle
from collections import defaultdict


def load_msu_to_rap(msu_to_rap_dict, rap_to_msu_file):
    with open(rap_to_msu_file) as rap_to_msu:
        for line in rap_to_msu:
            line = line.rstrip()

            rap, msu = line.split("\t")
            msu = msu.split(",")

            for id in msu:
                # Remove ".1" in "LOC_Os01g01019.1"
                id_components = id.split(".")
                id = id_components[0]

                if id != "None" and rap != "None":
                    msu_to_rap_dict[id].add(rap)


def save_msu_rap_mapping(msu_to_rap_dict, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f"{output_dir}/msu_to_rap.pickle", "wb") as handle:
        pickle.dump(msu_to_rap_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"Generated {output_dir}/msu_to_rap.pickle")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "rap_to_msu_file", help="text file mapping RAP to MSU accessions"
    )
    parser.add_argument(
        "output_dir",
        help="output directory for the pickled dictionary mapping MSU accessions to their respective KEGG transcript IDs",
    )

    args = parser.parse_args()

    msu_to_rap_dict = defaultdict(set)

    load_msu_to_rap(msu_to_rap_dict, args.rap_to_msu_file)
    save_msu_rap_mapping(msu_to_rap_dict, args.output_dir)
