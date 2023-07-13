import os
import csv

DATA_DIR = '../../data'
CONDITION_DIR = os.path.join(DATA_DIR, 'conditions')
CSV_NAME = os.path.join(DATA_DIR, 'bigtom/bigtom.csv')
INITIAL_BELIEF = [0, 1] # 0 hide initial belief, 1 show initial belief
VARIABLES = ['forward_belief', 'forward_action', 'backward_belief', 'percept_to_belief']
CONDITIONS = ['true_belief', 'false_belief', 'true_control', 'false_control']

def get_completions():
    with open(CSV_NAME, "r") as f:
        reader = csv.reader(f, delimiter=";")
        completions = list(reader)
    return completions

def generate_conditions(completions):
    list_var = ["Story", "Aware of event", "Not Aware of event", "Action aware", "Action not aware", "Belief Question", "Desire Question", "Action Question",
                "Belief Answer Aware", "Desire Answer Aware", "Action Answer Aware", "Belief Answer not Aware",
                "Desire Answer not Aware", "Action Answer not Aware", "Random Event", "Aware of random event", "Not aware of random event"]

    for completion_idx, completion in enumerate(completions):

        dict_var = {list_var[i]: completion[i] for i in range(len(list_var))}
        
        for init_belief in INITIAL_BELIEF:

            for variable in VARIABLES:  

                if variable == "percept_to_belief":
                    question = dict_var["Belief Question"]
                    answers = [dict_var["Belief Answer Aware"], dict_var["Belief Answer not Aware"]]
                    # story and parts 
                    story = dict_var["Story"]
                    story_parts = dict_var["Story"].split(".")
                    
                    if init_belief == 1:
                        story = story_parts[0] + "." + story_parts[1] + "." + story_parts[2] + "." 
                        

                elif variable == "forward_belief":
                    question = dict_var["Belief Question"]
                    answers = [dict_var["Belief Answer Aware"], dict_var["Belief Answer not Aware"]]
                    awareness = [dict_var["Aware of event"], dict_var["Not Aware of event"]]
                    awareness_random = [dict_var["Aware of random event"], dict_var["Not aware of random event"]]
                    
                    # story and parts 
                    story = dict_var["Story"]
                    story_parts = dict_var["Story"].split(".")

                    # include / exclude initial belief 
                    if init_belief == 0:
                        story = story_parts[0] + "." + story_parts[1] + "." + story_parts[2] + "." + story_parts[4] + "."
                        story_control = ".".join(story_parts[:3] + [" " + dict_var["Random Event"]])
                    elif init_belief == 1:
                        story = story_parts[0] + "." + story_parts[1] + "." + story_parts[2] + "." + story_parts[3] + "."  + story_parts[4] + "."
                        story_control = ".".join(story_parts[:4] + [" " + dict_var["Random Event"]])

                elif variable == "forward_action":
                    question = dict_var["Action Question"]
                    answers = [dict_var["Action Answer Aware"], dict_var["Action Answer not Aware"]]
                    awareness = [dict_var["Aware of event"], dict_var["Not Aware of event"]]
                    awareness_random = [dict_var["Aware of random event"], dict_var["Not aware of random event"]]
                    story = dict_var["Story"]
                    story_parts = dict_var["Story"].split(".")

                    # include / exclude initial belief 
                    if init_belief == 0:
                        story = story_parts[0] + "." + story_parts[1] + "." + story_parts[2] + "." + story_parts[4] + "."
                        story_control = ".".join(story_parts[:3] + [" " + dict_var["Random Event"]])
                    elif init_belief == 1:
                        story = story_parts[0] + "." + story_parts[1] + "." + story_parts[2] + "." + story_parts[3] + "."  + story_parts[4] + "."
                        story_control = ".".join(story_parts[:4] + [" " + dict_var["Random Event"]])

                elif variable == "backward_belief":
                    question = dict_var["Belief Question"]
                    answers = [dict_var["Belief Answer Aware"], dict_var["Belief Answer not Aware"]]
                    awareness = [dict_var["Aware of event"], dict_var["Not Aware of event"]]
                    actions = [dict_var["Action aware"], dict_var["Action not aware"]]
                    awareness_random = [dict_var["Aware of random event"], dict_var["Not aware of random event"]]

                    # include / exclude initial belief 
                    if init_belief == 0:
                        story_parts = dict_var["Story"].split(".")
                        story = story_parts[0] + "." + story_parts[1] + "." + story_parts[2] + "." + story_parts[4] + "."
                        story_parts = story.split(".")
                        story_control = ".".join(story_parts[:3] + [" " + dict_var["Random Event"]])

                    elif init_belief == 1:
                        
                        story_parts = dict_var["Story"].split(".")
                        story = story_parts[0] + "." + story_parts[1] + "." + story_parts[2] + "." +  story_parts[3] + "." + story_parts[4] + "."
                        story_parts = story.split(".")
                        story_control = ".".join(story_parts[:4] + [" " + dict_var["Random Event"]])

                elif variable == "backward_desire":
                    question = dict_var["Desire Question"]
                    answers = [dict_var["Desire Answer Aware"], dict_var["Desire Answer not Aware"]]
                    if answers[0] == answers[1]:
                        # if dict_var["Alternate Desire"] != "None": # @kankishk TODO: uncomment this line once we have added alternate desires for v_3
                            # answers[1] = dict_var["Alternate Desire"]
                        # else:
                        continue
                    awareness = [dict_var["Aware of event"], dict_var["Not Aware of event"]]
                    actions = [dict_var["Action aware"], dict_var["Action not aware"]]
                    awareness_random = [dict_var["Aware of random event"], dict_var["Not aware of random event"]]

                    # include / exclude initial belief 
                    if init_belief == 0:
                        story_parts = dict_var["Story"].split(".")
                        story = story_parts[0] + "." + story_parts[2] + "." + story_parts[4] + "."
                        story_parts = story.split(".")
                        story_control = ".".join(story_parts[:2] + [" " + dict_var["Random Event"]])

                    elif init_belief == 1:
                        
                        story_parts = dict_var["Story"].split(".")
                        story = story_parts[0] + "." + story_parts[2] + "." + story_parts[3] + "." + story_parts[4] + "."
                        story_parts = story.split(".")
                        story_control = ".".join(story_parts[:3] + [" " + dict_var["Random Event"]])

                for condition in CONDITIONS:

                    # check if folder exists

                    # Write the row to the CSV file based on the condition and variable
                    if variable == "percept_to_belief":
                        if condition == "true_belief" and init_belief == 1:
                            if not os.path.exists(os.path.join(CONDITION_DIR, f'{init_belief}_{variable}_{condition}')):
                                os.makedirs(os.path.join(CONDITION_DIR, f'{init_belief}_{variable}_{condition}'))
                            new_csv_file = os.path.join(CONDITION_DIR, f'{init_belief}_{variable}_{condition}/stories.csv')
                            
                            with open(new_csv_file, "a" if completion_idx > 0 else "w", newline='') as csvfile:
                                writer = csv.writer(csvfile, delimiter=";")
                                writer.writerow([f"{story}", question, answers[0], answers[1]])
                          
                    elif variable != "percept_to_belief":
                        # Check if the new file needs to be created or appended
                        if not os.path.exists(os.path.join(CONDITION_DIR, f'{init_belief}_{variable}_{condition}')):
                            os.makedirs(os.path.join(CONDITION_DIR, f'{init_belief}_{variable}_{condition}'))
                        new_csv_file = os.path.join(CONDITION_DIR, f'{init_belief}_{variable}_{condition}/stories.csv')
                        with open(new_csv_file, "a" if completion_idx > 0 else "w", newline='') as csvfile:
                            writer = csv.writer(csvfile, delimiter=";")
                            if condition == "true_belief":
                                if variable == "backward_desire":
                                    writer.writerow([f"{story} {awareness[0]} {actions[0]}", question, answers[0], answers[1]])
                                elif variable == "backward_belief":
                                    writer.writerow([f"{story} {actions[0]}", question, answers[0], answers[1]])
                                else:
                                    writer.writerow([f"{story} {awareness[0]}", question, answers[0], answers[1]])
                            elif condition == "false_belief":
                                if variable == "backward_desire":
                                    writer.writerow([f"{story} {awareness[1]} {actions[1]}", question, answers[1], answers[0]])
                                elif variable == "backward_belief":
                                    writer.writerow([f"{story} {actions[1]}", question, answers[1], answers[0]])
                                else:
                                    writer.writerow([f"{story} {awareness[1]}", question, answers[1], answers[0]])
                            elif condition == "true_control":
                                if variable == "backward_desire":
                                    writer.writerow([f"{story_control} {awareness_random[0]} {actions[1]}", question, answers[1], answers[0]])
                                elif variable == "backward_belief":
                                    writer.writerow([f"{story_control} {actions[1]}", question, answers[1], answers[0]])
                                else:
                                    writer.writerow([f"{story_control} {awareness_random[0]}", question, answers[1], answers[0]])
                            elif condition == "false_control":
                                if variable == "backward_desire":
                                    writer.writerow([f"{story_control} {awareness_random[1]} {actions[1]}", question, answers[1], answers[0]])
                                elif variable == "backward_belief":
                                    writer.writerow([f"{story_control} {actions[1]}", question, answers[1], answers[0]])
                                else:
                                    writer.writerow([f"{story_control} {awareness_random[1]}", question, answers[1], answers[0]])


if __name__ == "__main__":  
    completions = get_completions()
    generate_conditions(completions)
