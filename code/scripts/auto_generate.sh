# This script is used to generate stories in a fully automatic way.
num_stories=5
temperature=0.7
model="openai/text-davinci-003"
target="belief"

python ../src/auto_generate.py --inference_target $target --num_stories $num_stories --model $model --temperature $temperature