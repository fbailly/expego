donnees = read.csv2('results.csv',sep=",",dec=".")
summary(donnees)
boxplot(donnees[["Resultat"]]~donnees[["Condition"]])
mod.rm<-aov(Resultat ~ Condition + Error(Sujets/Condition), data=donnees)
summary(mod.rm)
donnees$Condition <- with(donnees, reorder(Condition, Resultat, mean))
boxplot(donnees$Resultat~donnees$Condition)

pairwise.t.test(donnees$Resultat,donnees$Condition,p.adj = "bonferroni",pool.sd = FALSE, paired=TRUE)