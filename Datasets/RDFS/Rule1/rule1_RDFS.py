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

# gather all classes
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

classes = [] #list of classes with URI
clean_class_list = [] #list of classes without URI

for result in results["results"]["bindings"]:
    clean_class = urllib.parse.unquote(result["class"]["value"]).split("/")[-1] #removes the URI from Class
    classes.append(result["class"]["value"])
    clean_class_list.append(clean_class)

def create_statements(answer, label, counter, max_statements):

    statements = [] 
    statements_count = 0
    query_count = 0

    for class_uri in classes:

        if statements_count >= max_statements:  # break the loop if the maximum number of statements is reached
            break

        sparql.setQuery(f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX dbp: <http://dbpedia.org/resource/>

            SELECT DISTINCT ?x ?y ?z
            WHERE {{
                ?x rdf:type <{class_uri}> .
                <{class_uri}> rdfs:subClassOf ?z .
                FILTER(
                (STRSTARTS(STR(?z), STR(dbo:)) || STRSTARTS(STR(?z), STR(dbp:)))
                )
            }}
            LIMIT 3
        """)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        query_count += 1

        print(f'Queries performed so far: {query_count}')

        for result in results["results"]["bindings"]:

            if statements_count >= max_statements:  # break the loop if the maximum number of statements is reached
                break

            x_uri = result['x']['value']
            y_uri = class_uri 
            z_uri = result['z']['value'] 

            x_local = urllib.parse.unquote(x_uri).split("/")[-1]
            y_local = urllib.parse.unquote(y_uri).split("/")[-1]
            z_local = urllib.parse.unquote(z_uri).split("/")[-1]

            # remove the underscores and parentheses
            cleaned_x = clean_element(x_local)
            cleaned_y = clean_element(y_local)
            cleaned_z = clean_element(z_local)

            # condition for true statements
            if label == 'True':
                # conditions for checking when to use "an" or "a"
                if cleaned_y[0].lower() in ['a', 'e', 'i', 'o', 'u'] and cleaned_z[0].lower() in ['a', 'e', 'i', 'o', 'u']:
                    triple_1 = f"{cleaned_x} is an {cleaned_y}."
                    triple_2 = f"{cleaned_y} is a subclass of {cleaned_z}."
                    inferred_triple = f"{cleaned_x} is an {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_x} an {cleaned_z}?"
                elif cleaned_y[0].lower() in ['a', 'e', 'i', 'o', 'u']:
                    triple_1 = f"{cleaned_x} is an {cleaned_y}."
                    triple_2 = f"{cleaned_y} is a subclass of {cleaned_z}."
                    inferred_triple = f"{cleaned_x} is a {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_x} a {cleaned_z}?"
                elif cleaned_z[0].lower() in ['a', 'e', 'i', 'o', 'u']:
                    triple_1 = f"{cleaned_x} is a {cleaned_y}."
                    triple_2 = f"{cleaned_y} is a subclass of {cleaned_z}."
                    inferred_triple = f"{cleaned_x} is an {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_x} an {cleaned_z}?"
                else:
                    triple_1 = f"{cleaned_x} is a {cleaned_y}."
                    triple_2 = f"{cleaned_y} is a subclass of {cleaned_z}."
                    inferred_triple = f"{cleaned_x} is a {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_x} a {cleaned_z}?"
                
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

                # Conditions for checking when to use "an" or "a"
                if cleaned_y[0].lower() in ['a', 'e', 'i', 'o', 'u'] and cleaned_z[0].lower() in ['a', 'e', 'i', 'o', 'u']:
                    triple_1 = f"{cleaned_x} is an {cleaned_y}."
                    triple_2 = f"{cleaned_y} is a subclass of {random_class}."
                    inferred_triple = f"{cleaned_x} is not an {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_x} an {cleaned_z}?"
                elif cleaned_y[0].lower() in ['a', 'e', 'i', 'o', 'u']:
                    triple_1 = f"{cleaned_x} is an {cleaned_y}."
                    triple_2 = f"{cleaned_y} is a subclass of {random_class}."
                    inferred_triple = f"{cleaned_x} is not a {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_x} a {cleaned_z}?"
                elif cleaned_z[0].lower() in ['a', 'e', 'i', 'o', 'u']:
                    triple_1 = f"{cleaned_x} is a {cleaned_y}."
                    triple_2 = f"{cleaned_y} is a subclass of {random_class}."
                    inferred_triple = f"{cleaned_x} is not an {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_x} an {cleaned_z}?"
                else:
                    triple_1 = f"{cleaned_x} is a {cleaned_y}."
                    triple_2 = f"{cleaned_y} is a subclass of {random_class}."
                    inferred_triple = f"{cleaned_x} is not a {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_x} a {cleaned_z}?"
                
                statement= [counter, triple_1, triple_2, question, answer, inferred_triple, label] 
                statements.append(statement)

                counter += 1
                statements_count += 1
            
    return statements, counter

# create the true and false statements
true_statements, counter= create_statements('Yes', 'True', 1, 1000)
false_statements, _= create_statements('No','False', counter, 1000)

file_path = '/Users/kaho2/Desktop/Thesis/Datasets/RDFS/Rule1/rule1_RDFS.csv'

with open(file_path, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["ID", "triple1", "triple2", "question", "answer", "inferred triple", "label"])

    # put the statements in the csv file
    for element in true_statements:
        writer.writerow(element)
    for element in false_statements:  
        writer.writerow(element)  