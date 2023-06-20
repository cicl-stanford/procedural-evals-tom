import random
import json

NUM_CONDITIONS = 1
# true belief
NUM_FORWARD_BELIEF_TRUE = 5
NUM_BACKWARD_BELIEF_TRUE = 5
NUM_FORWARD_ACTION_TRUE = 5
NUM_BACKWARD_DESIRE_TRUE = 20
NUM_BACKWARD_DESIRE_TRUE_CORRECT = 5
# false belief
NUM_FORWARD_BELIEF_FALSE = 5
NUM_BACKWARD_BELIEF_FALSE = 5
NUM_FORWARD_ACTION_FALSE = 5
NUM_BACKWARD_DESIRE_FALSE = 20
NUM_BACKWARD_DESIRE_FALSE_CORRECT = 5


def read_csv(csv_file):
    with open(csv_file, 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        lines[i] = line.strip().split(';')
    return lines

def stitch_csv(tb, fb):
    combined_true = []
    combined_false = []
    for i in range(len(tb)): 
        t_story = [tb[i][0], tb[i][1], tb[i][2], fb[i][2]]
        f_story = [fb[i][0], fb[i][1], fb[i][2], tb[i][2]]
        combined_true.append(t_story)
        combined_false.append(f_story)
    return combined_true, combined_false
            
def convert_to_task(stories, data_source):
    tasks = []
    for i, s in enumerate(stories):
        if s[2] == s[3]:
            continue
        else:
            task = {}
            task['story'] = s[0]
            task['question'] = s[1]
            s[2] = s[2] + " (Correct Answer)"
            answers = s[2:]
            random.shuffle(answers)
            task['answers'] = answers
            task['data_source'] = data_source
            task['id'] = f"{data_source}_{i:02d}"
            tasks.append(task)
    return tasks

# true belief
forward_belief_true = read_csv('../../data/conditions/1_forward_belief_true_belief/stories.csv')
backward_belief_true = read_csv('../../data/conditions/1_backward_belief_true_belief/stories.csv')
forward_action_true = read_csv('../../data/conditions/1_forward_action_true_belief/stories.csv')
backward_desire_true = read_csv('../../data/conditions/1_backward_desire_true_belief/stories.csv')
# false belief
forward_belief_false = read_csv('../../data/conditions/1_forward_belief_false_belief/stories.csv')
backward_belief_false = read_csv('../../data/conditions/1_backward_belief_false_belief/stories.csv')
forward_action_false = read_csv('../../data/conditions/1_forward_action_false_belief/stories.csv')
backward_desire_false = read_csv('../../data/conditions/1_backward_desire_false_belief/stories.csv')

forward_belief_true, forward_belief_false = stitch_csv(forward_belief_true, forward_belief_false)
backward_belief_true, backward_belief_false = stitch_csv(backward_belief_true, backward_belief_false)
forward_action_true, forward_action_false = stitch_csv(forward_action_true, forward_action_false)
backward_desire_true, backward_desire_false = stitch_csv(backward_desire_true, backward_desire_false)

zipped = list(zip(forward_belief_true, 
                  backward_belief_true, 
                  forward_action_true, 
                  backward_desire_true, 
                  forward_belief_false, 
                  backward_belief_false, 
                  forward_action_false, 
                  backward_desire_false))
random.shuffle(zipped)

forward_belief_true, backward_belief_true, forward_action_true, backward_desire_true, \
    forward_belief_false, backward_belief_false, forward_action_false, backward_desire_false = zip(*zipped)

forward_belief_true = forward_belief_true[:NUM_FORWARD_BELIEF_TRUE*NUM_CONDITIONS]
backward_belief_true = backward_belief_true[:NUM_BACKWARD_BELIEF_TRUE*NUM_CONDITIONS]
forward_action_true = forward_action_true[:NUM_FORWARD_ACTION_TRUE*NUM_CONDITIONS]
backward_desire_true = backward_desire_true[:NUM_BACKWARD_DESIRE_TRUE*NUM_CONDITIONS]
forward_belief_false = forward_belief_false[:NUM_FORWARD_BELIEF_FALSE*NUM_CONDITIONS]
backward_belief_false = backward_belief_false[:NUM_BACKWARD_BELIEF_FALSE*NUM_CONDITIONS]
forward_action_false = forward_action_false[:NUM_FORWARD_ACTION_FALSE*NUM_CONDITIONS]
backward_desire_false = backward_desire_false[:NUM_BACKWARD_DESIRE_FALSE*NUM_CONDITIONS]

forward_belief_true = convert_to_task(forward_belief_true, 'forward_belief_true')
backward_belief_true = convert_to_task(backward_belief_true, 'backward_belief_true')
forward_action_true = convert_to_task(forward_action_true, 'forward_action_true')
backward_desire_true = convert_to_task(backward_desire_true, 'backward_desire_true')
forward_belief_false = convert_to_task(forward_belief_false, 'forward_belief_false')
backward_belief_false = convert_to_task(backward_belief_false, 'backward_belief_false')
forward_action_false = convert_to_task(forward_action_false, 'forward_action_false')
backward_desire_false = convert_to_task(backward_desire_false, 'backward_desire_false')



for i in range(NUM_CONDITIONS):
    json_file = './condition_' + str(i) + '.json'
    forward_belief_true = forward_belief_true[i*NUM_FORWARD_BELIEF_TRUE:(i+1)*NUM_FORWARD_BELIEF_TRUE]
    backward_belief_true = backward_belief_true[i*NUM_BACKWARD_BELIEF_TRUE:(i+1)*NUM_BACKWARD_BELIEF_TRUE]
    forward_action_true = forward_action_true[i*NUM_FORWARD_ACTION_TRUE:(i+1)*NUM_FORWARD_ACTION_TRUE]
    backward_desire_true = backward_desire_true[i*NUM_BACKWARD_DESIRE_TRUE_CORRECT:(i+1)*NUM_BACKWARD_DESIRE_TRUE_CORRECT]
    forward_belief_false = forward_belief_false[i*NUM_FORWARD_BELIEF_FALSE:(i+1)*NUM_FORWARD_BELIEF_FALSE]
    backward_belief_false = backward_belief_false[i*NUM_BACKWARD_BELIEF_FALSE:(i+1)*NUM_BACKWARD_BELIEF_FALSE]
    forward_action_false = forward_action_false[i*NUM_FORWARD_ACTION_FALSE:(i+1)*NUM_FORWARD_ACTION_FALSE]
    backward_desire_false = backward_desire_false[i*NUM_BACKWARD_DESIRE_FALSE_CORRECT:(i+1)*NUM_BACKWARD_DESIRE_FALSE_CORRECT]
    tasks = forward_belief_true + backward_belief_true + forward_action_true + backward_desire_true + \
        forward_belief_false + backward_belief_false + forward_action_false + backward_desire_false
    random.shuffle(tasks)
    with open(json_file, 'w') as f:
        json.dump(tasks, f)
    

