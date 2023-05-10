library(TPEA)
library(data.table)
library(ggplot2)
library(riceidconverter)
library(clusterProfiler)

DEGs<-sample(100:10000,10);
DEG<-as.matrix(DEGs);
number<-50;
scores<-AUEC(DEG);
FDR_method<-"fdr";
results<-TPEA(DEG,scores,number,FDR_method);

tpea_df <- as.data.frame(results)
write.table(tpea_df, "data/tpea_df.tsv", sep = "\t", row.names = FALSE, quote = FALSE)

# p1 <- dotplot(results,
#               showCategory = nrow(tpea_df),
#               title = "Top 10 most statistically significant enriched KEGG terms",
#               font.size = 10
# )
# 
# ggsave(p1,
#        filename = "data/kegg_dotplot.png",
#        height = 22, width = 22, units = "cm"
# )