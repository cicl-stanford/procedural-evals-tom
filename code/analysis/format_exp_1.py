import ast
import pandas as pd

DATA_PATH = "../../data/prolific/exp_1/"
N_TRIALS = 30

df_trials = pd.read_csv(DATA_PATH + "main_01_trials_complete.csv")
df_ids = pd.read_csv(DATA_PATH + "main_01_ids_complete.csv")
df_exit = pd.read_csv(DATA_PATH + "main_01_exit_complete.csv")

# Initialize an empty list to hold the transformed data
data = []
a = True
# Loop over each row in the DataFrame
for i, row in df_trials.iterrows():

    prolific_id = df_ids.iloc[i]["prolificPid"]
    exit_survey = df_exit.iloc[i]
    age = exit_survey["age"]
    ethnicity = exit_survey["ethnicity"]
    gender = exit_survey["gender"]
    race = exit_survey["race"]
    
    # Loop over trials
    for trial in range(1, N_TRIALS + 1):
        # Get item ratings
        item = ast.literal_eval(row[f"trial{trial}"])
        item_ratings = item["likertResponses"]
        ratings = [int(item_ratings[key]) for key in sorted(item_ratings.keys())]
        average_rating = sum(ratings) / len(ratings)

        # Group survey types
        survey_type_dict = {
            "dodell": "expert",
            "ullman": "expert",
            "kosinski": "expert",
            "false_belief": "ours",
            "true_belief": "ours",
            "social_iqa": "social_iqa",
        }
        survey_type = survey_type_dict.get(item["data_source"], "unknown")

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
            "understandability": ratings[0],
            "coherent_q_a": ratings[1],
            "unambiguous": ratings[2],
            "average_rating": average_rating,
        })

# Convert the list of dictionaries into a DataFrame
df_long = pd.DataFrame(data)

# Sort DataFrame
df_long.sort_values(by=['survey_type', 'item_id'], inplace=True)

# Save the DataFrame as a CSV file
df_long.to_csv(DATA_PATH + "main_01_long.csv", index=False)