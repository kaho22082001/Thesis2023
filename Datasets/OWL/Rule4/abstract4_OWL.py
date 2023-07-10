import csv
import random

def create_abstract_statements(letter_list, answer, label, counter):

    # The subjects for the triples
    subjects = ['A','B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']

    # A list of statements for each subject
    statements = []

    # Generate the triples and question for each subject
    for subject in subjects:
        
        for _ in range(40): 

            # Create a temporary list that excludes the current subject
            temp_list = [letter for letter in letter_list if letter != subject]

            # Select a random letter for each object and predicate
            object1 = random.choice(temp_list)

            # Check if the statements should be true
            if label == 'True':

                # Create the triples and question
                triple1 = f"{subject} is different from {object1}."
                inferred_triple = f"{object1} is different from {subject}."
                question = f"Given the previous statements, is {object1} diferent from {subject}?"

                # Add the rows to the list and update the counter
                statement = ([counter, triple1, question, answer, inferred_triple, label])
                statements.append(statement)
                counter += 1

            else:
                # Create the triples and question
                triple1 = f"{subject} is different from {subject}."
                inferred_triple = f"{object1} is not different from {subject}."
                question = f"Given the previous statements, is {object1} different from {subject}?"

                # Add the rows to the list and update the counter
                statement = ([counter, triple1, question, answer, inferred_triple, label])
                statements.append(statement)
                counter += 1
    return statements, counter

# Generate the statements using the list
letters = ['A','B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
true_abstract_statements, counter = create_abstract_statements(letters, 'Yes', 'True', 1)
false_abstract_statements, _ = create_abstract_statements(letters, 'No', 'False', counter)

# The location where the file should be saved
file_path = '/Users/kaho2/Desktop/Thesis/Datasets/OWL/Rule4/abstract4_OWL.csv'

# Creating a new file and add all rows
with open (file_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['ID','triple1', 'question', 'answer', 'inferred triple', 'label'])

    for element in true_abstract_statements:
        writer.writerow(element)
    for element in false_abstract_statements:
        writer.writerow(element)