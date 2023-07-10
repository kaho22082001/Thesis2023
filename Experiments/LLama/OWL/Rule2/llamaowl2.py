import torch
from transformers import LlamaTokenizer, LlamaForCausalLM
from transformers import pipeline
import csv
import random
import re


def create_input(rule_number, data_type, rule_type, mode):

    new_statements = []
    #selects the model

    model_path = 'openlm-research/open_llama_3b'
    # model_path = 'openlm-research/open_llama_7b'


    tokenizer = LlamaTokenizer.from_pretrained(model_path)
    model = LlamaForCausalLM.from_pretrained(
        model_path, torch_dtype=torch.float32, device_map='auto'
    )
    # device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    # model.to(device)
    print("model is loaded")

    with open(f"/home/kpoon/Thesis/Datasets/OWL/Rule{rule_number}/{data_type}{rule_number}_{rule_type}.csv", 'r', encoding='utf-8') as file:
    # Create a CSV reader object
        csv_reader = csv.reader(file)
        statements_list = list(csv_reader)[1:]
        
        #list gets shuffled
        random.shuffle(statements_list)

        for statement in statements_list:
            
            #zero shot testing
            if mode == "zero":

                if len(statement) == 6:
                    number_of_statements = len(statement)

                    input = f"{statement[1]} {statement[2]}"
                    prompt = f"Q: {input}\nA:"
                    input_ids = tokenizer(prompt, return_tensors="pt").input_ids

                    generation_output = model.generate(
                        input_ids=input_ids, max_new_tokens=1
                    )
                    model_result = tokenizer.decode(generation_output[0])
                    split_result = model_result.split("A:")
                    sentence = split_result[1].split("A:")[0].strip() 
                    new_statement = [statement[0], statement[1], statement[2], statement[3], statement[4], statement[5], sentence]
                    new_statements.append(new_statement)

                elif len(statement) == 7:
                    number_of_statements = len(statement)

                    input = f"{statement[1]} {statement[2]} {statement[3]}"
                    prompt = f"Q: {input}\nA:"
                    input_ids = tokenizer(prompt, return_tensors="pt").input_ids
                    generation_output = model.generate(
                        input_ids=input_ids, max_new_tokens=1
                    )
                    model_result = tokenizer.decode(generation_output[0])
                    split_result = model_result.split("A:")
                    sentence = split_result[1].split("A:")[0].strip()  
                    new_statement = [statement[0], statement[1], statement[2], statement[3], statement[4], statement[5], statement[6], sentence]
                    new_statements.append(new_statement)

                elif len(statement) == 8:
                    number_of_statements = len(statement)

                    input = f"{statement[1]} {statement[2]} {statement[3]} {statement[4]}"
                    prompt = f"Q: {input}\nA:"
                    input_ids = tokenizer(prompt, return_tensors="pt").input_ids

                    generation_output = model.generate(
                        input_ids=input_ids, max_new_tokens=1
                    )
                    model_result = tokenizer.decode(generation_output[0])
                    split_result = model_result.split("A:")
                    sentence = split_result[1].split("A:")[0].strip()   
                    print(sentence)
                    new_statement = [statement[0], statement[1], statement[2], statement[3], statement[4], statement[5], statement[6], statement[7], sentence]
                    print(new_statement)
                    new_statements.append(new_statement)

            #few shot testing
            elif mode == "few":
                
                input = ""

                other_lists = []
                for other_list in statements_list:
                    if other_list != statement:
                        other_lists.append(other_list)

                other_lists = random.sample(other_lists, 2)

                if len(statement) == 6:
                    number_of_statements = len(statement)
                    for sublist in other_lists:
                        input += " ".join(sublist[1:4]) + "\n"

                    input += " ".join(statement[1:3]) + "\n"
                    prompt = f"Q: {input}\nA:"
                    input_ids = tokenizer(prompt, return_tensors="pt").input_ids

                    generation_output = model.generate(
                        input_ids=input_ids, max_new_tokens=4
                    )
                    model_result = tokenizer.decode(generation_output[0])
                    split_result = model_result.split("A:")
                    sentence = split_result[1].split("A:")[0].strip()   
                    new_statement = [statement[0], statement[1], statement[2], statement[3], statement[4], statement[5], sentence]
                    new_statements.append(new_statement)

                elif len(statement) == 7:
                    number_of_statements = len(statement)
                    for sublist in other_lists:
                        input += " ".join(sublist[1:5]) + "\n"

                    input += " ".join(statement[1:4]) + "\n"

                    prompt = f"Q: {input}\nA:"
                    input_ids = tokenizer(prompt, return_tensors="pt").input_ids

                    generation_output = model.generate(
                        input_ids=input_ids, max_new_tokens=4
                    )
                    model_result = tokenizer.decode(generation_output[0])
                    split_result = model_result.split("A:")
                    sentence = split_result[1].split("A:")[0].strip()   
                    new_statement = [statement[0], statement[1], statement[2], statement[3], statement[4], statement[5], statement[6], sentence]
                    new_statements.append(new_statement)

                elif len(statement) == 8:
                    number_of_statements = len(statement)
                    for sublist in other_lists:
                        input += " ".join(sublist[1:6]) + "\n"

                    input += " ".join(statement[1:5]) + "\n"

                    prompt = f"Q: {input}\nA:"

                    input_ids = tokenizer(prompt, return_tensors="pt").input_ids

                    generation_output = model.generate(
                        input_ids=input_ids, max_new_tokens=4
                    )
                    model_result = tokenizer.decode(generation_output[0])
                    split_result = model_result.split("A:")
                    sentence = split_result[1].split("A:")[0].strip()   
                    new_statement = [statement[0], statement[1], statement[2], statement[3], statement[4], statement[5], statement[6], statement[7], sentence]
                    print(new_statement)
                    new_statements.append(new_statement)

    return new_statements, number_of_statements

def get_results(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
    # Create a CSV reader object
        csv_reader = csv.reader(file)
        first_row = next(csv_reader)
        statements_list = list(csv_reader)[0:]

        true_positive = 0
        false_positive = 0
        false_negative = 0 
        true_negative = 0

        results = []

        for statement in statements_list:
            if len(first_row) == 7:
                if len(statement) == 6:
                    given_answer = ''
                else:
                    given_answer = statement[6]
                true_answer = statement[3]
            elif len(first_row) == 8:
                if len(statement) == 7:
                    given_answer = ''
                else:
                    given_answer = statement[7]
                true_answer = statement[4]
            elif len(first_row) == 9:
                if len(statement) == 8:
                    given_answer = ''
                else:
                    given_answer = statement[8]
                true_answer = statement[5]
            
            if given_answer == '':
                predicted_answer = ''
            else:
                answer_parsed = given_answer.split(',')
                predicted_answer = answer_parsed[0].strip()

            if true_answer == "Yes" and ("Yes" in predicted_answer or "yes" in predicted_answer):
                true_positive += 1
            elif true_answer == "No" and ("Yes" in predicted_answer or "yes" in predicted_answer):
                false_positive += 1
            elif true_answer == "Yes" and ("No" in predicted_answer or "no" in predicted_answer):
                false_negative += 1
            elif true_answer == "No" and ("No" in predicted_answer or "no" in predicted_answer):
                true_negative += 1
            elif true_answer == "Yes" and ("Yes" not in predicted_answer or "yes" not in predicted_answer) and ("No" not in predicted_answer or "no" not in predicted_answer):
                false_negative += 1
            elif true_answer == "No" and ("Yes" not in predicted_answer or "yes" not in predicted_answer) and ("No" not in predicted_answer or "no" not in predicted_answer):
                false_positive += 1
            elif predicted_answer == '' and true_answer == "Yes":
                false_negative += 1 
            elif predicted_answer == '' and true_answer == "No":
                false_positive += 1


        if (true_positive + false_positive + false_negative + true_negative) != 0:
            accuracy = (true_positive + true_negative) / (true_positive + false_positive + false_negative + true_negative)
        else: 
            accuracy = 0

        if (true_positive + false_positive) != 0:
            precision = true_positive / (true_positive + false_positive)
        else:
            precision = 0

        if (true_positive + false_negative) != 0:
            recall = true_positive / (true_positive + false_negative)
        else:
            recall = 0
        
        if (precision + recall) != 0:
            f1 = (2 * precision * recall) / (precision + recall)
        else:
            f1 = 0

        results.append([true_positive, false_positive, false_negative, true_negative, accuracy, precision, recall, f1])
    return results

def process_and_write(rule_number, data_type, rule_type, mode, file_path):

    # call create_input with the given inputs
    created_statements, statements_number = create_input(rule_number, data_type, rule_type, mode)
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if statements_number == 6:
            writer.writerow(["ID", "triple1", "question", "answer", "inferred triple", "label", "LLM output"])
        elif statements_number == 7:
            writer.writerow(["ID", "triple1", "triple2", "question", "answer", "inferred triple", "label", "LLM output"])
        elif statements_number == 8:
            writer.writerow(["ID", "triple1", "triple2", "triple3", "question", "answer", "inferred triple", "label", "LLM output"])

        # put the statements in the csv file
        for element in created_statements:
            writer.writerow(element)    
    return file_path

file_path_zero = process_and_write("2", "rule", "OWL", "zero", "/home/kpoon/Thesis/Experiments/LLama/OWL/Rule2/llama2_results_zero.csv")
file_path2_zero = process_and_write("2", "abstract", "OWL", "zero", "/home/kpoon/Thesis/Experiments/LLama/OWL/Rule2/abstractllama2_OWL_results_zero.csv")
file_path_few = process_and_write("2", "rule", "OWL", "few", "/home/kpoon/Thesis/Experiments/LLama/OWL/Rule2/llama2_OWL_results_few.csv")
file_path2_few = process_and_write("2", "abstract", "OWL", "few", "/home/kpoon/Thesis/Experiments/LLama/OWL/Rule2/abstractllama2_OWL_results_few.csv")
file_path5 = f"/home/kpoon/Thesis/Experiments/LLama/OWL/Rule2/allllama2_OWL_results_few.csv"

print("files created")

real_statements_zero = get_results(file_path_zero)[0]
print(real_statements_zero)
abstract_statements_zero = get_results(file_path2_zero)[0]
print(abstract_statements_zero)
real_statements_few = get_results(file_path_few)[0]
abstract_statements_few = get_results(file_path2_few)[0]

print("calculations done")

with open(file_path5, 'w', newline='', encoding='utf-8') as file5:
    writer = csv.writer(file5)
    writer.writerow(["Zero shot"])
    writer.writerow(["", "DBpedia data", "abstract"])
    writer.writerow(["TP", f"{real_statements_zero[0]}", f"{abstract_statements_zero[0]}"])
    writer.writerow(["FP", f"{real_statements_zero[1]}", f"{abstract_statements_zero[1]}"])
    writer.writerow(["FN", f"{real_statements_zero[2]}", f"{abstract_statements_zero[2]}"])
    writer.writerow(["TN", f"{real_statements_zero[3]}", f"{abstract_statements_zero[3]}"])
    writer.writerow(["Accuracy", f"{real_statements_zero[4]}", f"{abstract_statements_zero[4]}"])
    writer.writerow(["Precision", f"{real_statements_zero[5]}", f"{abstract_statements_zero[5]}"])
    writer.writerow(["Recall", f"{real_statements_zero[6]}", f"{abstract_statements_zero[6]}"])
    writer.writerow(["F1 Score", f"{real_statements_zero[7]}", f"{abstract_statements_zero[7]}"])

print("results created")
with open(file_path5, 'a', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([])
    writer.writerow(["Few shot"])
    writer.writerow(["", "DBpedia data", "abstract"])
    writer.writerow(["TP", f"{real_statements_few[0]}", f"{abstract_statements_few[0]}"])
    writer.writerow(["FP", f"{real_statements_few[1]}", f"{abstract_statements_few[1]}"])
    writer.writerow(["FN", f"{real_statements_few[2]}", f"{abstract_statements_few[2]}"])
    writer.writerow(["TN", f"{real_statements_few[3]}", f"{abstract_statements_few[3]}"])
    writer.writerow(["Accuracy", f"{real_statements_few[4]}", f"{abstract_statements_few[4]}"])
    writer.writerow(["Precision", f"{real_statements_few[5]}", f"{abstract_statements_few[5]}"])
    writer.writerow(["Recall", f"{real_statements_few[6]}", f"{abstract_statements_few[6]}"])
    writer.writerow(["F1 Score", f"{real_statements_few[7]}", f"{abstract_statements_few[7]}"])
