import random
import numpy as np
import pandas as pd

df = pd.read_excel('Programs.xlsx')


def describe():
    print("The total number of positions is " + str(int(df.Positions.sum()))+".")
    print("The number of possible combinations of regions and specilties is " + str(int(df.describe().Positions.loc["count"]))+".")
    print()
    print("There are "+str(len(df.Region.value_counts()))+" different regions.")
    print("The number of specilties for each region:")
    print(df.Region.value_counts())
    print("The number of positions for each region:")
    print(df.groupby("Region").sum())
    print()
    print("There are "+str(len(df.Specialty.value_counts()))+" different specialties.")
    print("The number of regions for each specialty:")
    print(df.Specialty.value_counts())
    print("The number of positions for each specialty:")
    print(df.groupby("Specialty").sum())

    print()
    print("The averge number of positions per specialty per regions is " + str(float(df.describe().Positions.loc["mean"]))+".")
    print("The standard deviation is " + str(float(df.describe().Positions.loc["std"]))+".")
    print("The min number of positions per specialty per regions is " + str(int(df.describe().Positions.loc["min"]))+".")
    print("The max number of positions per specialty per regions is " + str(int(df.describe().Positions.loc["max"]))+" ("
          +str(df[df.Positions==170].Specialty.iloc[0])+", "+str(df[df.Positions==170].Region.iloc[0])+").")

## describe()


## This is to shape the datafarme to be more usefull
df['Choice']=(df.Specialty + "; " +df.Region)
df=df.drop(columns=["Specialty","Region"])
df['Variable']="Positions"
df=df.rename(columns = {'Positions':'Value'})
df=df[["Choice","Variable","Value"]]

## Here, we are creating a second dataframe for imaginary candidates and their marks and choices for specializwation.
def cList(): 
    List = []
    for candidate in range(5000):
        List.append([candidate,"Mark",random.randint(50,90)])
        List.append([candidate,"Best Choice",1])
        List.append([candidate,"Accepted Choice","Not Accepted"])
        choices=[]
        for x in range(10):
            choices.append(df.Choice.loc[random.randint(0,len(df)-1)])
        choices.append('No available positions')
        List.append([candidate,"Wishes",choices])
    return List        
cdf = pd.DataFrame(cList())
cdf.columns = ['Candidate', 'Variable', 'Value']

# More reshaping of the first dataframe
choicesList= df.Choice
for x in df.Choice:
    df=df.append({'Choice':x, 'Variable':"Lowest Mark","Value":100}, ignore_index=True)
    df=df.append({'Choice':x, 'Variable':"Accepted Candidates","Value":0}, ignore_index=True)
df=df.sort_values(by=["Choice"]).reset_index(drop=True)
df=df.set_index(["Choice","Variable"])
cdf=cdf.set_index(["Candidate","Variable"])

candidates=cdf.loc[pd.IndexSlice[:,["Mark"]],:].reset_index().drop(columns="Variable")
bestMark=max(candidates.Value)
bestCandidates=candidates[candidates.Value==bestMark].drop(columns="Value").reset_index(drop=True)
full=[]
def operation():
    global bestCandidates
    global candidates
    global bestMark
    global cdf
    global df
    global full
    for bestCandidate in range(len(bestCandidates)):
        firstChoice=cdf.loc[(bestCandidates.Candidate[bestCandidate],"Wishes"),"Value"][cdf.loc[(bestCandidates.Candidate[bestCandidate],"Best Choice"),"Value"]-1]    
        available = True
        if firstChoice in full:
            available = False
        while available == False:
            cdf.loc[(bestCandidates.Candidate[bestCandidate],"Best Choice"),"Value"]+=1
            firstChoice=cdf.loc[(bestCandidates.Candidate[bestCandidate],"Wishes"),"Value"][cdf.loc[(bestCandidates.Candidate[bestCandidate],"Best Choice"),"Value"]-1]
            if firstChoice in full:
                available = False
            else:
                available = True
                print (bestCandidates.Candidate[bestCandidate],cdf.loc[(bestCandidates.Candidate[bestCandidate],"Best Choice"),"Value"])
        if firstChoice != "No available positions":
            cdf.loc[(bestCandidates.Candidate[bestCandidate],"Accepted Choice"),"Value"]=firstChoice
            df.loc[(firstChoice,"Accepted Candidates"),"Value"]+=1
           # The next line should be corrected later
            bestMark = cdf.loc[(bestCandidates.Candidate[bestCandidate],"Mark"),"Value"]
            df.loc[(firstChoice,"Lowest Mark"),"Value"]=bestMark

    full=[] 
    for singleChoice in range(len(choicesList)):
        if df.loc[(choicesList[singleChoice],"Accepted Candidates"),"Value"] >= df.loc[(choicesList[singleChoice],"Positions"),"Value"]:
            print(choicesList[singleChoice])
            print(df.loc[(choicesList[singleChoice],"Accepted Candidates"),"Value"],df.loc[(choicesList[singleChoice],"Positions"),"Value"])
            full.append(choicesList[singleChoice])
##    candidates= candidates[candidates.Value < bestMark]
##    bestCandidates=candidates[candidates.Value == max(candidates.Value)].drop(columns="Value").reset_index(drop=True)

operation()
continueOperation = True
while continueOperation== True:
    if len(full) < len(choicesList):
        if min(candidates.Value) < bestMark: 
            candidates= candidates[candidates.Value < bestMark]
            bestCandidates=candidates[candidates.Value == max(candidates.Value)].drop(columns="Value").reset_index(drop=True)
            operation()
        else:
            print("No more candidates")
            continueOperation= False
    else:
        print("Positions are full.")
        continueOperation= False
fdf = []
for x in choicesList:
    fdf.append([x,df.loc[x,"Positions"].Value,df.loc[x,"Accepted Candidates"].Value, df.loc[x,"Lowest Mark"].Value])
xfdf = pd.DataFrame(fdf,columns=['Program', 'Positions', 'Accepted Candidiates', 'Lowest Mark'])

candidates=cdf.loc[pd.IndexSlice[:,["Mark"]],:].reset_index().drop(columns="Variable")
fcdf = []
for x in candidates.Candidate:
    fcdf.append([x,cdf.loc[x,"Mark"].Value,cdf.loc[x,"Accepted Choice"].Value, cdf.loc[x,"Best Choice"].Value,cdf.loc[x,"Wishes"].Value])
xfcdf = pd.DataFrame(fcdf,columns=['Candidate', 'Mark','Program', 'Choice Number','List of Choices'])

writer = pd.ExcelWriter('Matching.xlsx')
xfdf.to_excel(writer,'Sheet1')
xfcdf.to_excel(writer,'Sheet2')
writer.save()
