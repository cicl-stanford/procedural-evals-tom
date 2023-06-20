method="chat-0shot"
max_tokens=20
num=100
offset=0
temperature=0
model="claude-v1.3"
# list of init beliefs
init_beliefs="0_forward 0_backward 1_forward 1_backward"
# list of conditions
conditions="false_control true_control"
# list of variables
variables="belief"

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

# list of init beliefs
init_beliefs="0_forward 1_forward"
# list of conditions
conditions="false_control true_control"
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