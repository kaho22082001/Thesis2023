import csv
import random

def create_abstract_statements(letter_list, number_of_triples, answer, label, counter):
    # Keep track of the used combinations
    used_combinations = set()

    # The subjects for the triples
    subjects = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

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
            object1, object2, object3, predicate1 = random.sample(temp_list, 4)

            # Check if the statements should be true
            if label == 'True':
                # Check if this combination has been used before
                if (object1, object2, predicate1) not in used_combinations:
                    # If not, add it to the set of used combinations
                    used_combinations.add((object1, object2, predicate1))

                    # Create the triples and question
                    triple1 = f"{subject} {predicate1} {object1}."
                    triple2 = f"{predicate1} has domain {object2}."
                    inferred_triple = f"{subject} is a {object2}."
                    question = f"Given the previous statements, is {subject} a {object2}?"

                    # Add the rows to the list and update the counter
                    statement = ([counter, triple1, triple2, question, answer, inferred_triple, label])
                    statements.append(statement)
                    counter += 1

            else:
                # Check if this combination has been used before
                if (object1, object2, object3, predicate1) not in used_combinations:
                    # If not, add it to the set of used combinations
                    used_combinations.add((object1, object2, object3, predicate1))

                    # Create the triples and question
                    triple1 = f"{subject} {predicate1} {object1}."
                    triple2 = f"{predicate1} has domain {object3}."
                    inferred_triple = f"{subject} is not a {object2}."
                    question = f"Given the previous statements, is {subject} a {object2}?"

                    # Add the rows to the list and update the counter
                    statement = ([counter, triple1, triple2, question, answer, inferred_triple, label])
                    statements.append(statement)
                    counter += 1
    return statements, counter

# Generate the statements using the list
letters = ['A','B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
true_abstract_statements, counter = create_abstract_statements(letters, 100, 'Yes', 'True', 1)
false_abstract_statements, _ = create_abstract_statements(letters, 100, 'No', 'False', counter)

# The location where the file should be saved
file_path = '/Users/kaho2/Desktop/Thesis/Datasets/RDFS/Rule3/abstract3_RDFS.csv'

# Creating a new file and add all rows
with open (file_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['ID','triple1', 'triple2', 'question', 'answer', 'inferred triple', 'label'])

    for element in true_abstract_statements:
        writer.writerow(element)
    for element in false_abstract_statements:
        writer.writerow(element)