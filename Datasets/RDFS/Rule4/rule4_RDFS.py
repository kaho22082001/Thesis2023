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
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?predicate
WHERE {
  ?predicate rdf:type rdf:Property .
   FILTER(
    STRSTARTS(STR(?predicate), STR(dbo:))
  )
} 
LIMIT 2800
""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

predicates = [] #list of predicates with URI
clean_predicate_list = [] #list of predicates without URI

for result in results["results"]["bindings"]:
    clean_predicate = urllib.parse.unquote(result["predicate"]["value"]).split("/")[-1] # removes the URI from predicate
    predicates.append(result["predicate"]["value"])
    clean_predicate_list.append(clean_predicate)

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
LIMIT 500
""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

clean_class_list = [] #list of classes without URI

for result in results["results"]["bindings"]:
    created_class = urllib.parse.unquote(result["class"]["value"]).split("/")[-1] #removes the URI from Class
    clean_class = clean_element(created_class)
    clean_class_list.append(clean_class)
  
def create_statements(answer, label, counter, max_statements):

    statements = [] 
    statements_count = 0
    query_count = 0

    for predicate in predicates:

        if statements_count >= max_statements:  # break the loop if the maximum number of statements is reached
            break

        sparql.setQuery(f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX dbp: <http://dbpedia.org/resource/>

            SELECT DISTINCT ?x ?y ?z
            WHERE {{
                ?x <{predicate}> ?y.
                <{predicate}> rdfs:range ?z .
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
            predicate1_uri = predicate 
            y_uri = result['y']['value'] 
            z_uri = result['z']['value']

            x_local = urllib.parse.unquote(x_uri).split("/")[-1]
            predicate1_local = urllib.parse.unquote(predicate1_uri).split("/")[-1]
            y_local = urllib.parse.unquote(y_uri).split("/")[-1]
            z_local = urllib.parse.unquote(z_uri).split("/")[-1]

            # remove the underscores and parentheses
            cleaned_x = clean_element(x_local)
            cleaned_predicate1 = clean_element(predicate1_local)
            cleaned_y = clean_element(y_local)
            cleaned_z = clean_element(z_local)

            # condition for true statements
            if label == 'True':

                if cleaned_z[0].lower() in ['a', 'e', 'i', 'o', 'u']:
                    triple_1 = f"{cleaned_x} {cleaned_predicate1} {cleaned_y}."
                    triple_2 = f"{cleaned_predicate1} has range {cleaned_z}."
                    inferred_triple = f"{cleaned_y} is an {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_y} an {cleaned_z}?"
                else:
                    triple_1 = f"{cleaned_x} {cleaned_predicate1} {cleaned_y}."
                    triple_2 = f"{cleaned_predicate1} has range {cleaned_z}."
                    inferred_triple = f"{cleaned_y} is a {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_y} a {cleaned_z}?"
                
                statement_true = [counter, triple_1, triple_2, question, answer, inferred_triple, label] 
                statements.append(statement_true)

                counter += 1            
                statements_count += 1

            # condition for false statements
            elif label == 'False':

                temp_list = [] # list of classes for incorrect triples
                for class_clean in clean_class_list:
                    # the class cannot be the same as the other classes
                    if class_clean != cleaned_z and class_clean != cleaned_y:
                            temp_list.append(class_clean)

                random_class = random.choice(temp_list)

                if cleaned_z[0].lower() in ['a', 'e', 'i', 'o', 'u']:
                    triple_1 = f"{cleaned_x} {cleaned_predicate1} {cleaned_y}."
                    triple_2 = f"{cleaned_predicate1} has range {random_class}."
                    inferred_triple = f"{cleaned_y} is not an {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_y} an {cleaned_z}?"
                else:
                    triple_1 = f"{cleaned_x} {cleaned_predicate1} {cleaned_y}."
                    triple_2 = f"{cleaned_predicate1} has range {random_class}."
                    inferred_triple = f"{cleaned_y} is not a {cleaned_z}."
                    question = f"Given the previous statements, is {cleaned_y} a {cleaned_z}?"
                
                statement_true = [counter, triple_1, triple_2, question, answer, inferred_triple, label] 
                statements.append(statement_true)

                counter += 1
                statements_count += 1
            
    return statements, counter

# create the true and false statements
true_statements, counter= create_statements('Yes', 'True', 1, 1000)
false_statements, _= create_statements('No','False', counter, 1000)

file_path = '/Users/kaho2/Desktop/Thesis/Datasets/RDFS/Rule4/rule4_RDFS.csv'

with open(file_path, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["ID", "triple1", "triple2", "question", "answer", "inferred triple", "label"])

    # put the statements in the csv file
    for element in true_statements:
        writer.writerow(element)
    for element in false_statements:  
        writer.writerow(element)  