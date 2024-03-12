import csv
import os
import pickle

GREEK_LETTERS = {
    "alpha": ("α", "Α"),
    "beta": ("β", "Β"),
    "gamma": ("γ", "Γ"),
    "delta": ("δ", "Δ"),
    "epsilon": ("ε", "Ε"),
    "zeta": ("ζ", "Ζ"),
    "eta": ("η", "Η"),
    "theta": ("θ", "Θ"),
    "iota": ("ι", "Ι"),
    "kappa": ("κ", "Κ"),
    "lambda": ("λ", "Λ"),
    "mu": ("μ", "Μ"),
    "nu": ("ν", "Ν"),
    "xi": ("ξ", "Ξ"),
    "omicron": ("ο", "Ο"),
    "pi": ("π", "Π"),
    "rho": ("ρ", "Ρ"),
    "sigma": ("σ", "Σ"),
    "tau": ("τ", "Τ"),
    "upsilon": ("υ", "Υ"),
    "phi": ("φ", "Φ"),
    "chi": ("χ", "Χ"),
    "psi": ("ψ", "Ψ"),
    "omega": ("ω", "Ω"),
}


def map_symbol_to_msu(gene_index_file):
    mapping = {}
    with open(gene_index_file, encoding="utf8") as f:
        csv_reader = csv.reader(f, delimiter=",")
        next(csv_reader)

        for line in csv_reader:
            # Some entries in the accession column consist of multiple accessions
            accessions = line[2].split(",")
            # Remove the opening and closing brackets
            gene_symbols = line[-1][1:-1].split(",")
            gene_symbols = [
                gene_symbol.replace('"', "").replace("'", "").replace("\\", "").strip()
                for gene_symbol in gene_symbols
            ]

            for idx, gene_symbol in enumerate(gene_symbols):
                if gene_symbol.isdigit():
                    # Handle cases like \\OsAMT1,2\\
                    gene_symbols[idx - 1] = gene_symbols[idx - 1] + "," + gene_symbol
                    gene_symbols[idx] = ""

                if len(gene_symbol) == 1:
                    gene_symbols[idx] = ""

            gene_symbols = [
                symbol.lower() for symbol in list(filter(None, gene_symbols))
            ]

            for gene_symbol in gene_symbols:
                for letter, greek_symbol in GREEK_LETTERS.items():
                    if letter in gene_symbol:
                        gene_symbols.append(
                            gene_symbol.replace(letter, greek_symbol[0])
                        )
                        gene_symbols.append(
                            gene_symbol.replace(letter, greek_symbol[1])
                        )

            for gene_symbol in gene_symbols:
                mapping[gene_symbol] = accessions

    return mapping


def export_mapping_dict(mapping_dict, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f"{output_dir}/genesymbol_to_msu.pickle", "wb") as f:
        pickle.dump(mapping_dict, f, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"Generated {output_dir}/genesymbol_to_msu.pickle")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "gene_index_file", help="file containing gene accessions and their common names"
    )
    parser.add_argument(
        "output_dir",
        help="output directory for the pickled dictionary mapping gene symbols (names) to their MSU IDs",
    )

    args = parser.parse_args()

    mapping = map_symbol_to_msu(args.gene_index_file)
    export_mapping_dict(mapping, args.output_dir)
