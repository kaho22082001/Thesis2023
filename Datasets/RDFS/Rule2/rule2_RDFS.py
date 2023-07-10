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
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?predicate
WHERE {
  ?predicate rdf:type rdf:Property .
  ?predicate rdfs:label ?label .
   FILTER(
    STRSTARTS(STR(?predicate), STR(dbo:)) &&
    LANGMATCHES(LANG(?label), "en")
  )
} 
LIMIT 2900
""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

predicates = [] #list of predicates with URI
clean_predicate_list = [] #list of predicates without URI

for result in results["results"]["bindings"]:
    clean_predicate = urllib.parse.unquote(result["predicate"]["value"]).split("/")[-1] # removes the URI from predicate
    predicates.append(result["predicate"]["value"])
    clean_predicate_list.append(clean_predicate)
  
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

            SELECT DISTINCT ?x ?y ?q
            WHERE {{
              ?x <{predicate}> ?y.
              <{predicate}> rdfs:subPropertyOf ?q .
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
            predicate2_uri = result['q']['value']
            y_uri = result['y']['value'] 

            x_local = urllib.parse.unquote(x_uri).split("/")[-1]
            predicate1_local = urllib.parse.unquote(predicate1_uri).split("/")[-1]

            # splitting method based on condition
            if "#" in predicate2_uri:
                predicate2_local = urllib.parse.unquote(predicate2_uri).split("#")[-1]
            else: 
                predicate2_local = urllib.parse.unquote(predicate2_uri).split("/")[-1]

            y_local = urllib.parse.unquote(y_uri).split("/")[-1]

            # remove the underscores and parentheses
            cleaned_x = clean_element(x_local)
            cleaned_predicate1 = clean_element(predicate1_local)
            cleaned_predicate2 = clean_element(predicate2_local)
            cleaned_y = clean_element(y_local)

            # condition for true statements
            if label == 'True':

                triple_1 = f"{cleaned_x} {cleaned_predicate1} {cleaned_y}."
                triple_2 = f"{cleaned_predicate1} is a subproperty of {cleaned_predicate2}."
                inferred_triple = f"{cleaned_x} has a relation with {cleaned_y} through {cleaned_predicate2}."
                question = f"Given the previous statements, does {cleaned_x} have a relation with {cleaned_y} through {cleaned_predicate2}?"
                
                statement_true = [counter, triple_1, triple_2, question, answer, inferred_triple, label] 
                statements.append(statement_true)

                counter += 1            
                statements_count += 1

            # condition for false statements
            elif label == 'False':

                other_predicates = [] # list of predicates for incorrect triples
                for predicate_clean in clean_predicate_list:
                    # the predicates cannot be the same as the other predicates
                    if predicate_clean != cleaned_predicate1 and predicate_clean != cleaned_predicate2:
                            other_predicates.append(predicate_clean)

                other_predicates = list(set(other_predicates)) #removes duplicates
                predicate3 = random.choice(other_predicates)

                triple_1 = f"{cleaned_x} {cleaned_predicate1} {cleaned_y}."
                triple_2 = f"{cleaned_predicate1} is a subproperty of {predicate3}."
                inferred_triple = f"{cleaned_x} does not have a relation with {cleaned_y} through {cleaned_predicate2}."
                question = f"Given the previous statements, does {cleaned_x} have a relation with {cleaned_y} through {cleaned_predicate2}?"
                
                statement= [counter, triple_1, triple_2, question, answer, inferred_triple, label] 
                statements.append(statement)

                counter += 1
                statements_count += 1
            
    return statements, counter

# create the true and false statements
true_statements, counter= create_statements('Yes', 'True', 1, 1000)
false_statements, _= create_statements('No','False', counter, 1000)

file_path = '/Users/kaho2/Desktop/Thesis/Datasets/RDFS/Rule2/rule2_RDFS.csv'

with open(file_path, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["ID", "triple1", "triple2", "question", "answer", "inferred triple", "label"])

    # put the statements in the csv file
    for element in true_statements:
        writer.writerow(element)
    for element in false_statements:  
        writer.writerow(element)  