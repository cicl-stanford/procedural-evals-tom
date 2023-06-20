method="chat-1shot-cot"
max_tokens=220
num=200
offset=0
temperature=0
model="gpt-4"
# list of init beliefs
init_beliefs="1_backward"
# list of conditions
conditions="true_belief"
# list of variables
variables="belief"

# for init_belief in $init_beliefs
# do
#     for condition in $conditions
#     do
#         for variable in $variables
#         do
#             python ../src/evaluate_conditions.py -n $num --init_belief $init_belief --method $method --condition $condition --variable $variable --mcq --model_name $model --max_tokens $max_tokens --temperature $temperature --offset $offset
#         done
#     done
# done


# list of init beliefs
init_beliefs="1_forward"
# list of conditions
conditions="true_belief"
# list of variables
variables="action"

for init_belief in $init_beliefs
do
    for condition in $conditions
    do
        for variable in $variables
        do
            python ../src/evaluate_conditions.py -n $num --init_belief $init_belief --method $method --condition $condition --variable $variable --mcq --model_name $model --max_tokens $max_tokens --temperature $temperature --offset $offset
        done
    done
done