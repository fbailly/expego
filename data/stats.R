donnees = read.csv2('results.csv',sep=",",dec=".")
summary(donnees)
donnees$Condition <- with(donnees, reorder(Condition, Resultat, mean))
mod.rm<-aov(Resultat ~ Condition + Error(Sujets/Condition), data=donnees)
summary(mod.rm)

boxplot(donnees$Resultat~donnees$Condition)


library(ez)

aov.rm <- ezANOVA(donnees,
dv = Resultat,
wid= Sujets,
between =,
within= Condition,
type = 3,
return_aov=TRUE)

aov.rm

aov.fig <- ezPlot(donnees,
dv = .(Resultat),
wid= .(Sujets),
between= ,
within = .(Condition),
x = .(Condition),
x_lab = 'Partie du corp',
y_lab = 'Score total'
)

aov.fig

pdf("stats.pdf",width=30,height=17)
par(mar=c(20,20,4,4))
par(pin=c(20,10))
par(mgp=c(10,1,.5))
par(cex.axis=2)
boxplot(donnees$Resultat~donnees$Condition,las=2,outline=TRUE)
mtext("Score moyen", side = 2, line = 15, outer = FALSE, cex = 2.5)
mtext("Partie du corps", side = 1, line = 13, outer = FALSE, cex = 2.5)
dev.off()
