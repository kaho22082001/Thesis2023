import csv
from SPARQLWrapper import SPARQLWrapper, JSON
import ssl
import urllib
import re
import random
import json

def clean_element(text):
    text = text.replace('_', ' ') # remove underscores
    text = re.sub(r'\(.*?\)', '', text) # remove everything between parentheses
    return text.strip() # return the triple

# to bypass the SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

# sparql endpoint
sparql = SPARQLWrapper("http://dbpedia.org/sparql")

# gather all subjects and objects
sparql.setQuery("""
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX dbo: <http://dbpedia.org/ontology/>

SELECT DISTINCT ?x ?y
WHERE {
  ?x owl:differentFrom ?y .
  FILTER(
    STRSTARTS(STR(?x), STR(dbr:)) &&
    STRSTARTS(STR(?y), STR(dbr:))
  )
} LIMIT 3
""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results["results"]["bindings"]:

    subject1 = result["x"]["value"]
    subject2 = result["y"]["value"]

    clean_subject1 = clean_element(urllib.parse.unquote(result["x"]["value"]).split("/")[-1]) # removes the URI from predicate
    clean_subject2 = clean_element(urllib.parse.unquote(result["y"]["value"]).split("/")[-1]) # removes the URI from predicate

    triple_1 = f"{clean_subject1} is different from {clean_subject2}."
    inferred_triple = f"{clean_subject2} is different from {clean_subject1}."
    question = f"Given the previous statement, is {clean_subject2} an {clean_subject1}?"

def create_statements(answer, label, counter):

    statements = []

    sparql.setQuery("""
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX dbr: <http://dbpedia.org/resource/>
    PREFIX dbo: <http://dbpedia.org/ontology/>

    SELECT DISTINCT ?x ?y
    WHERE {
    ?x owl:differentFrom ?y .
    FILTER(
        STRSTARTS(STR(?x), STR(dbr:)) &&
        STRSTARTS(STR(?y), STR(dbr:))
    )
    } LIMIT 1000
    """)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    for result in results["results"]["bindings"]:

        subject1 = result["x"]["value"]
        subject2 = result["y"]["value"]

        clean_subject1 = clean_element(urllib.parse.unquote(subject1).split("/")[-1]) # removes the URI from predicate
        clean_subject2 = clean_element(urllib.parse.unquote(subject2).split("/")[-1]) # removes the URI from predicate


            # condition for true statements
        if label == 'True':

            triple_1 = f"{clean_subject1} is different from {clean_subject2}."
            inferred_triple = f"{clean_subject2} is different from {clean_subject1}."
            question = f"Given the previous statement, is {clean_subject2} an {clean_subject1}?"
            
            statement_true = [counter, triple_1, question, answer, inferred_triple, label] 
            statements.append(statement_true)

            counter += 1            

        # condition for false statements
        elif label == 'False':

            triple_1 = f"{clean_subject1} is different from {clean_subject1}."
            inferred_triple = f"{clean_subject2} is not different from {clean_subject1}."
            question = f"Given the previous statement, is {clean_subject2} an {clean_subject1}?"

            statement= [counter, triple_1, question, answer, inferred_triple, label] 
            statements.append(statement)

            counter += 1

            
    return statements, counter

# create the true and false statements
true_statements, counter= create_statements('Yes', 'True', 1)
false_statements, _= create_statements('No','False', counter)

file_path = '/Users/kaho2/Desktop/Thesis/Datasets/OWL/Rule4/rule4_OWL.csv'

with open(file_path, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["ID", "triple1", "question", "answer", "inferred triple", "label"])

    # put the statements in the csv file
    for element in true_statements:
        writer.writerow(element)
    for element in false_statements:  
        writer.writerow(element)  