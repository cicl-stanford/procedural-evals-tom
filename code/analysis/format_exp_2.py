import ast
import pandas as pd

DATA_PATH = "../../data/prolific/exp_2/"
N_TRIALS_1= 42
N_TRIALS_2 = 12

df_trials = pd.read_csv(DATA_PATH + "main_02_trials_1.csv")
df_ids = pd.read_csv(DATA_PATH + "main_02_ids_1.csv")
df_exit = pd.read_csv(DATA_PATH + "main_02_exit_1.csv")

df_trials_2 = pd.read_csv(DATA_PATH + "main_02_trials_2.csv")
df_ids_2 = pd.read_csv(DATA_PATH + "main_02_ids_2.csv")
df_exit_2 = pd.read_csv(DATA_PATH + "main_02_exit_2.csv")

# Initialize an empty list to hold the transformed data
data = []


# Loop over each row in the DataFrame
for i, row in df_trials.iterrows():
    prolific_id = df_ids.iloc[i]["prolificPid"]
    exit_survey = df_exit.iloc[i]
    age = exit_survey["age"]
    ethnicity = exit_survey["ethnicity"]
    gender = exit_survey["gender"]
    race = exit_survey["race"]
    # Loop over trials
    for trial in range(1, N_TRIALS_1 + 1):
        item = ast.literal_eval(row[f"trial{trial}"])
        item_id = item["id"]
        response = item["selected_answer_idx"]
        true_answers = item["true_labels"]
        correct = int(true_answers[int(response)]) == 1
        if item_id == "attention_check_1":
            correct = int(response) == 0
        elif item_id == "attention_check_2":
            correct = int(response) == 1
        survey_type = item["data_source"]
         # split survey 
        true_false = survey_type.split("_")[-1]
        tf = None
        if true_false == "true":
            tf = True
        elif true_false == "false":
            tf = False
        if "backward" not in item_id and tf is not None: # ignore backward_desire and backward_belief
            # Append transformed data to the list
            data.append({
                "data_source": item["data_source"],
                "split": row["proliferate.condition"],
                "survey_type": survey_type,
                "item_id": item["id"],
                "worker_id": row["workerid"],
                "prolific_id": prolific_id,
                "age": age,
                "ethnicity": ethnicity,
                "gender": gender,
                "race": race, 
                "item_story": item["story"],
                "item_question": item["question"],
                "item_answers": item["answers"],
                "item_true_answers": true_answers,
                "response": response,
                "correct": int(correct),
                "true_false": tf,
            })
        else:
            continue


for i, row in df_trials_2.iterrows():
    prolific_id = df_ids_2.iloc[i]["prolificPid"]
    exit_survey = df_exit_2.iloc[i]
    age = exit_survey["age"]
    ethnicity = exit_survey["ethnicity"]
    gender = exit_survey["gender"]
    race = exit_survey["race"]
    # Loop over trials
    for trial in range(1, N_TRIALS_2 + 1):
        item = ast.literal_eval(row[f"trial{trial}"])
        item_id = item["id"]
        response = item["selected_answer_idx"]
        true_answers = item["true_labels"]
        correct = int(true_answers[int(response)]) == 1
        if item_id == "attention_check_1":
            correct = int(response) == 0
        elif item_id == "attention_check_2":
            correct = int(response) == 1
        survey_type = item["data_source"]
        
        # split survey 
        tf = None
        true_false = survey_type.split("_")[-1]
        if true_false == "true":
            tf = True
        elif true_false == "false":
            tf = False

       
        # Append transformed data to the list
        if tf is not None:
            data.append({
                "data_source": item["data_source"],
                "split": row["proliferate.condition"],
                "survey_type": survey_type,
                "item_id": item["id"],
                "worker_id": row["workerid"],
                "prolific_id": prolific_id,
                "age": age,
                "ethnicity": ethnicity,
                "gender": gender,
                "race": race, 
                "item_story": item["story"],
                "item_question": item["question"],
                "item_answers": item["answers"],
                "item_true_answers": true_answers,
                "response": response,
                "correct": int(correct),
                "true_false": tf,
            })




# Convert the list of dictionaries into a DataFrame
df_long = pd.DataFrame(data)

# Sort DataFrame
df_long.sort_values(by=['survey_type', 'item_id'], inplace=True)

# Save the DataFrame as a CSV file
df_long.to_csv(DATA_PATH + "main_02_long.csv", index=False)

