import csv
from SPARQLWrapper import SPARQLWrapper, JSON
import ssl
import urllib
import re
import random

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
PREFIX dbo: <http://dbpedia.org/ontology/>

SELECT DISTINCT ?x ?y
WHERE {
  ?x owl:disjointWith ?y .
  FILTER(
    STRSTARTS(STR(?x), STR(dbo:)) 
  )
} LIMIT 27
""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

class_list = []

for result in results["results"]["bindings"]:

    class1 = result["x"]["value"]
    class2 = result["y"]["value"]

    clean_class1= clean_element(urllib.parse.unquote(result["x"]["value"]).split("/")[-1]) # removes the URI from predicate
    clean_class2= clean_element(urllib.parse.unquote(result["y"]["value"]).split("/")[-1]) # removes the URI from predicate

    if ":" in clean_class2:
        clean_class2 = urllib.parse.unquote(clean_class2).split(":")[-1]

    class_list.append([class1, class2, clean_class1, clean_class2])

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
statements = []

for result in results["results"]["bindings"]:
    clean_class = urllib.parse.unquote(result["class"]["value"]).split("/")[-1] #removes the URI from Class
    clean_class_list.append(clean_class)

def create_statements(answer, label, counter, max_statements):

    statements = [] 
    statements_count = 0
    query_count = 0

    for class_uri in class_list:

        if statements_count >= max_statements:  # break the loop if the maximum number of statements is reached
            break

        query_class = class_uri[1]

        sparql.setQuery(f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX dbo: <http://dbpedia.org/ontology/>

        SELECT DISTINCT ?x
        WHERE {{
            ?x a <{query_class}>.
        }}
        LIMIT 5
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
            # remove the underscores and parentheses
            cleaned_y = class_uri[3]
            cleaned_z = class_uri[2]

            # condition for true statements
            if label == 'True':

                if cleaned_z[0].lower() in ['a', 'e', 'i', 'o', 'u'] and cleaned_y in ['a', 'e', 'i', 'o', 'u']:
                    triple_1 = f"{cleaned_x} is an {cleaned_y}."
                    triple_2 = f"{cleaned_y} is disjoint with {cleaned_z}."
                    inferred_triple = f"{cleaned_x} is not an {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_x} not an {cleaned_z}?"
                elif cleaned_z[0].lower() in ['a', 'e', 'i', 'o', 'u'] :
                    triple_1 = f"{cleaned_x} is a {cleaned_y}."
                    triple_2 = f"{cleaned_y} is disjoint with {cleaned_z}."
                    inferred_triple = f"{cleaned_x} is not an {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_x} not an {cleaned_z}?"
                elif cleaned_y[0].lower() in ['a', 'e', 'i', 'o', 'u'] :
                    triple_1 = f"{cleaned_x} is an {cleaned_y}."
                    triple_2 = f"{cleaned_y} is disjoint with {cleaned_z}."
                    inferred_triple = f"{cleaned_x} is not a {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_x} not a {cleaned_z}?"
                else:
                    triple_1 = f"{cleaned_x} is a {cleaned_y}."
                    triple_2 = f"{cleaned_y} is disjoint with {cleaned_z}."
                    inferred_triple = f"{cleaned_x} is not a {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_x} not a {cleaned_z}?"
            
                statement_true = [counter, triple_1, triple_2, question, answer, inferred_triple, label] 
                statements.append(statement_true)

                counter += 1            
                statements_count += 1

        # condition for false statements
            elif label == 'False':

                other_classes = [] # list of classes for incorrect triples
                for class_clean in clean_class_list:
                    # the class cannot be the same as the other classes
                    if class_clean != cleaned_z and class_clean != cleaned_y:
                            other_classes.append(class_clean)

                random_class = random.choice(other_classes)

                if cleaned_z[0].lower() in ['a', 'e', 'i', 'o', 'u'] and cleaned_y[0].lower() in ['a', 'e', 'i', 'o', 'u']:
                    triple_1 = f"{cleaned_x} is an {cleaned_y}."
                    triple_2 = f"{cleaned_y} is disjoint with {random_class}."
                    inferred_triple = f"{cleaned_x} could be an {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_x} not an {cleaned_z}?"
                elif cleaned_z[0].lower() in ['a', 'e', 'i', 'o', 'u'] :
                    triple_1 = f"{cleaned_x} is a {cleaned_y}."
                    triple_2 = f"{cleaned_y} is disjoint with {random_class}."
                    inferred_triple = f"{cleaned_x} could be an {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_x} not an {cleaned_z}?"
                elif cleaned_y[0].lower() in ['a', 'e', 'i', 'o', 'u'] :
                    triple_1 = f"{cleaned_x} is an {cleaned_y}."
                    triple_2 = f"{cleaned_y} is disjoint with {random_class}."
                    inferred_triple = f"{cleaned_x} could be a {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_x} not a {cleaned_z}?"
                else:
                    triple_1 = f"{cleaned_x} is a {cleaned_y}."
                    triple_2 = f"{cleaned_y} is disjoint with {random_class}."
                    inferred_triple = f"{cleaned_x} could be a {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_x} not a {cleaned_z}?"
            
                statement= [counter, triple_1, triple_2, question, answer, inferred_triple, label] 
                statements.append(statement)

                counter += 1
                statements_count += 1
            
    return statements, counter

# create the true and false statements
true_statements, counter= create_statements('Yes', 'True', 1, 1000)
false_statements, _= create_statements('No','False', counter, 1000)

file_path = '/Users/kaho2/Desktop/Thesis/Datasets/OWL/Rule5/rule5_OWL.csv'

with open(file_path, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["ID", "triple1", "triple2", "question", "answer", "inferred triple", "label"])

    # put the statements in the csv file
    for element in true_statements:
        writer.writerow(element)
    for element in false_statements:  
        writer.writerow(element)  