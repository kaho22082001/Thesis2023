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
PREFIX dbr: <http://dbpedia.org/resource/>

SELECT DISTINCT ?x ?y
WHERE {
  ?x owl:sameAs ?y .
  FILTER(
    STRSTARTS(STR(?x), STR(dbr:)) 
  )
} LIMIT 1000
""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()
# json_result = json.dumps(results)
# print(json_result)

sbj_obj_list = []
clean_sbj_obj_list =[]

for result in results["results"]["bindings"]:

    subject = result["x"]["value"]
    object = result["y"]["value"]

    clean_subject= clean_element(urllib.parse.unquote(result["x"]["value"]).split("/")[-1]) # removes the URI from predicate
    clean_object= clean_element(urllib.parse.unquote(result["y"]["value"]).split("/")[-1]) # removes the URI from predicate

    if subject != "http://dbpedia.org/resource/Giovanni_\"Ernesto\"_Ceirano":
        sbj_obj_list.append([subject, object, clean_subject, clean_object])
        clean_sbj_obj_list.append([clean_subject, clean_object])

# print(sbj_obj_list)

sparql.setQuery("""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT DISTINCT ?class 
WHERE {
  ?class a owl:Class .
  FILTER(
    STRSTARTS(STR(?class), STR(dbo:))
  )
} 
LIMIT 780
""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

clean_class_list = [] #list of classes without URI

for result in results["results"]["bindings"]:
    clean_class = urllib.parse.unquote(result["class"]["value"]).split("/")[-1] #removes the URI from Class
    clean_class_list.append(clean_class)

def create_statements(answer, label, counter, max_statements):

    statements = [] 
    statements_count = 0
    query_count = 0

    for sbj_obj in sbj_obj_list:

        if statements_count >= max_statements:  # break the loop if the maximum number of statements is reached
            break

        query_subject = sbj_obj[0]

        sparql.setQuery(f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>

        SELECT DISTINCT ?z
        WHERE {{
            <{query_subject}> a ?z .
            FILTER(
                STRSTARTS(STR(?z), STR(dbo:)) 
            )
        }}
        LIMIT 3
        """)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        # json_results = json.dumps(results)
        # print(json_results)

        query_count += 1

        print(f'Queries performed so far: {query_count}')

        for result in results["results"]["bindings"]:

            if statements_count >= max_statements:  # break the loop if the maximum number of statements is reached
                break

            z_uri = result['z']['value']
            z_local = urllib.parse.unquote(z_uri).split("/")[-1]
            cleaned_z = clean_element(z_local)
            # remove the underscores and parentheses
            cleaned_x = sbj_obj[2]
            cleaned_y = sbj_obj[3]

            # condition for true statements
            if label == 'True' and cleaned_x != cleaned_y:

                if cleaned_z[0].lower() in ['a', 'e', 'i', 'o', 'u']:
                    triple_1 = f"{cleaned_x} is an {cleaned_z}."
                    triple_2 = f"{cleaned_x} is the same as {cleaned_y}."
                    inferred_triple = f"{cleaned_y} is a {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_y} an {cleaned_z}?"
                else:
                    triple_1 = f"{cleaned_x} is a {cleaned_z}."
                    triple_2 = f"{cleaned_x} is the same as {cleaned_y}."
                    inferred_triple = f"{cleaned_y} is a {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_y} a {cleaned_z}?"
            
                statement_true = [counter, triple_1, triple_2, question, answer, inferred_triple, label] 
                statements.append(statement_true)

                counter += 1            
                statements_count += 1

        # condition for false statements
            elif label == 'False' and cleaned_x != cleaned_y:

                other_classes = [] # list of classes for incorrect triples
                for class_clean in clean_class_list:
                    # the class cannot be the same as the other classes
                    if class_clean != cleaned_z:
                            other_classes.append(class_clean)

                random_class = random.choice(other_classes)

                if cleaned_z[0].lower() in ['a', 'e', 'i', 'o', 'u'] and random_class[0].lower() in ['a', 'e', 'i', 'o', 'u']:
                    triple_1 = f"{cleaned_x} is an {random_class}."
                    triple_2 = f"{cleaned_x} is the same as {cleaned_y}."
                    inferred_triple = f"{cleaned_y} is not an {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_y} an {cleaned_z}?"
                elif random_class[0].lower() in ['a', 'e', 'i', 'o', 'u']: 
                    triple_1 = f"{cleaned_x} is an {random_class}."
                    triple_2 = f"{cleaned_x} is the same as {cleaned_y}."
                    inferred_triple = f"{cleaned_y} is not a {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_y} a {cleaned_z}?"
                elif cleaned_z[0].lower() in ['a', 'e', 'i', 'o', 'u']: 
                    triple_1 = f"{cleaned_x} is a {random_class}."
                    triple_2 = f"{cleaned_x} is the same as {cleaned_y}."
                    inferred_triple = f"{cleaned_y} is not an {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_y} an {cleaned_z}?"
                else:
                    triple_1 = f"{cleaned_x} is a {random_class}."
                    triple_2 = f"{cleaned_x} is the same as {cleaned_y}."
                    inferred_triple = f"{cleaned_y} is not a {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_y} a {cleaned_z}?"
            
                statement= [counter, triple_1, triple_2, question, answer, inferred_triple, label] 
                statements.append(statement)

                counter += 1
                statements_count += 1
            
    return statements, counter

# create the true and false statements
true_statements, counter= create_statements('Yes', 'True', 1, 1000)
false_statements, _= create_statements('No','False', counter, 1000)

file_path = '/Users/kaho2/Desktop/Thesis/Datasets/Simple Datasets/OWL/Rule3/rule3_OWL.csv'

with open(file_path, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["ID", "triple1", "triple2", "question", "answer", "inferred triple", "label"])

    # put the statements in the csv file
    for element in true_statements:
        writer.writerow(element)
    for element in false_statements:  
        writer.writerow(element)  