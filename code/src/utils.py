import os
import csv
from subprocess import Popen, PIPE
import itertools


def edit_csv_row(filename, row_to_edit, new_data):
    if not os.path.exists(filename):
        raise Exception('No csv file found', filename)
    # Read the CSV file and store the data in a list
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        data = [row for row in reader]

    # Update the data in the desired row
    if len(data) > row_to_edit:
        data[row_to_edit] = new_data
    else:
        assert row_to_edit == len(data)
        data.append(new_data)

    # Write the updated data back to the CSV file
    print('writing to', filename)
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerows(data)

def push_data(data_dir: str, repo_url: str):

    # Get the current working directory
    cwd = os.getcwd()

    # Change the working directory to the data directory
    os.chdir(data_dir)

    # pull changes from GitHub
    p = Popen(['git', 'pull'], stdout=PIPE, stderr=PIPE) # needs to be '.' to add all files from data directory
    p.communicate()

    # Stage all changes (can send them somwhere better than github i guess?)
    p = Popen(['git', 'add', '.'], stdout=PIPE, stderr=PIPE) # needs to be '.' to add all files from data directory
    p.communicate()

    # Commit changes
    p = Popen(['git', 'commit', '-m', 'auto-commit-csv-change'], stdout=PIPE, stderr=PIPE)
    p.communicate()

    # Push changes to GitHub
    p = Popen(['git', 'push', repo_url], stdout=PIPE, stderr=PIPE)
    p.communicate()

    # Change back to the original working directory
    os.chdir(cwd)


def get_num_items(file_name: str) -> int:
    # Open the CSV file in append mode
    csv_file = f'{file_name}'
    print(csv_file)
    if not os.path.exists(csv_file):
        return 0
    num_rows = 0
    with open(csv_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            num_rows += 1
    return num_rows

def get_vars_from_out(out:str, var_list: list, stage_1=False) -> dict[str, str]:
    # Get the variables from the output
    var_dict = {}
    for lines in out.splitlines():
        for var in var_list:
            if f'{var}:' in lines:
                if stage_1:
                    var_dict[var] = ": ".join(lines.split(": ")[1:])
                else:
                    var_dict[var] = lines.split(': ')[1].strip()
    return var_dict