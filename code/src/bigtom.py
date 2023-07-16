import random
import csv
import tqdm
import argparse

from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

from utils import push_data, get_num_items, get_vars_from_out

letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'
           'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W','X', 'Y', 'Z']
DATA_DIR = '../../data'
PROMPT_DIR = '../prompt_instructions'
REPO_URL = 'https://github.com/cicl-stanford/marple_text'
CSV_NAME = 'bigtom/bigtom'

parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, default='gpt-4', help='model name')
parser.add_argument('--temperature', type=float, default=0.5, help='temperature')
parser.add_argument('--max_tokens', type=int, default=450, help='max tokens')
# change num completions to 10
parser.add_argument('--num_completions', type=int, default=1, help='number of completions')
parser.add_argument('--num_shots', type=int, default=3, help='number of shots')
parser.add_argument('--num_stories', type=int, default=1, help='number of stories to generate')
parser.add_argument('--verbose', action='store_true', help='verbose')

def get_llm(args):
    llm = ChatOpenAI(
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        n=args.num_completions,
        request_timeout=180
    )
    return llm

def gen_chat(args):
    response_template = """Here is the story:
Story: {story}
Aware of event: {awarenes}
Not aware of event: {not_aware}
Action given new state: {action_new}
Action given initial state: {action_init}
Belief Question: {belief_question}
Desire Question: {desire_question}
Action Question: {action_question}
Belief Aware: {belief_answer_aware}
Desire Aware: {desire_answer_aware}
Action Aware: {action_answer_aware}
Belief not Aware: {belief_answer_not_aware}
Desire not Aware: {desire_answer_not_aware}
Action not Aware: {action_answer_not_aware}
Random Event: {random_event}
Aware of random event: {aware_of_random_event}
Not aware of random event: {not_aware_of_random_event}"""
    llm = get_llm(args)
    with(open(f'{PROMPT_DIR}/bigtom.txt', 'r')) as f:
        instruction_text = f.read()
    system_message = SystemMessage(content=instruction_text)
    # 2-shots by default
    human_message_0 = HumanMessage(content='Generate a story')
    letter = random.choice(letters)
    human_message_1 = HumanMessage(content=f'Generate another story, using a different context, object states, and names than the examples did. The name must start with {letter}.') 
    
    
    examples = []
    template_var = ["story", "awarenes", "not_aware", "action_new", "action_init", "belief_question", "desire_question", "action_question", 
                    "belief_answer_aware", "desire_answer_aware", "action_answer_aware", "belief_answer_not_aware", "desire_answer_not_aware", 
                    "action_answer_not_aware", "random_event", "aware_of_random_event", "not_aware_of_random_event"]
    
    csv_file = f'{DATA_DIR}/{CSV_NAME}.csv'


    prompt_tokens_used = 0
    completion_tokens_used = 0

    # run loop with n stories, increase by num_completions
    for n_story in tqdm.tqdm(range(0, args.num_stories, args.num_completions)):
        letter = random.choice(letters)
        human_message_1 = HumanMessage(content=f'Generate another story, using a different context, object states, and names than the examples did. The name must start with {letter}.') 

        # read examples from csv file every iteration to add generated samples to the pool of seed examples
        if args.verbose:
            print(f"Reading examples from {csv_file} with existing {get_num_items(csv_file)} examples")
        # read a few examples from the csv file
        with open(csv_file, 'r') as f:
            for line in f.readlines():
                params = line.split(';')
                example = {k: params[v].strip() for v, k in enumerate(template_var)}
                examples.append(example)
        random.shuffle(examples)

        # 3-shots by default
        messages = [system_message]
        for i in range(args.num_shots):
            messages.append(human_message_0)
            messages.append(AIMessage(content=response_template.format(**examples[i])))
        messages.append(human_message_1)

        if args.verbose:
            print(f"------ messages ------")
            print(messages)

            
        responses = llm.generate([messages])
        prompt_tokens_used += responses.llm_output['token_usage']['prompt_tokens']
        completion_tokens_used += responses.llm_output['token_usage']['completion_tokens']
        price = (prompt_tokens_used * 0.03 + completion_tokens_used * 0.06) / 1000.
        # update tqdm progress bar with price
        tqdm.tqdm.write(f"Price: {price:.2f} USD, Price per story: {price/(n_story+args.num_completions):.2f} USD")

        for g, generation in enumerate(responses.generations[0]):
            # TODO: account for multiple completions
            if args.verbose:
                print(f"------ Generated Story {n_story+g} ------")
                print(generation.text)
                print("------------ Fin --------------")
            list_var = ["Story", "Aware of event", "Not aware of event", "Action given new state", "Action given initial state", "Belief Question", "Desire Question", "Action Question",
                        "Belief Aware", "Desire Aware", "Action Aware", "Belief not Aware",
                        "Desire not Aware", "Action not Aware", "Random Event", "Aware of random event", "Not aware of random event"]
            out_vars = get_vars_from_out(generation.text, list_var)
            data = [out_vars[k] for k in list_var]
            data += ["auto", 0]
            # write to csv file
            story_file = f'{DATA_DIR}/{CSV_NAME}.csv'
            with open(story_file, 'a') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                writer.writerow(data)
    # push to github
    # push_data(DATA_DIR, REPO_URL)
    
    
if __name__ == "__main__":
    args = parser.parse_args()
    print(f"Generating {args.num_stories} stories")
    if args.verbose:
        print(args)
    gen_chat(args)