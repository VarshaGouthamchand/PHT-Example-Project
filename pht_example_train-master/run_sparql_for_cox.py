import json
import pandas as pd
import requests
from io import StringIO
import re
import subprocess
import os

def run_sparql_for_cox (args):
    query = """
        PREFIX dbo: <http://um-cds/ontologies/databaseontology/>
        PREFIX roo: <http://www.cancerdata.org/roo/>
        PREFIX ncit: <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?Gender ?TumourLocation ?HPV ?Tstage ?Nstage ?Survival
        WHERE {
        OPTIONAL{
        ?tablerow roo:P100018 ?genderv.
        ?tablerow roo:P100029 ?neoplasm.
        ?neoplasm roo:P100202 ?tumourv.
        ?neoplasm roo:P100244 ?tstagev.
        ?neoplasm roo:P100242 ?nstagev.
        ?tablerow roo:P100022 ?hpvv.
        ?tablerow roo:P100254 ?survivalv.

        ?genderv dbo:has_cell ?gendercell.
        ?tumourv dbo:has_cell ?tumourcell.
        ?tstagev dbo:has_cell ?tcell.
        ?nstagev dbo:has_cell ?ncell.
        ?hpvv dbo:has_cell ?hpvcell.
        ?survivalv dbo:has_cell ?scell.

        ?gendercell a ?g.
        ?tumourcell a ?t.
        ?tcell a ?tS.
        ?ncell a ?n.
        ?hpvcell a ?h.
        ?scell a ?s.
            
        FILTER regex(str(?g), ("http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C16576|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C20197"))
        FILTER regex(str(?t), ("http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C12762|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C12246|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C12420|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C12423"))
        FILTER regex(str(?tS), ("http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48719|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48720|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48724|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48728|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48732"))
        FILTER regex(str(?n), ("http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48705|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48706|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48786|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48714"))
        FILTER regex(str(?h), ("http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C128839|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C131488"))
        FILTER regex(str(?s), ("http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C28554|http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C37987"))
            
        BIND(strafter(str(?g), "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#") AS ?Gender)
        BIND(strafter(str(?t), "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#") AS ?TumourLocation)
        BIND(strafter(str(?n), "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#") AS ?Nstage)
        BIND(strafter(str(?tS), "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#") AS ?Tstage)
        BIND(strafter(str(?h), "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#") AS ?HPV)
        BIND(strafter(str(?s), "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#") AS ?Survival)
    }
    }
    """
    codedict = {
        "C16576": "Female", "C20197": "Male", "C27966": "Stage I", "C28054": "Stage II",
        "C27970": "Stage III", "C27971": "Stage IV", "C12762": "Oropharynx", "C12420": "Larynx",
        "C12246": "Hypopharynx", "C12423": "Nasopharynx", "C48719": "T0", "C48720": "T1", "C48724": "T2",
        "C48728": "T3", "C48732": "T4", "C48705": "N0", "C48706": "N1", "C48786": "N2", "C48714": "N3",
        "C48699": "M0", "C48700": "M1", "C28554": "Dead", "C37987": "Alive", "C128839": "HPV Positive",
        "C131488": "HPV Negative", "C94626": "ChemoRadiotherapy", "C15313": "Radiotherapy"
    }

    endpoint = "http://"+args+":7200/repositories/" + userRepo
    annotationResponse = requests.post(endpoint,data="query=" + query,
                                       headers={
                                           "Content-Type": "application/x-www-form-urlencoded",
                                           # "Accept": "application/json"
                                       })
    output = annotationResponse.text
    #return output 
    hnscc = pd.read_csv(StringIO(output))
    for col in hnscc.columns:
        hnscc[col] = hnscc[col].map(codedict).fillna(hnscc[col])
    return hnscc
