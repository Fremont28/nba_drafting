library(survival)
library(survminer)
library(dplyr)
library(ggplot2)

nba_life=read.csv("metrics_fin.csv")
hist(nba_life$G) 
hist(nba_life$VORP)

#survival based on first three year VORP 
nba_life=nba_life %>% mutate(vorp_group=ifelse(VORP>0.291,"over","under"))
nba_life$vorp_group=factor(nba_life$vorp_group)

nba_life=nba_life %>% mutate(age_group=ifelse(Age>=24,"old","not_old"))
nba_life$age_group=factor(nba_life$age_group)

#fit the survival data using Kaplan-Meier method  
surv_object=Surv(time=nba_life$G)
surv_object 

fit1=survfit(surv_object~vorp_group,data=nba_life) #puff pastry???? 
summary(fit1)

ggsurvplot(fit1,data=nba_life,pval=TRUE)

#cox proportional hazard model 
fit_coxph=coxph(surv_object~vorp_group+age_group,data=nba_life)
ggforest(fit_coxph,data=nba_life)


#Players coached by the Spurs 
nba_life$early_sas1=ifelse(nba_life$early_sas>0,"yes","no")
table(nba_life$early_sas1) #58 players play at least one season over first three) con Popovich

#median games by group 
avg_games=ddply(nba_life,.(early_sas1), summarize, games=mean(G))
avg_games #241.62 avg games sas, 228.6 avg games non sas 
surv_object1=Surv(time=nba_life$G)
surv_object1

fit2=survfit(surv_object1~early_sas1,data=nba_life) #puff pastry???? 
summary(fit2)
ggsurvplot(fit2,data=nba_life,pval=TRUE)

#customize survival curves 
ggsurvplot(
  fit2, 
  data = nba_life, 
  size = 1,                 # change line size
  palette = 
    c("#E7B800", "#2E9FDF"),# custom color palettes
  conf.int = TRUE,          # Add confidence interval
  pval = TRUE,              # Add p-value
  risk.table = TRUE,        # Add risk table
  risk.table.col = "strata",# Risk table color by groups
  legend.labs = 
    c("Spurs", "Other Team"),    # Change legend labels
  risk.table.height = 0.25, # Useful to change when you have multiple groups
  ggtheme = theme_bw()      # Change ggplot2 theme
)

#plot 2
ggsurv <- ggsurvplot(
  fit2,                     # survfit object with calculated statistics.
  data = nba_life,             # data used to fit survival curves.
  risk.table = TRUE,       # show risk table.
  pval = TRUE,             # show p-value of log-rank test.
  conf.int = TRUE,         # show confidence intervals for 
  # point estimates of survival curves.
  palette = c("#E7B800", "#2E9FDF"),
  xlim = c(0,1300),         # present narrower X axis, but not affect
  # survival estimates.
  xlab = "Games",   # customize X axis label.
  break.time.by = 100,     # break X axis in time intervals by 500.
  ggtheme = theme_light(), # customize plot and risk table with a theme.
  risk.table.y.text.col = T,# colour risk table text annotations.
  risk.table.height = 0.25, # the height of the risk table
  risk.table.y.text = FALSE,# show bars instead of names in text annotations
  # in legend of risk table.
  ncensor.plot = TRUE,      # plot the number of censored subjects at time t
  ncensor.plot.height = 0.12,
  conf.int.style = "step",  # customize style of confidence intervals
  surv.median.line = "hv",  # add the median survival pointer.
  legend.labs = 
    c("Other Franchise", "Spurs")    # change legend labels.
)
ggsurv




#College Conference Viz (NBA VORP)
conf_vorp=read.csv("conf_pcts.csv") 
conf_vorp$Percent=round(conf_vorp$Percent,1)
conf_vorp=conf_vorp[!grepl("Pac-12", conf_vorp$Conference),]

x_labels <- c( "<0 \n VORP", "0-2 \n VORP", "2-4 \n VORP", "4+ \n VORP" )
label_names <- c( "A-10"="A-10", 
                  "ACC"="ACC", 
                  "Big 12"="Big 12", 
                  "Big East"="Big East", 
                  "Big Ten"="Big Ten", 
                  "Pac-10"="Pac-12",
                  "SEC"="SEC")

#2000-01 to 2018-19 
ggplot(conf_vorp, aes( x = VORP, y = Percent / 100, fill = VORP) ) +
  geom_bar( stat = "identity", width = 0.75, color = "#2b2b2b", size = 0.05 ) + 
  scale_y_continuous( labels = percent, limits = c( 0, 0.5 ) ) + 
  scale_x_discrete( expand = c( 0, 1 ), labels = x_labels ) + 
  scale_fill_manual( values = c( "#a6cdd9", "#d2e4ee", "#b7b079", "#efc750" ) ) +
  facet_wrap( ~ Conference, labeller = as_labeller(label_names) ) + 
  labs( x = NULL, y = NULL, title = "The SEC Produces Some Of The NBA's Best Talent" ) +
  theme( strip.text = element_text( size = 12, color = "white", hjust = 0.5 ),
         strip.background = element_rect( fill = "#858585", color = NA ),    
         panel.background = element_rect( fill = "#efefef", color = NA ),
         panel.grid.major.x = element_blank(),
         panel.grid.minor.x = element_blank(),
         panel.grid.minor.y = element_blank(),
         panel.grid.major.y = element_line( color = "#b2b2b2" ),
         panel.spacing.x = unit( 1, "cm" ),
         panel.spacing.y = unit( 0.5, "cm" ),
         legend.position = "none" ) +theme(plot.title = element_text(hjust = 0.5))


#********************************
#tale of two orginizations-----includes current players 
marfa=read.csv("pop_wines.csv")
sa_ny=subset(marfa,sas=="yes" | nyk=="yes",select=c("Player","G","sas"))
sa_ny$Team=ifelse(sa_ny$sas=="yes","SAS","NYK")

a=ggplot(sa_ny, aes(x = G))
a + geom_area(stat = "bin")

a + geom_area(aes(fill = Team), stat="bin",alpha=0.6) +#stat_bin(binwidth = 5)
  theme_classic()+scale_fill_manual(values=c("SAS"="black","NYK"="orange"))+
  ggtitle("Players That Are Drafted Or Signed By The Spurs Tend To Have Long Careers")+ylab("Count")+xlab("Games")+theme(plot.title = element_text(hjust = 0.5))


tm_gm=read.csv("tm_games.csv",sep=",")
merge_vorpy=merge(t1,tm_gm,by="Team")
cor.test(merge_vorpy$vorp_avg,merge_vorpy$Games) #0.153
merge_vorpy$subra=ifelse(merge_vorpy$Games>256.9,"Above Average","Below Average")


theme_set(theme_bw())
ggplot(merge_vorpy, aes(x=`Team`, y=Games, label=Games)) + 
  geom_point(stat='identity')  +
  scale_color_manual(name="Career Games", 
                     labels = c("Above Average", "Below Average"), 
                     values = c("above"="#00ba38", "below"="#f8766d")) + 
  geom_text(color="white", size=2) +
  labs(title="Teams that draft and sign players with longevity") +
  ylim(100, 340) +
  coord_flip()