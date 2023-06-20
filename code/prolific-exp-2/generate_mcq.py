import json

NUM_CONDITIONS = 1

def process_data(data):
    for item in data:
        current_answers = item.get("answers", [])
        cleaned_answers = []
        labels = []

        for answer in current_answers:
            if "(Correct Answer)" in answer:
                cleaned_answer = answer.replace(" (Correct Answer)", "")
                cleaned_answers.append(cleaned_answer)
                labels.append(1)
            else:
                cleaned_answers.append(answer)
                labels.append(0)

        item["answers_no_label"] = cleaned_answers
        item["true_labels"] = labels
        
    return data

for i in range(NUM_CONDITIONS):
    json_file = './condition_' + str(i) + '.json'

    # Read the JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Process the data
    processed_data = process_data(data)

    # Write the processed data to a new JSON file
    output_file = './condition_' + str(i) + '_mcq.json'
    with open(output_file, 'w') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=4)
