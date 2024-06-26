import gffutils
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord


def main(
    genome, gff_db, upstream_win_len, downstream_win_len, out_fasta, promoter_gene_map_f
):
    records = SeqIO.to_dict(SeqIO.parse(genome, "fasta"))
    db = gffutils.FeatureDB(gff_db, keep_order=True)
    genes = list(db.features_of_type("gene"))
    promoters = []
    promoter_gene_map = open(args.promoter_gene_map, "a")
    for gene in genes:
        if gene.strand == "+":
            promoter_seq_up = str(
                records[gene.seqid].seq[
                    gene.start - 1 - upstream_win_len : gene.start - 1
                ]
            )
            promoter_seq_dn = str(
                records[gene.seqid].seq[
                    gene.start - 1 : gene.start - 1 + downstream_win_len
                ]
            )
            promoter_seq = promoter_seq_up + promoter_seq_dn
            promoter_seq_id = (
                gene.seqid
                + ":"
                + str(gene.start - 1 - upstream_win_len)
                + "-"
                + str(gene.start - 1 + downstream_win_len)
            )
            promoter_seq_rec = SeqRecord(
                Seq(promoter_seq), id=promoter_seq_id, description=""
            )

        elif gene.strand == "-":
            promoter_seq_up = str(
                records[gene.seqid].seq[gene.end : gene.end + upstream_win_len]
            )
            promoter_seq_dn = str(
                records[gene.seqid].seq[gene.end - 1 - downstream_win_len : gene.end]
            )
            promoter_seq = promoter_seq_dn + promoter_seq_up
            promoter_seq_id = (
                gene.seqid
                + ":"
                + str(gene.start - 1 - upstream_win_len)
                + "-"
                + str(gene.start - 1 + downstream_win_len)
            )
            promoter_seq_rec = SeqRecord(
                Seq(promoter_seq), id=promoter_seq_id, description=""
            )
            promoters.append(promoter_seq_rec)

        promoters.append(promoter_seq_rec)
        promoter_gene_map.write(
            promoter_seq_id + "\t" + gene.attributes["ID"][0] + "\n"
        )

        #    promoter_seq = str(records[gene.seqid].seq[gene.start - upstream_win_len:gene.start - 1])

    SeqIO.write(promoters, out_fasta, "fasta")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("genome", help="genome sequence")
    parser.add_argument("gff_db", help="path to gff db")
    parser.add_argument(
        "upstream_win_len",
        type=int,
        help="how many bps upstream of TSS do we search for motifs",
    )
    parser.add_argument(
        "downstream_win_len",
        type=int,
        help="how many bps downstream of TSS do we search for motifs",
    )
    parser.add_argument("out_fasta", help="path to output fasta file")
    parser.add_argument(
        "promoter_gene_map", help="path to file containing promoter-to-gene map"
    )

    args = parser.parse_args()
    main(
        args.genome,
        args.gff_db,
        args.upstream_win_len,
        args.downstream_win_len,
        args.out_fasta,
        args.promoter_gene_map,
    )
