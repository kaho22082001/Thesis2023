import csv
import random

def create_abstract_statements(letter_list, number_of_triples, answer, label, counter):
    # Keep track of the used combinations
    used_combinations = set()

    # The subjects for the triples
    subjects = ['A','B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

    # A list of statements for each subject
    statements = []

    # Generate the triples and question for each subject
    for subject in subjects:

        # Reset used combinations for each subject
        used_combinations.clear()

        while len(used_combinations) < number_of_triples:

            # Create a temporary list that excludes the current subject
            temp_list = [letter for letter in letter_list if letter != subject]

            # Select a random letter for each object and predicate
            object1, object2, object3= random.sample(temp_list, 3)

            # Check if the statements should be true
            if label == 'True':
                # Check if this combination has been used before
                if (object1, object2) not in used_combinations:
                    # If not, add it to the set of used combinations
                    used_combinations.add((object1, object2))

                    # Create the triples and question
                    triple1 = f"{subject} is a {object1}."
                    triple2 = f"{object1} is disjoint with {object2}."
                    inferred_triple = f"{subject} is not a {object2}."
                    question = f"Given the previous statements, is {subject} not a {object2}?"

                    # Add the rows to the list and update the counter
                    statement = ([counter, triple1, triple2, question, answer, inferred_triple, label])
                    statements.append(statement)
                    counter += 1

            else:
                # Check if this combination has been used before
                if (object1, object2, object3) not in used_combinations:
                    # If not, add it to the set of used combinations
                    used_combinations.add((object1, object2, object3))

                    # Create the triples and question
                    triple1 = f"{subject} is a {object1}."
                    triple2 = f"{object1} is disjoint with {object3}."
                    inferred_triple = f"{subject} could be a {object2}."
                    question = f"Given the previous statements, is {subject} not a {object2}?"


                    # Add the rows to the list and update the counter
                    statement = ([counter, triple1, triple2, question, answer, inferred_triple, label])
                    statements.append(statement)
                    counter += 1
    return statements, counter

# Generate the statements using the list
letters = ['A','B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
true_abstract_statements, counter = create_abstract_statements(letters, 11, 'Yes', 'True', 1)
false_abstract_statements, _ = create_abstract_statements(letters, 11, 'No', 'False', counter)

# The location where the file should be saved
file_path = '/Users/kaho2/Desktop/Thesis/Datasets/Simple Datasets/OWL/Rule5/abstract5_OWL.csv'

# Creating a new file and add all rows
with open (file_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['ID','triple1', 'triple2', 'question', 'answer', 'inferred triple', 'label'])

    for element in true_abstract_statements:
        writer.writerow(element)
    for element in false_abstract_statements:
        writer.writerow(element)