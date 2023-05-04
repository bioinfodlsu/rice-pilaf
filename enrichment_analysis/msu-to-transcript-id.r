library(data.table)
library(riceidconverter)

all_genes <- read.table("data/all_genes.txt")
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

lapply(na_all_transcript, write, "data/temp/all-na-transcript-id.txt", append = TRUE, sep = "\n")
lapply(all_transcript, write, "data/temp/all-transcript-id.txt", append = TRUE, sep = "\n")
