library(GO.db)

go_table <- as.data.frame(GOTERM)
godb <- unique(go_table[,c(1,3,4)])

write.table(goterms, sep="\t", quote=FALSE, file="data/go/go_terms.txt")