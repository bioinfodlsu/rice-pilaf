import os
import pickle
from collections import defaultdict


def convert_transcript_to_msu(transcript_id, transcript_to_msu_files):
    msu = set()
    for file in transcript_to_msu_files:
        with open(file, "rb") as f:
            transcript_to_msu_mapping = pickle.load(f)
            msu = msu.union(transcript_to_msu_mapping[transcript_id])

    return msu


def map_genes_to_pathway(pathway_geneset_file, transcript_to_msu_files):
    genes_to_pathway_mapping = defaultdict(set)

    with open(pathway_geneset_file, "rb") as f:
        pathway_geneset = pickle.load(f)

        ctr = 0
        for pathway, transcript_ids in pathway_geneset.items():
            for transcript_id in transcript_ids:
                msu_accessions = convert_transcript_to_msu(
                    transcript_id, transcript_to_msu_files
                )

                for msu_accession in msu_accessions:
                    genes_to_pathway_mapping[msu_accession].add(pathway)

            ctr += 1
            print(f"Processed {ctr} out of {len(pathway_geneset)} pathways")

    return genes_to_pathway_mapping


def export_mapping(mapping, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f"{output_dir}/genes_to_pathway.pickle", "wb") as handle:
        pickle.dump(mapping, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print(f"Generated {output_dir}/genes_to_pathway.pickle")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "pathway_geneset_file",
        help="pickled dictionary mapping pathways to the genes involved in the pathways",
    )
    parser.add_argument(
        "output_dir",
        help="output directory for the pickled dictionary mapping genes to their pathways",
    )
    parser.add_argument(
        "transcript_to_msu_files",
        help="pickled dictionaties mapping transcript IDs to MSU accessions",
        nargs="+",
    )

    args = parser.parse_args()

    export_mapping(
        map_genes_to_pathway(args.pathway_geneset_file, args.transcript_to_msu_files),
        args.output_dir,
    )
