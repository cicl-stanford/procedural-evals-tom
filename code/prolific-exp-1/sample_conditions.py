import random
import json

NUM_CONDITIONS = 5
NUM_EXPERT_STORIES = 5
NUM_CROWD_STORIES = 5
NUM_TRUE_BELIEF = 10
NUM_FALSE_BELIEF = 10

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

ullman = read_csv('../../data/expert_data/ullman.csv')[:8]
dodell_feder = read_csv('../../data/expert_data/dodell-feder.csv')[:8]
kosinski = read_csv('../../data/expert_data/kosinski.csv')[:9]
expert_stories = convert_to_task(ullman, 'ullman') + convert_to_task(dodell_feder,'dodell') + convert_to_task(kosinski, 'kosinski')
crowd_stories = read_csv('../../data/social_iqa/social_iqa.csv')[:25]
crowd_stories = convert_to_task(crowd_stories, 'social_iqa')

true_belief = read_csv('../../data/conditions/1_belief_true_belief/stories.csv')
false_belief = read_csv('../../data/conditions/1_belief_false_belief/stories.csv')
true_belief, false_belief = stitch_csv(true_belief, false_belief)
zipped = list(zip(true_belief, false_belief))
random.shuffle(zipped)
true_belief, false_belief = zip(*zipped)
true_belief = true_belief[:NUM_TRUE_BELIEF*NUM_CONDITIONS]
false_belief = false_belief[NUM_FALSE_BELIEF*NUM_CONDITIONS:NUM_FALSE_BELIEF*NUM_CONDITIONS*2]
true_belief = convert_to_task(true_belief, 'true_belief')
false_belief = convert_to_task(false_belief, 'false_belief')

for i in range(NUM_CONDITIONS):
    json_file = './condition_' + str(i) + '.json'
    expert = expert_stories[i*NUM_EXPERT_STORIES:(i+1)*NUM_EXPERT_STORIES]
    crowd = crowd_stories[i*NUM_CROWD_STORIES:(i+1)*NUM_CROWD_STORIES]
    true = true_belief[i*NUM_TRUE_BELIEF:(i+1)*NUM_TRUE_BELIEF]
    false = false_belief[i*NUM_FALSE_BELIEF:(i+1)*NUM_FALSE_BELIEF]
    tasks = expert + crowd + true + false
    random.shuffle(tasks)
    with open(json_file, 'w') as f:
        json.dump(tasks, f)
    

