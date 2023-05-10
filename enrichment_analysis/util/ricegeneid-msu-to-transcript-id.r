library(data.table)
library(riceidconverter)
library(optparse)

option_list <- list(
  make_option(c("-g", "--msu_genes"),
    type = "character", default = NULL,
    help = "text file containing the input genes (MSU ID)"
  ),
  make_option(c("-o", "--output_dir"),
    type = "character", default = NULL,
    help = "output directory for the text file containing the equivalent KEGG transcript IDs and the text file containing the genes without equivalent KEGG transcript IDs"
  )
)

opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser)

all_genes <- read.table(opt$msu_genes)
all_genes <- all_genes[[1]]

all_transcript <- c()
na_all_transcript <- c()

for (gene in all_genes) {
  transcript_id <- RiceIDConvert(gene, fromType = "MSU", toType = "TRANSCRIPTID")
  transcript_id_list <- c()
  transcript_id_list <- append(transcript_id_list, gene)

  for (id in transcript_id$TRANSCRIPTID) {
    if (is.na(id)) {
      print(gene)
      na_all_transcript <- append(na_all_transcript, gene)
    } else {
      transcript_id_list <- append(transcript_id_list, id)
    }
  }

  all_transcript <- append(all_transcript, list(transcript_id_list))
}

if (!dir.exists(opt$output_dir)) {
  dir.create(opt$output_dir)
}

lapply(na_all_transcript, write, paste0(opt$output_dir, "/all-na-transcript-id.txt"), append = TRUE, sep = "\n")
lapply(all_transcript, write, paste0(opt$output_dir, "/all-transcript-id.txt"), append = TRUE, sep = "\n")
