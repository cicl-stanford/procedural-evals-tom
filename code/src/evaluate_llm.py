from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)


PROMPT_DIR = '../prompt_instructions'
ONE_SHOT = {'story': 'Kofi is a fisherman from a small village in Ghana. He wants to catch enough fish today to provide for his family and sell the surplus at the market. Kofi repaired his fishing net last night. While Kofi is away from his boat, a group of monkeys comes and plays with the fishing net, tearing it apart. Kofi does not see the monkeys damaging his fishing net.',
          'question': 'Does Kofi believe his fishing net is in good condition or torn apart?\nChoose one of the following:\na)Kofi believes his fishing net is in good condition.\nb)Kofi believes his fishing net is torn apart.',
          'answer': 'a)Kofi believes his fishing net is in good condition.',
          'thought': 'Let\'s think step by step:\n1) Kofi repaired his fishing net last night. So last night he believes that his net is fixed.\n2) While Kofi is away from his boat, a group of monkeys comes and plays with the fishing net, tearing it apart.\n3) Kofi does not see the monkeys damaging his fishing net. So, his belief about his net stays the same. He thinks that it is fixed.\n4) Does Kofi believe his fishing net is in good condition or torn apart?\n5) Kofi believes his fishing net is in good condition.'}
ONE_SHOT_CHAT = [HumanMessage(content="Story: {story}\nQuestion: {question}".format(story=ONE_SHOT['story'], question=ONE_SHOT['question'])), AIMessage(content="Answer: {answer}".format(answer=ONE_SHOT['answer']))]
ONE_SHOT_CHAT_COT = [HumanMessage(content="Story: {story}\nQuestion: {question}".format(story=ONE_SHOT['story'], question=ONE_SHOT['question'])), AIMessage(content="Thought: {thought}\nAnswer: {answer}".format(answer=ONE_SHOT['answer'], thought=ONE_SHOT['thought']))]



def parse_chat_response(response):
    answer_idx = response.find('Answer:')
    return response[answer_idx+8:].strip()

class EvaluateLLM():

    def __init__(self, llm, method='0shot'):
        self.llm = llm
        self.instruction = None
        self.method = method

        if method == '0shot':
            # predict answer
            self.stop_tokens = ["Story:", "Question:"]
            with(open(f'{PROMPT_DIR}/evaluate.txt', 'r')) as f:
                self.instruction = f.read()
            self.prompt = """{instruction}

Story: {story}
Question: {question}
Answer:"""
        elif method == '1shot':
            # predict answer
            self.stop_tokens = ["Story:", "Question:"]
            with(open(f'{PROMPT_DIR}/evaluate.txt', 'r')) as f:
                self.instruction = f.read()
            one_shot =  "Story: {story}\nQuestion: {question}\nAnswer: {answer}".format(story=ONE_SHOT['story'], question=ONE_SHOT['question'], answer=ONE_SHOT['answer'])
            self.prompt = "{instruction}" + "\n" + one_shot + "\n" + """

Story: {story}
Question: {question}
Answer:"""
            
        elif method == '0shot-cot':
            self.stop_tokens = ["Story:", "Question:", "Answer:"]
            with(open(f'{PROMPT_DIR}/evaluate_cot.txt', 'r')) as f:
                self.instruction = f.read()
            self.prompt = """{instruction}

Story: {story}
Question: {question}
Thought: Let's think step by step:"""
        elif method == '1shot-cot':
            self.stop_tokens = ["Story:", "Question:", "Answer:"]
            with(open(f'{PROMPT_DIR}/evaluate_cot.txt', 'r')) as f:
                self.instruction = f.read()
            one_shot =  "Story: {story}\nQuestion: {question}\nThought: {thought}\nWrite the answer as <option>) <answer>\nAnswer: {answer}".format(story=ONE_SHOT['story'], question=ONE_SHOT['question'], answer=ONE_SHOT['answer'], thought=ONE_SHOT['thought'])
            self.prompt = """{instruction}

Story: {story}
Question: {question}
Thought: Let's think step by step:"""
        elif method == 'chat-0shot' or method == 'chat-1shot':
            with open(f'{PROMPT_DIR}/evaluate.txt', 'r') as f:
                self.instruction = f.read()
            self.prompt = """Story: {story}\nQuestion: {question}"""
        
        elif method == 'chat-0shot-cot' or method == 'chat-1shot-cot':
            with open(f'{PROMPT_DIR}/evaluate_cot_chat.txt', 'r') as f:
                self.instruction = f.read()
            self.prompt = """Story: {story}\nQuestion: {question}"""

        elif method == 'eval':
            # grade answer
            self.stop_tokens = ["Predicted Answer:", "True Answer:", "Response:"]
            with(open(f'{PROMPT_DIR}/grade.txt', 'r')) as f:
                self.instruction = f.read()
            self.prompt = """{instruction}

Here is the question:
{query}
Here is the true answer:
{true_answer}
Here is the false answer:
{wrong_answer}
Here is the predicted answer:
{predicted_answer}
Is the predicted answer close to the true answer compared to the false answer? Answer True or False.
A:"""   
        else:
            raise ValueError(f"method {method} not supported")

    def predict_answer(self, story, question):
        if 'chat' in self.method:
            prompt = [SystemMessage(content=self.instruction)]
            if self.method == 'chat-1shot':
                prompt += ONE_SHOT_CHAT
            elif self.method == 'chat-1shot-cot':
                prompt += ONE_SHOT_CHAT_COT
            prompt += [HumanMessage(content=self.prompt.format(story=story, question=question))]
            response = self.llm.generate([prompt])
            response = response.generations[0][0].text
        elif 'cot' not in self.method:
            prompt = self.prompt.format(instruction=self.instruction, story=story, question=question)
            response = self.llm(prompt=prompt, stop=self.stop_tokens)
        else:
            prompt = self.prompt.format(instruction=self.instruction, story=story, question=question)
            self.llm.max_tokens = 200
            thought = self.llm(prompt=prompt, stop=self.stop_tokens)
            self.llm.max_tokens = 30
            prompt = prompt + thought + "\nWrite the answer as <option>) <answer>\nAnswer:"
            response = self.llm(prompt=prompt, stop=self.stop_tokens)
        return response
    
    def grade_answer(self, query, predicted_answer, true_answer, wrong_answer):
        prompt = self.prompt.format(instruction=self.instruction, query=query, wrong_answer=wrong_answer, predicted_answer=predicted_answer, true_answer=true_answer)
        response = self.llm(prompt=prompt, stop=self.stop_tokens)
        return response