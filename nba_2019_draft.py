import numpy as np 
import pandas as pd 
import re 

#import datasets 
nba_yr=pd.read_csv("nba_todos.csv")
college=pd.read_csv("college_todos.csv")
draft_ages=pd.read_csv("draft_ages.csv")
draft_com=pd.read_csv("nba_draft_combine_all_years.csv")

#combine data
comb1=pd.merge(nba_yr,college,on="Player") 
comb1=pd.merge(comb1,draft_ages,on="Player") #age and position 
comb1.to_csv("comb1.csv")

comb2=pd.merge(comb1,draft_com,on="Player") #1309 (physical metrics data for building the model)
comb2=comb2.sort_values(by="Season")

#first three seasons in the NBA 
nba_now1=comb2.sort_values(by=['Player','Season'], ascending=[False,False]).groupby('Player').tail(3)
nba_vorp=nba_now1.groupby('Player')['VORP'].sum()
nba_vorp=pd.DataFrame(nba_vorp)
nba_vorp.reset_index(level=0,inplace=True)
nba_now1=pd.merge(nba_now1,nba_vorp,on="Player")
nba_now1=nba_now1.drop_duplicates(subset=['Player']) 
nba_now1.to_csv("jelly2.csv") #jelly1.csv (primero season), jelly2.csv (third season)

comb3=comb2.sort_values(by=['Player','Season'], ascending=[False,False]).groupby('Player').tail(7)
comb3=comb3.sort_values(by="Season",ascending=False) #for second season and beyond 
comb3=comb3.drop_duplicates(subset=['Player'])

#year X vorp (one year ahead of other metrics)
yX_vorp=comb2.sort_values(by=['Player','Season'], ascending=[False,False]).groupby('Player').tail(8)
yX_vorp=yX_vorp.sort_values(by="Season",ascending=False) 
yX_vorp=yX_vorp.drop_duplicates(subset=['Player'])
yX_vorp=yX_vorp[["Player","VORP"]]
yX_vorp.columns=['Player','VORP_real']
comb4=pd.merge(comb3,yX_vorp,on="Player") #854,102

#unique players only 
comb4=comb4.drop_duplicates('Player') #273 players 

#select columns to subset x=nba, y=college
sub1=comb4.iloc[:,2:36] 
sub2=comb4.iloc[:,36:102]
sub2=sub2.drop("College_x",1)   
sub2=sub2.drop("Year_x",1)
sub2=sub2.drop("Lg",1)   
sub2=sub2.drop("Rd",1)
sub2=sub2.drop("Pk",1)
sub2=sub2.drop("Tm",1)
sub3=pd.concat([sub1,sub2],axis=1)
sub3.to_csv("nba_past1.csv") 


#combine csv files 
#YEAR 1 
yr1=pd.read_csv("year8_0.5.csv")
yr1x=pd.read_csv("year8_0.9.csv")
yr1xx=pd.read_csv("year8_0.1.csv")

yr1_players=comb2.sort_values(by=['Player','Season'], ascending=[False,False]).groupby('Player').tail(8)
yr1_players=yr1_players[["Player","Season"]]

#merge y1_0.5
y1m=pd.merge(yr1,yr1_players,on="Player")
y1m=y1m[y1m.predict1 !=0]
y1m.columns=['x','xx','predict_yr1_0.5','Player','vorp_yr1','Season']

#merge y1_0.9
y1h=pd.merge(yr1x,yr1_players,on="Player")
y1h=y1h[y1h.predict1 !=0]
y1h.columns=['x','xx','predict_yr1_0.9','Player','vorp_yr1','Season']

#merge y1_0.1
y1l=pd.merge(yr1xx,yr1_players,on="Player")
y1l=y1l[y1l.predict1 !=0]
y1l.columns=['x','xx','predict_yr1_0.1','Player','vorp_yr1','Season']

#average by season 
y1_total=pd.merge(y1m,y1h,on="Player")
y1_total=pd.merge(y1_total,y1l,on="Player")
y1_total.to_csv("y8_total.csv") 

#averages by season 
y1_avgM=y1_total.groupby('Season')['predict_yr1_0.5'].mean()
y1_avgH=y1_total.groupby('Season')['predict_yr1_0.9'].mean()
y1_avgL=y1_total.groupby('Season')['predict_yr1_0.1'].mean()
y1_actual=y1_total.groupby('Season')['vorp_yr1'].mean() 

y1_finals=pd.concat([y1_avgM,y1_avgH,y1_avgL,y1_actual],axis=1)
y1_finals.to_csv("y8_finals.csv") 

#all years players 
yr1_tot=pd.read_csv("y1_total.csv")
yr1_tot=yr1_tot.drop_duplicates('Player')
yr2_tot=pd.read_csv("y2_total.csv")
yr2_tot=yr2_tot.drop_duplicates('Player')
yr3_tot=pd.read_csv("y3_total.csv")
yr3_tot=yr3_tot.drop_duplicates('Player')
yr4_tot=pd.read_csv("y4_total.csv")
yr4_tot=yr4_tot.drop_duplicates('Player')
yr5_tot=pd.read_csv("y5_total.csv")
yr5_tot=yr5_tot.drop_duplicates('Player')
yr6_tot=pd.read_csv("y6_total.csv")
yr6_tot=yr6_tot.drop_duplicates('Player')
yr7_tot=pd.read_csv("y7_total.csv")
yr7_tot=yr7_tot.drop_duplicates('Player')

todos_players=pd.concat([yr1_tot,yr2_tot,yr3_tot,yr4_tot,yr5_tot,yr6_tot,yr7_tot],axis=0)
todos_players=todos_players[["Player","Season","predict_yr1_0.5","predict_yr1_0.9","predict_yr1_0.1","vorp_yr1"]]
todos_players.columns=['Player','Season','pred_0.5','pred_0.9','pred_0.1','vorp']
todos_players=todos_players.drop_duplicates()
yr1_tot=yr1_tot.drop_duplicates(['Player','Season'])
todos_players.to_csv("todos_players.csv")


#*************************************************************************
##for otro analysis merge age, pos with original dataframe 
ana=comb1.sort_values(by=['Player','Season'], ascending=[False,False]).groupby('Player').tail(1) #591 players
ana=ana.iloc[:,0:63]
ana.to_csv("ana.csv")

#Q1. average age of draft picks by season?
avg=ana.groupby(['Season'])[['Age_x','VORP']].mean() 
avg.sort_values(by='VORP')

#Q2. age at nba debut? (age bins)
dor=comb1.sort_values(by=['Player','Season'], ascending=[False,False]).groupby('Player').tail(3)
bins=[18,21,24,27,30]
dor['binned_age']=pd.cut(dor['Age_y'],bins)
bin_age=dor.groupby('binned_age').count()['Player'] #18-21 226, 21-24 354, 11 24-27, 0 above?? 

#Q3. vorp first three seasons based on age bin?
age_vorp=dor.groupby('binned_age')['VORP'].mean()

#Q4. vorp total for players start career at 18-21 vs. 22 above?
cin=comb1.sort_values(by=['Player','Season'], ascending=[False,False]).groupby('Player').tail(1)
under_22=cin[cin.Age_y<22]["Player"] #358 unique players 
under_22=pd.DataFrame(under_22)
under_22_merge=pd.merge(under_22,comb1,on="Player")
under_22_merge['VORP'].mean() #0.767 VORP

#average season (x) vs. average vorp (y) 
avg1=above_22_merge.groupby('Season')['VORP'].mean()
avg1=pd.DataFrame(avg1)
avg1.reset_index(level=0,inplace=True)
avg1.to_csv("avg2.csv")

#above 22 
above_22=cin[cin.Age_y>=22]["Player"] 
above_22=pd.DataFrame(above_22) #233 unique? 
above_22_merge=pd.merge(above_22,comb1,on="Player")
above_22_merge['VORP'].mean() #0.341 VORP

#Q5. percent of games started players under 26? 
per_26=comb1[comb1.Age_x>=26] #25.43 mean games started <26, >=26 29.51 GS since 2000-01 
per_26x=per_26.groupby('Season')['GS'].mean()
per_26x=pd.DataFrame(per_26x)
per_26x.to_csv("26_over.csv") 

#Q6. are centers playing less by season? 
centers=comb1[comb1.Pos=="C"]
centers_mp=centers.groupby('Season')['MP_x'].mean() #20.2 min 18-19 (17.02 to 20.23 13-14 to 18-19)

#Q7. turnaround players? negative vorp first 3 seasons and +3 VORP over first six years? 
neg=comb1.sort_values(by=['Player','Season'], ascending=[False,False]).groupby('Player').tail(3)
avg_3v=neg.groupby('Player')['VORP'].sum()
avg_3v=pd.DataFrame(avg_3v) #1-3
avg_3v.reset_index(level=0,inplace=True)
avg_3v=avg_3v[avg_3v.VORP<=0]

pos=comb1.sort_values(by=['Player','Season'], ascending=[False,False]).groupby('Player').tail(6)
avg_3v1=neg.groupby('Player')['VORP'].sum()
avg_3v1=pd.DataFrame(avg_3v1) #4-6 
avg_3v1.reset_index(level=0,inplace=True)
avg_3v1=avg_3v1[avg_3v1.VORP>=0.5]

merge_v=pd.merge(avg_3v,avg_3v1,on="Player")
merge_v  

#last x seasons
combXX=comb2.sort_values(by=['Player','Season'], ascending=[False,False]).groupby('Player').tail(3)
college=pd.read_csv("college_todos.csv")

#how to find hidden talent? 
sz=college[college['Player'].str.contains('DeAndre Hunter')]
list_playas=['Zion Williamson','Coby White']
college[college['Player'].str.contains('Zion Williamson| Cody White | DeAndre Hunter')] 

antes=comb2 
draft_com.columns
antes['Pos'].unique()

avg_anthro=antes.groupby('Pos')[['Height (With Shoes)','Height (No Shoes)',
'Wingspan','Standing reach','Vertical (Max)','Vertical (Max Reach)',
'Vertical (No Step)','Vertical (No Step Reach)','Weight','Body Fat',
'Hand (Length)','Hand (Width)','Bench','Agility','Sprint']].mean()

avg_anthro=pd.DataFrame(avg_anthro)
avg_anthro.reset_index(level=0,inplace=True)
avg_anthro.to_csv("avg_ant.csv")


###4/19/19--- search jugadores 
new=pd.read_csv("college_todos_2019.csv")

list_playas=['Zion Williamson','Coby White','DeAndre Hunter','Keldon Johnson','Nassir Little',
'Cameron Reddish','Bruno Fernando','Jarrett Culver','Nickeil Alexander-Walker',
'Jaxson Hayes','KZ Okpala','Darius Garland','Romeo Langford',
'Bol Bol','Mfiondu Kabengele','Daniel Gafford','Naz Reid','Kris Wilkes',
'Chuma Okeke','Jordan Nwora','Ty Jerome','Ashton Hagans','Moses Brown',
'Kevin Porter','PJ Washington','Nicolas Claxton','Jalen Smith',
'Ochai Agbaji','Ayo Dosunmu','Jaylen Nowell','Tre Jones',
'Tyler Bey','Tyler Cook','Cameron Johnson','Admiral Schofield',
'Devon Dotson','Louis King','Carsen Edwards','Ignas Brazdeikis',
'Eric Paschall','Jontay Porter','Matisse Thybulle','Sagaba Konate',
'Ky Bowman','Markus Howard','Robert Franks','Jalen Lecque',
'Isaiah Roby','Luguentz Dort','James Palmer','Grant Williams',
'Dedric Lawson','Tyler Herro','Kyle Guy','Talen Horton-Tucker',
'Jaylen Hoard','Quentin Grimes','Makai Mason','Aric Holman',
'Udoka Azubuike','Caleb Martin','Steve Enoch','Shamorie Ponds','Jaylen Hands',
'R.J. Barrett']

np=new[new['Player'].str.contains('|'.join(list_playas))]
college19=pd.read_csv("college_2019.csv")

#merge dataframe on player 
np1=pd.merge(np,college19,on="Player")
np1.to_csv("np1.csv")
fin=pd.read_csv("np1.csv") #with physical features 


#4/20/19 add nba players from past 
past_nba=comb1 
past_nba1=past_nba 
past_vorp=past_nba1.groupby('Player')['VORP'].sum() # black grass !Lucha Contra De La Injustica? 
past_vorp=pd.DataFrame(past_vorp)
past_vorp.reset_index(level=0,inplace=True)
past_nba2=pd.merge(past_nba,past_vorp,on="Player")
past_nba2.to_csv("jelly4.csv") #jelly3.csv (first five seasons), jelly4.csv (everything)

tm='TOR'
first_tresX['phi']=np.where(first_tresX['Team'].str.contains(tm),'yes','no')

sub_pop=first_tresX[["Player","sas","dal","bos","mia","atl","lal","mil",
"ind","brk","orl","det","cha","mia","wsh","chi","nyk","gsw",
"den","por","uta","hou","okc","lac","sac","min","mem","nop",
"dal","phx","ind","tor","phi"]]
sub_pop=sub_pop.drop_duplicates('Player') #drop duplicate players??? 
pop=pd.merge(sub_pop,games,on="Player")
pop.to_csv("pop_wines.csv")


#select players that didn't play este temprano 
select_total=nba_yr['Player']
select_total=pd.DataFrame(select_total)
select_total=select_total.drop_duplicates()
select_now=nba_yr[nba_yr['Season']=='2018-19']['Player']
select_now=pd.DataFrame(select_now)
select_now=select_now['Player'].tolist() 

past_playa=select_total[~select_total.Player.isin(select_now)]
past_playa=past_playa[~past_playa.Player.str.contains("Russell Westbrook")]
past_playa=past_playa[~past_playa.Player.str.contains("Stephen Curry")]
past_playa=past_playa[~past_playa.Player.str.contains("LeBron James")]

list_past_players=past_playa['Player'].tolist() 
for_games=nba_yr[nba_yr.Player.isin(list_past_players)]
games=for_games.groupby('Player')['G'].sum() 
games=pd.DataFrame(games)
games.reset_index(level=0,inplace=True)

#survival times based on two groups? 
first_tres=nba_yr.sort_values(by=['Player','Season'], ascending=[False,False]).groupby('Player').tail(3)

#early Spurs (1-3 years)
def early_spurs(x):
    if x=="no":
        return 0
    else:
        return 1 

first_tres['early_sas']=first_tres['sas'].apply(early_spurs)
tm="POR"
first_tres['por']=np.where(first_tresX['Team'].str.contains(tm),1,0)

metrics=first_tres.groupby('Player')[["GS","VORP","eFG%","TRB","Age","FTA","early_sas"]].mean()
metrics=pd.DataFrame(metrics)
metrics.reset_index(level=0,inplace=True)

metrics_fin=pd.merge(games,metrics,on="Player")
metrics_fin.to_csv("metrics_fin.csv")


###some college VORP/Season metrics 
bins=[-2,0,2,4,14]
coll_stats=comb1[["Conf","VORP"]] #3436 player seasons from major conference 
coll_stats['binned_vorp']=pd.cut(coll_stats['VORP'],bins)
conf_met=coll_stats.groupby(['Conf','binned_vorp'])['binned_vorp'].count()
conf_met=pd.DataFrame(conf_met)
#percent within conference 
conf_pcts = conf_met.groupby(level=0).apply(lambda x:
                                                 100 * x / float(x.sum()))

conf_pcts.reset_index(level=0,inplace=True)
conf_pcts.to_csv("conf_pcts.csv")

