import os
import csv
import random

from flask import Flask, render_template, request

# from gen_fns import 
from utils import push_data, get_num_items, edit_csv_row

app = Flask(__name__)
DATA_DIR = '../../data'
REPO_URL = 'https://github.com/cicl-stanford/marple_text'

# get index
@app.route('/')
def index():
    return render_template('expert_evaluate.html')


def get_num_stories(name):
    num_stories = get_num_items(f'{DATA_DIR}/ratings/{name}.csv')
    return num_stories


def get_stories(evaluator):
    eval_file = f'{DATA_DIR}/ratings/{evaluator}.csv'
    if os.path.exists(eval_file):
        # get the id of the last story rated
        with open(eval_file, 'r') as f:
            lines = list(csv.reader(f, delimiter=';'))
        idx = sum([1 for l in lines if len(l)==2])
    else:
        idx = 0
    
    story_dict = {}
    story_file = f'{DATA_DIR}/chat/story_v4.csv'
    if not os.path.exists(story_file):
        raise Exception('No context file found')
    with open(story_file, 'r') as f:
        stories = list(csv.reader(f, delimiter=';'))
    if idx >= len(stories):
        raise Exception('No more stories to rate')
    story_dict['context'] = stories[idx][0]
    story_dict[f'perception'] = f"{stories[idx][1]};{stories[idx][2]}"
    story_dict[f'action'] = f"{stories[idx][3]};{stories[idx][4]}"
    story_dict[f'belief_question'] = stories[idx][5]
    story_dict[f'desire_question'] = stories[idx][6]
    story_dict[f'action_question'] = stories[idx][7]
    story_dict[f'belief_answer'] = f"{stories[idx][8]};{stories[idx][11]}"
    story_dict[f'desire_answer'] = f"{stories[idx][9]};{stories[idx][12]}"
    story_dict[f'action_answer'] = f"{stories[idx][10]};{stories[idx][13]}"
    # story_dict[f'alt_desire'] = stories[idx][14]
    story_dict[f'distractor'] = stories[idx][14]
    story_dict[f'distractor_percept'] = f"{stories[idx][15]};{stories[idx][16]}"
    return story_dict, idx

# load story
@app.route('/load_story', methods=['POST'])
def load():
    evaluator = request.form['evaluator']
    data, idx = get_stories(evaluator)
    data['row'] = idx
    data['num_stories'] = get_num_stories(request.form['evaluator'])
    return data

# save data
@app.route('/store', methods=['POST'])
def store():
    evaluator = request.form['evaluator']
    row = int(request.form['row'])
    story_file = f'{DATA_DIR}/chat/story_v4.csv'
    with open(story_file, 'r') as f:
        stories = list(csv.reader(f, delimiter=';'))
        story = stories[row]
    # print(story[3], story[4])
    story[3] = request.form['action_aware']
    story[4] = request.form['action_not_aware']
    # story[14] = request.form['alt_desire']
    print(story[3], story[4])
    
    edit_csv_row(story_file, row, story)
    data = [request.form.get(f) for f in ["story_structure", "behavior_evaluation"]]
    eval_csv = f'{DATA_DIR}/ratings/{evaluator}.csv'
    row = int(request.form.get('row'))
    edit_csv_row(eval_csv, row, data)
    data = {}
    data, idx = get_stories(evaluator)
    data['row'] = idx
    data['num_stories'] = get_num_stories(request.form.get('evaluator'))
    # Auto push the data to GitHub
    # push_data(DATA_DIR, REPO_URL)
    return data


if __name__ == '__main__':
    app.run(debug=True)