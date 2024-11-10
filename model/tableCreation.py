import pandas as pd
import random

df = pd.read_csv("model\ptsd_survey.csv")

bin = [0,29,44,59,120]
labels = [0,1,2,3]
df['Age'] = pd.cut(df['Age'], bins=bin, labels=labels, right=True)
print(df.head())


def random_age_by_category(row):
    category = row["Age"]
    if category == 0:
        return random.randint(18,29)
    if category == 1:
        return random.randint(30,44)
    if category == 2:
        return random.randint(45,59)
    if category == 3:
        return random.randint(60,90)


def random_score_by_category(row):
    category = row["PCL-Score"]
    if category == "None/Resilience":
        return random.randint(0,31)
    if category == "Mild":
        return random.randint(32,47)
    if category == "Moderate":
        return random.randint(48,63)
    if category == "Serious":
        return random.randint(64,80)


def random_perc_by_category(row):
    category = row["PCL-Score"]
    if category == "None/Resilience":
        return random.uniform(0.001, 0.4999)  
    elif category == "Mild":
        return random.uniform(0.5, 0.666)  
    elif category == "Moderate":
        return random.uniform(0.6777, 0.8333)  
    elif category == "Serious":
        return random.uniform(0.8444, 1) 
    else:
        return random.uniform(0, 1)  

    

df['Age'] = df.apply(random_age_by_category, axis=1)
df['PTSD'] = df.apply(random_perc_by_category, axis=1)
df['PCL-Score'] = df.apply(random_score_by_category, axis=1)


df.to_csv('model\ptsd_survey3.csv', index=False)

print(df.head())
