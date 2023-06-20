import os
import random
import csv
import tqdm
import argparse
from crfm_llm import crfmLLM
from evaluate_llm import EvaluateLLM
from langchain.chat_models import ChatOpenAI, ChatAnthropic
from langchain import HuggingFaceHub, HuggingFacePipeline
from langchain.llms import LlamaCpp
from evaluate_llm import parse_chat_response

DATA_DIR = '../../data'
MODEL_DIR = 'llama.cpp/models'
CONDITION_DIR = os.path.join(DATA_DIR, 'conditions')
RESULTS_DIR = os.path.join(DATA_DIR, 'results')
PROMPT_DIR = '../prompt_instructions'
random.seed(0)


def evaluate_condition(eval_model, model_name, temperature, method,
                    init_belief, variable, condition, num_probs,
                    max_tokens, verbose, mcq, offset):

    if 'openai' in model_name:
        llm = crfmLLM(model_name=model_name, temperature=temperature, max_tokens=max_tokens, verbose=False)
    elif 'llama' in model_name:
        if 'llama-65' in model_name:
            llm = LlamaCpp(model_path=f"{MODEL_DIR}/65B/ggml-model-q5_1.bin", n_ctx=1536, max_tokens=max_tokens, temperature=temperature, n_threads=16, n_batch=16)
        elif 'llama-33' in model_name:
            llm = LlamaCpp(model_path=f"{MODEL_DIR}/33B/ggml-model-q5_1.bin", n_ctx=1536, max_tokens=max_tokens, temperature=temperature, n_threads=16, n_batch=16)
        elif 'llama-13' in model_name:
            llm = LlamaCpp(model_path=f"{MODEL_DIR}/13B/ggml-model-q5_1.bin", n_ctx=1536, max_tokens=max_tokens, temperature=temperature, n_threads=16, n_batch=16)
        elif 'llama-7' in model_name:
            llm = LlamaCpp(model_path=f"{MODEL_DIR}/7B/ggml-model-q5_1.bin", n_ctx=1536, max_tokens=max_tokens, temperature=temperature, n_threads=16, n_batch=16)
            # repo_id = "decapoda-research/llama-65b-hf"
            # llm = HuggingFacePipeline.from_model_id(model_id=repo_id, task="text-generation", model_kwargs={"temperature":temperature, "max_new_tokens":max_tokens})
            # llm = HuggingFaceHub(repo_id=repo_id, model_kwargs={"temperature":temperature, "max_length":max_tokens})
    elif model_name in ['gpt-4', 'gpt-3.5-turbo']:
        llm = ChatOpenAI(
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        n=1,
        request_timeout=180
    )
    elif model_name in ['claude-v1.3', 'claude-instant-v1.1']:
        llm = ChatAnthropic(
        model=model_name,
        temperature=temperature,
        max_tokens_to_sample=max_tokens,
    )
    else:
        raise ValueError(f"Model {model_name} not supported")
    test_model = EvaluateLLM(llm, method=method)

    if 'openai' in eval_model:
        eval_llm = crfmLLM(model_name=eval_model, temperature=0, max_tokens=10, verbose=False)
    eval_model = EvaluateLLM(eval_llm, method='eval')

    # load condition csv    
    csv_name = os.path.join(CONDITION_DIR, f'{init_belief}_{variable}_{condition}/stories.csv')
    with open(csv_name, "r") as f:
        reader = csv.reader(f, delimiter=";")
        condition_rows = list(reader)

    predicted_answers = []
    graded_answers = []

    for row in tqdm.tqdm(condition_rows[offset:num_probs]):
        story = row[0]
        question_orig = row[1]
        question = row[1]
        true_answer, wrong_answer = row[2], row[3]
        answers = [true_answer, wrong_answer]
        random.shuffle(answers)
        if mcq:
            question = f"{question}\nChoose one of the following:\na){answers[0]}\nb){answers[1]}"
        predicted_answer = test_model.predict_answer(story, question).strip()
        if verbose:
            print(f"story: {story}")
            print(f"question: {question}")
            print(f"true answer: {true_answer}")
            print(f"wrong answer: {wrong_answer}")
            print(f"predicted answer: {predicted_answer}")
        if answers[0] == true_answer:
            answer_key = 'a)'
            negative_answer_key = 'b)'
            true_answer = 'a) ' + true_answer
            wrong_answer = 'b) ' + wrong_answer
        else:
            answer_key = 'b)'
            negative_answer_key = 'a)'
            true_answer = 'b) ' + true_answer
            wrong_answer = 'a) ' + wrong_answer
        if mcq:
            predicted_answer_parsed = predicted_answer
            if method == 'chat-0shot-cot':
                predicted_answer_parsed = parse_chat_response(predicted_answer)
            if answer_key in predicted_answer_parsed.lower():
                graded_answer = 'True'
            elif negative_answer_key in predicted_answer_parsed.lower():
                graded_answer = 'False'
            else:
                print(f"predicted answer: {predicted_answer}")
                print(f"true answer: {true_answer}")
                print(f"wrong answer: {wrong_answer}")
                # user_grade = input("Please grade the answer (True:1/False:0): ")
                # graded_answer = True if user_grade == '1' else False
                graded_answer = eval_model.grade_answer(question_orig, predicted_answer_parsed, true_answer, wrong_answer).strip()
                print(f"graded answer: {graded_answer}")
        else:
            if method == 'chat-0shot-cot':
                predicted_answer_parsed = parse_chat_response(predicted_answer)
                graded_answer = eval_model.grade_answer(question_orig, predicted_answer_parsed, true_answer, wrong_answer).strip()
            else:
                graded_answer = eval_model.grade_answer(question_orig, predicted_answer, true_answer, wrong_answer).strip()
        predicted_answers.append(predicted_answer)
        graded_answers.append(graded_answer)
        if verbose:
            print(f"graded answer: {graded_answer}")

    # save results
    model_name = model_name.replace('/', '_')
    prediction = os.path.join(RESULTS_DIR, f'{init_belief}_{variable}_{condition}/prediction_{model_name}_{temperature}_{method}_{variable}_{condition}_{offset}_{num_probs}.csv')
    accuracy_file = os.path.join(RESULTS_DIR, f'{init_belief}_{variable}_{condition}/accuracy_{model_name}_{temperature}_{method}_{variable}_{condition}_{offset}_{num_probs}.csv')

    if not os.path.exists(os.path.join(RESULTS_DIR, f'{init_belief}_{variable}_{condition}')):
        os.makedirs(os.path.join(RESULTS_DIR, f'{init_belief}_{variable}_{condition}'))
    
    with open(prediction, "w") as f:
        writer = csv.writer(f, delimiter=";")
        # write a new row per element in predicted answers 
        for predicted_answer in predicted_answers:
            writer.writerow([predicted_answer])

    with open(accuracy_file, "w") as f:
        writer = csv.writer(f, delimiter=";")
        # write a new row per element in graded answers
        for graded_answer in graded_answers:
            writer.writerow([graded_answer])

    # accuracy 
    accuracy = graded_answers.count('True') / len(graded_answers)

    # Print results
    print("\n------------------------")
    print("         RESULTS        ")
    print("------------------------")
    print(f"MODEL: {model_name}, Temperature: {temperature}, Method: {method}")
    print(f"CONDITION: {init_belief} {variable}, {condition}")
    print(f"ACCURACY: {accuracy:.2%}")
    print("------------------------\n")
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--variable', type=str, default='belief')
    parser.add_argument('--condition', type=str, default='true_belief')
    parser.add_argument('--eval_model', type=str, default='openai/text-davinci-003')
    parser.add_argument('--model_name', type=str, default='openai/text-davinci-003')
    parser.add_argument('--temperature', type=float, default=0.0)
    parser.add_argument('--num_probs', '-n', type=int, default=1)
    parser.add_argument('--offset', '-o', type=int, default=0)
    parser.add_argument('--max_tokens', type=int, default=100)
    parser.add_argument('--method', type=str, default='0shot')
    parser.add_argument('--init_belief', type=str, default="0_backward")
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--mcq', action='store_true')
    args = parser.parse_args()

    evaluate_condition(args.eval_model, args.model_name, args.temperature,
                       args.method, args.init_belief, args.variable,
                       args.condition, args.num_probs, args.max_tokens, args.verbose, args.mcq, args.offset)

if __name__ == '__main__':
    main()