import json
import pandas as pd
import requests
from io import StringIO
import re
import subprocess
import os

mydict = {}
# read database uri
database_uri = os.getenv('DATABASE_URI','no_database_uri')
args = open(database_uri).read().strip()
print(args)

queryPatient = """
    PREFIX roo: <http://www.cancerdata.org/roo/>
    SELECT (COUNT(*) AS ?count)
    WHERE {
        ?tablerow roo:P100061 ?patient.
    }
"""
queryT = """
    PREFIX dbo: <http://um-cds/ontologies/databaseontology/>
    PREFIX roo: <http://www.cancerdata.org/roo/>
    PREFIX ncit: <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
	SELECT ?Tstage
    WHERE {
    OPTIONAL
    {
        ?tablerow roo:P100008 ?neoplasm.
        ?neoplasm roo:100243 ?7th_TNM.
        ?7th_TNM a ?tnm.
        ?tnm owl:equivalentClass ncit:C88937.
        ?7th_TNM roo:P100244 ?tstagev.
        ?tstagev dbo:has_cell ?cell.
        ?cell a ?t.
        FILTER regex(str(?t), ("http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48737|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48719|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48720|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48724|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48728|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48732|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48733|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C132010|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C10000"))
        BIND(strafter(str(?t), "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#") AS ?Tstage)
    }
    }
            """

queryG = """
    PREFIX dbo: <http://um-cds/ontologies/databaseontology/>
    PREFIX roo: <http://www.cancerdata.org/roo/>
    PREFIX ncit: <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?Gender
    WHERE {
    OPTIONAL
    {
        ?tablerow roo:P100018 ?genderv.
        ?genderv dbo:has_cell ?cell.
        ?cell a ?g.
        FILTER regex(str(?g), ("http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C16576|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C20197|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C10000"))
        BIND(strafter(str(?g), "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#") AS ?Gender)
    }
}
"""
queryN = """
    PREFIX dbo: <http://um-cds/ontologies/databaseontology/>
    PREFIX roo: <http://www.cancerdata.org/roo/>
    PREFIX ncit: <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?Nstage
    WHERE {
    OPTIONAL
    {
        ?tablerow roo:P100008 ?neoplasm.
        ?neoplasm roo:100243 ?7th_TNM.
        ?7th_TNM a ?tnm.
        ?tnm owl:equivalentClass ncit:C88937.
        ?7th_TNM roo:P100242 ?nstagev.
        ?nstagev dbo:has_cell ?cell.
        ?cell a ?n.
        FILTER regex(str(?n), ("http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48705|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48706|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48711|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48713|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48715|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48716|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48786|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48712|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48714|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C96026|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C10000"))
        BIND(strafter(str(?n), "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#") AS ?Nstage)
    }
    }
"""
queryM = """
    PREFIX dbo: <http://um-cds/ontologies/databaseontology/>
    PREFIX roo: <http://www.cancerdata.org/roo/>
    PREFIX ncit: <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?Mstage
    WHERE {
    OPTIONAL
    {
        ?tablerow roo:P100008 ?neoplasm.
        ?neoplasm roo:100243 ?7th_TNM.
        ?7th_TNM a ?tnm.
        ?tnm owl:equivalentClass ncit:C88937.
        ?7th_TNM roo:P100241 ?mstagev.
        ?mstagev dbo:has_cell ?cell.
        ?cell a ?m.
        FILTER regex(str(?m), ("http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48699|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48700|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48704|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C10000"))
        BIND(strafter(str(?m), "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#") AS ?Mstage)
    }
    }
"""
queryS = """
    PREFIX dbo: <http://um-cds/ontologies/databaseontology/>
    PREFIX roo: <http://www.cancerdata.org/roo/>
    PREFIX ncit: <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?Survival
    WHERE {
    OPTIONAL
    {
        ?tablerow roo:P100028 ?survivalv.
        ?survivalv dbo:has_cell ?cell.
        ?cell a ?s.
        FILTER regex(str(?s), ("http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C28554|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C37987|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C10000"))
        BIND(strafter(str(?s), "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#") AS ?Survival)
    }
    }
"""
queryAge = """
	PREFIX dbo: <http://um-cds/ontologies/databaseontology/>
    PREFIX roo: <http://www.cancerdata.org/roo/>
    PREFIX ncit: <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?agevalue   
    WHERE 
        {
        ?tablerow roo:P100000 ?age.
        ?age dbo:has_cell ?cell.
        ?cell roo:P100042 ?agevalue.  
	}
"""
queryTumour = """
    PREFIX dbo: <http://um-cds/ontologies/databaseontology/>
    PREFIX roo: <http://www.cancerdata.org/roo/>
    PREFIX ncit: <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?TumourLocation
    WHERE {
    OPTIONAL {
    ?tablerow roo:P100008 ?neoplasm.
    ?neoplasm roo:P100202 ?tumour. 
    ?tumour dbo:has_cell ?tumourcell. 
    ?tumourcell a ?t.
    FILTER regex(str(?t), ("http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C10000|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C4044|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C150211|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C12762|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C12246|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C12420|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C12421|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C12423"))
    BIND(strafter(str(?t), "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#") AS ?TumourLocation)
    }
}
"""
queryHpv = """
    PREFIX dbo: <http://um-cds/ontologies/databaseontology/>
    PREFIX roo: <http://www.cancerdata.org/roo/>
    PREFIX ncit: <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?HPV
    WHERE {
    OPTIONAL {
    ?tablerow roo:P100022 ?hpvv.
    ?hpvv dbo:has_cell ?hpvcell.
    ?hpvcell a ?h.
    FILTER regex(str(?h), ("http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C128839|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C131488|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C10000"))
    BIND(strafter(str(?h), "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#") AS ?HPV)
   }
}
"""
queryChemo = """
    PREFIX dbo: <http://um-cds/ontologies/databaseontology/>
    PREFIX roo: <http://www.cancerdata.org/roo/>
    PREFIX ncit: <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?Therapy
    WHERE {
    OPTIONAL {
    ?tablerow roo:P100231 ?chemov.
    ?chemov dbo:has_cell ?chemocell.
    ?chemocell a ?c.
    FILTER regex(str(?c), ("http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C160337|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C141342|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C158876|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C94626|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C10000|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C15313"))
    BIND(strafter(str(?c), "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#") AS ?Therapy)
   }
}
"""
queryAgeSurv = """
	PREFIX dbo: <http://um-cds/ontologies/databaseontology/>
	PREFIX roo: <http://www.cancerdata.org/roo/>
	SELECT ?agevalue ?survivaldays
	WHERE 
	{  
	OPTIONAL {
	   ?tablerow roo:P100000 ?age.
	   ?age dbo:has_cell ?agecell.
	   ?agecell roo:P100042 ?agevalue.
	   ?tablerow roo:P100311 ?survivalv.
	   ?survivalv dbo:has_cell ?cell.
	   ?cell roo:P100042 ?survivaldays.
	} 
	}
"""

def queryresult(repo, query):
    #endpoint = "http://172.17.0.1:7200/repositories/" + repo
    endpoint1 = "http://gateway.docker.internal:7200/repositories/" + repo
    try:
        endpoint = "http://"+args+":7200/repositories/" + repo
        annotationResponse = requests.post(endpoint,	
                                           data="query=" + query,
                                           headers={
                                               "Content-Type": "application/x-www-form-urlencoded",
                                               # "Accept": "application/json"
                                           })
        output = annotationResponse.text
        return output 
    except:
        annotationResponse = requests.post(endpoint1, data="query=" + query,
                                       headers={
                                           "Content-Type": "application/x-www-form-urlencoded",
                                           # "Accept": "application/json"
                                       })
        output = annotationResponse.text
        return output

result_hn = pd.DataFrame()

codedict = {
        "C16576": "Female", "C20197": "Male", "C12421": "Oral Cavity", "C12762": "Oropharynx", "C4044": "Larynx", "C150211": "Larynx advanced",
        "C12246": "Hypopharynx", "C12423": "Nasopharynx", "C00000": "Unknown", "C48737": "Tx", "C48719": "T0", "C48720": "T1", "C48724": "T2",
        "C48728": "T3", "C48732": "T4", "C48733": "T4A", "C132010": "T5", "C48705": "N0", "C48706": "N1", "C48786": "N2", "C48711": "N2A",
        "C48712": "N2B", "C48713": "N2C", "C48714": "N3", "C48715": "N3A", "C48716": "N3B", "C96026": "N4",
        "C48704": "Mx", "C48699": "M0", "C48700": "M1", "C28554": "Dead", "C37987": "Alive", "C128839": "HPV Positive",
        "C131488": "HPV Negative", "C10000": "Unknown", "C94626": "ChemoRadiotherapy", "C15313": "Radiotherapy",
        "C160337": "Chemo Not received", "C141342": "Concurrent ChemoRadiotherapy", "C158876": "Induction ChemoRadiotherapy"
    }

#url = "http://172.17.0.1:7200/rest/repositories"
url1 = "http://gateway.docker.internal:7200/rest/repositories"
try:
    url = "http://"+args+":7200/rest/repositories"
    node = requests.get(url, headers={"Accept": "application/json"})
    nodes = list(node.json())
except:
    node = requests.get(url1, headers={"Accept": "application/json"})
    nodes = list(node.json())
for i in nodes:
    txt = i['id']
    x = re.search("userRepo", txt)
    if x:
        repo = txt

result_data = queryresult(repo, queryPatient)
patientCount = pd.read_csv(StringIO(result_data))
x = patientCount['count'][0]
mydict['NumberOfPatients'] = str(x)

querylists = [queryT, queryG, queryN, queryM, queryS, queryTumour, queryHpv, queryChemo]
for lists in querylists:
    result_data_hn = queryresult(repo, lists)
    data_hn = pd.read_csv(StringIO(result_data_hn))
    result_hn = pd.concat([result_hn, data_hn], axis=1)
    for col in result_hn.columns:
    	result_hn[col] = result_hn[col].map(codedict).fillna(result_hn[col])
    	x = result_hn.value_counts(result_hn[col])
    	y = x.to_dict()
    	mydict[col] = y

result_data = queryresult(repo, queryAge)
agerangeData = pd.read_csv(StringIO(result_data))
maxAge = agerangeData['agevalue'].max()
minAge = agerangeData['agevalue'].min()
meanAge = agerangeData['agevalue'].mean()
agerangeData['Age_Range'] = pd.cut(agerangeData['agevalue'], [0, 40, 50, 60, 70, 80, 90],
                             labels=['0-40', '40-50', '50-60', '60-70', '70-80', '80-90'])
ageData = agerangeData.groupby(['Age_Range']).count()
y = ageData.to_dict()
mydict['AgeRange'] = y['agevalue']
mydict['minAge'] = str(minAge)
mydict['maxAge'] = str(maxAge)
mydict['meanAge'] = str(meanAge)

result_data = queryresult(repo, queryAgeSurv)
ageSurvdata = pd.read_csv(StringIO(result_data))
ageSurvdata['Age_Range'] = pd.cut(ageSurvdata['agevalue'], [0, 40, 50, 60, 70, 80, 90],
                             labels=['0-40', '40-50', '50-60', '60-70', '70-80', '80-90'])
ageSurvdata = ageSurvdata.sort_values("Age_Range").reset_index(drop=True)
ageSurvdata = ageSurvdata.drop(['agevalue'], axis=1)
ageSurvdict = ageSurvdata.groupby(['Age_Range']).mean()
y = ageSurvdict.to_dict()
x = {}
mydict['AverageSurvivalbyAge'] = y['survivaldays']

jsonObj = json.dumps(mydict)
#print(jsonObj)

with open('output.txt', 'w') as f:
	f.write(jsonObj)

	