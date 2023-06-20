##  

A Domain-Agnostic Method for Procedurally Generating LLM Evaluations

![Causal Template -> Prompt Template -> Test Items](./assets/generation.jpg)


### 🧐 What is this?
We have developed a method that uses large language models (LLMs) to procedurally generate evaluations for other LLMs. We initially applied this method to assess the performance of LLMs in a subdomain of social reasoning (Theory-of-Mind). Please checkout our [paper](https://sites.google.com/view/social-reasoning-lms) for further details.


### 📂 Repro structure
```
├── code                 
│   └── analysis
│   └── prolific-exp-1
│   └── prolific-exp-2
│   └── prompt_instructions
│   └── scripts
│   └── src 
├── data   
│   ├── bigtom    
│   └── expert_data
│   └── social_iqa
│   └── prolific
├── .gitignore
├── LICENSE            
└── requirements.txt
```

### 🚀 Getting started 
#### Using miniconda
1. `curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh`
2. `bash Miniconda3-latest-MacOSX-x86_64.sh`
3. close and reopen terminal
4. `source ~/.bashrc`
5. `conda create --name name-of-my-env python==3.10`
6. `conda activate name-of-my-env`
7. `pip install -r requirements.txt` 