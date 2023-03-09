import os
import pandas as pd
import json

# read database uri
database_uri = os.getenv('DATABASE_URI','no_database_uri')

# read/query data from database_uri
data = pd.read_csv(database_uri)
#data = pd.read_csv("C:\\Users\\P70070487\\Documents\\Maastro\\Triplifier_Project\\DataSets\\Houston.csv")
mydict = {}
#mydict['Summary'] = {}
## paste your algorithm here . Example to calculate sum of age from the data
count1 = len(data)
mean1 = data['Age at Diag'].mean()
minimum1 = data['Age at Diag'].min()
maximum1 = data['Age at Diag'].max()

mydict['Number of Records'] = int(count1)
mydict['Average age'] = int(mean1)
mydict['Minimum Age'] = int(minimum1)
mydict['Maximum Age'] = int(maximum1)

survdata = data.groupby(['Gender'])['Overall survival_duration'].mean()
sdata = survdata.to_dict()
sdata = {k : int(v) for k,v in sdata.items()}
mydict['Genderwise mean Survival days'] = sdata

#Count of Gender
gender = data['Gender'].value_counts()
g = gender.to_dict()
mydict['Gender'] = g

#Count of T-category
tvalue = data['T-category'].value_counts()
t = tvalue.to_dict()
mydict['T-stage'] = t

#Count of N-category
nvalue = data['N-category'].value_counts()
n = nvalue.to_dict()
mydict['N-stage'] = n

#Count of HPV
hpv = data['HPV Status'].value_counts()
h = hpv.to_dict()
mydict['HPV Status'] = h

#Count of AJCC
ajcc = data['AJCC Stage (7th edition)'].value_counts()
aj = ajcc.to_dict()
mydict['AJCC'] = aj

#Count of Vital status
vital = data['Vital status'].value_counts()
v = vital.to_dict()	
mydict['Vital status'] = v

#Count of Cancer subsite
subsite = data['Cancer subsite of origin'].value_counts()
sub = subsite.to_dict()	
mydict['Cancer subsite'] = sub

#Count of Therapy
therapy = data['Therapeutic Combination'].value_counts()
ther = therapy.to_dict()	
mydict['Therapy'] = ther

#Age range count
df = pd.DataFrame(columns=['Age_Range', 'count'])
data['Age_Range'] = pd.cut(data['Age at Diag'], [0, 40, 50, 60, 70, 80, 90],
                             labels=['0-40', '40-50', '50-60', '60-70', '70-80', '80-90'])
df = data.groupby(['Age_Range']).count()
df = df.filter(['Age_Range', 'Age at Diag'])
y = df.to_dict()
mydict['AgeRange'] = y['Age at Diag']

newdata = data.dropna(subset=["Overall survival_duration"], inplace=True)  # drops NaN
newdata = data.sort_values("Age_Range").reset_index(drop=True)
newdata = newdata.filter(['Age_Range', 'Overall survival_duration', 'Vital status'])
newdata = newdata.groupby(['Age_Range', 'Vital status'])['Overall survival_duration'].mean()
agedata = newdata.dropna().to_dict()
agedata = {k : int(v) for k,v in agedata.items()}
agedata = dict((', '.join(k), v) for k,v in agedata.items())
#agedata = {k: v for a, v in agedata.items() for k in a}
mydict['Agewise Mean-Survival'] = agedata

#AJCC & Tumour Location
ajccData = data.groupby(["Gender", "AJCC Stage (7th edition)", "HPV Status"]).size()
a = ajccData.dropna().to_dict()
a = dict((', '.join(k), v) for k,v in a.items())
mydict['Gender-AJCC-wise-HPV'] = a

jsonObj = json.dumps(mydict)
#print(jsonObj)

with open('output.txt', 'w') as f:
	f.write(jsonObj)
	