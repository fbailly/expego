donnees1 = read.csv2('stats_birapp1.csv',sep=";",dec=".")
summary(donnees1)
donnees1$Sujet<-as.factor(donnees1$Sujet)
summary(donnees1)

mod.rm<-aov(Resultat ~ Condition + Error(Sujet/Condition), data=donnees1)
summary(mod.rm)

boxplot(donnees1$Resultat~donnees1$Condition)


library(ez)

aov.rm <- ezANOVA(donnees1,
dv = Resultat,
wid= Sujets,
between =,
within= Condition,
type = 3,
return_aov=TRUE)

aov.rm

aov.fig <- ezPlot(donnees1,
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
boxplot(donnees1$Resultat~donnees1$Condition,las=2,outline=TRUE)
mtext("Score moyen", side = 2, line = 15, outer = FALSE, cex = 2.5)
mtext("Partie du corps", side = 1, line = 13, outer = FALSE, cex = 2.5)
dev.off()
