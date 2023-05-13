library(GO.db)
library(optparse)

option_list <- list(
    make_option(c("-o", "--output_dir"),
        type = "character", default = NULL,
        help = "output directory for the text file mapping GO term IDs to their respective GO term names"
    )
)

opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser)

go_table <- as.data.frame(GOTERM)
goterms <- unique(go_table[, c(1, 3, 4)])

if (!dir.exists(opt$output_dir)) {
    dir.create(opt$output_dir)
}

write.table(goterms,
    sep = "\t", quote = FALSE,
    file = paste0(opt$output_dir, "/go-terms.tsv"), col.names = FALSE, row.names = FALSE
)

print(paste0("Generated ", opt$output_dir, "/go-terms.tsv"))
