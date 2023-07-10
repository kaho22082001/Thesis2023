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

# gather all predicates
sparql.setQuery("""
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX dbo: <http://dbpedia.org/ontology/>

SELECT DISTINCT ?p
WHERE {
  ?p a owl:FunctionalProperty .
  ?p rdfs:label ?label .
  FILTER(LANG(?label) = "en")
} 
""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

predicate_list = [] #list for the predicates

for result in results["results"]["bindings"]:
    predicate = result["p"]["value"]
    predicate_list.append(predicate)

statements_temp = []
value_list = []

for predicate in predicate_list:

    #gather the subjects and data 
    sparql.setQuery(f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX dbr: <http://dbpedia.org/resource/>
    PREFIX dbo: <http://dbpedia.org/ontology/>

    SELECT DISTINCT ?x ?y
    WHERE {{
        ?x <{predicate}> ?y.
    }}
    LIMIT 5
    """)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    for result in results["results"]["bindings"]:
        current_subject = result["x"]["value"]
        predicate = predicate
        value = result["y"]["value"]
        if "datatype" in result["y"]:
            value_type = result["y"]["datatype"]
            new_value_statement = '"' + str(value) + '"^^' + "<" + value_type + ">"

            statements_temp.append([current_subject, predicate, value, new_value_statement])
            value_list.append(value)

def create_statements(answer, label, counter, max_statements):

    statements = [] 
    statements_count = 0
    query_count = 0
    

    for statement in statements_temp:

        if statements_count >= max_statements:  # break the loop if the maximum number of statements is reached
            break

        cleaned_sbj = clean_element(urllib.parse.unquote(statement[0]).split("/")[-1])
        cleaned_predicate = urllib.parse.unquote(statement[1]).split("/")[-1]

        new_predicate = statement[1]
        data = statement[2]
        new_statement = statement[3]
        
        sparql.setQuery(f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX dbo: <http://dbpedia.org/ontology/>

        SELECT DISTINCT ?x
        WHERE {{
            ?x <{new_predicate}> {new_statement}.
        }}
        LIMIT 22
        """)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        query_count += 1

        print(f'Queries performed so far: {query_count}')

        for result in results["results"]["bindings"]:

            if statements_count >= max_statements:  # break the loop if the maximum number of statements is reached
                break

            x_uri = result['x']['value']
            x_local = urllib.parse.unquote(x_uri).split("/")[-1]
            cleaned_x = clean_element(x_local)

            # condition for true statements
            if label == 'True' and cleaned_x != cleaned_sbj:

                triple_1 = f"{cleaned_x} {cleaned_predicate} {data}."
                triple_2 = f"{cleaned_sbj} {cleaned_predicate} {data}."
                triple_3 = f"{cleaned_predicate} is a functional property."
                inferred_triple = f"{cleaned_x} is the same as {cleaned_sbj}."
                question = f"Given the previous statements, is {cleaned_x} the same as {cleaned_sbj}?"
            
                statement_true = [counter, triple_1, triple_2, triple_3, question, answer, inferred_triple, label] 
                statements.append(statement_true)
                counter += 1            
                statements_count += 1

            # condition for false statements
            elif label == 'False' and cleaned_x != cleaned_sbj:

                other_classes = [] # list of classes for incorrect triples
                for potential_values in value_list:
                    # the class cannot be the same as the other classes
                    if potential_values != data:
                            other_classes.append(potential_values)

                random_value = random.choice(other_classes)

                triple_1 = f"{cleaned_x} {cleaned_predicate} {data}."
                triple_2 = f"{cleaned_sbj} {cleaned_predicate} {random_value}."
                triple_3 = f"{cleaned_predicate} is a functional property."
                inferred_triple = f"{cleaned_x} is not the same as {cleaned_sbj}."
                question = f"Given the previous statements, is {cleaned_x} the same as {cleaned_sbj}?"
            
                statement= [counter, triple_1, triple_2, triple_3, question, answer, inferred_triple, label] 
                statements.append(statement)
                counter += 1
                statements_count += 1
            
    return statements, counter

# create the true and false statements
true_statements, counter= create_statements('Yes', 'True', 1, 1000)
false_statements, _= create_statements('No','False', counter, 1000)

file_path = '/Users/kaho2/Desktop/Thesis/Datasets/OWL/Rule6/rule6_OWL.csv'

with open(file_path, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["ID", "triple1", "triple2", "triple3", "question", "answer", "inferred triple", "label"])

    # put the statements in the csv file
    for element in true_statements:
        writer.writerow(element)
    for element in false_statements:  
        writer.writerow(element)  


