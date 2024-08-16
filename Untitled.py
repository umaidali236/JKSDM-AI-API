#!/usr/bin/env python
# coding: utf-8



import pandas as pd
import time
import random
from tqdm import tqdm
from random import sample




data = dict()
X = pd.ExcelFile("Sample question.xlsx")
print(f"Sheets present: {X.sheet_names} : Number of sheets in API: {len(X.sheet_names)}")

data['IT-ITes'] = pd.read_excel("Sample question.xlsx", sheet_name=2)
data['Automotive'] = pd.read_excel("Sample question.xlsx", sheet_name=3)
data['Banking and Insurance'] = pd.read_excel("Sample question.xlsx", sheet_name=4)
data['AI'] = pd.read_excel("Sample question.xlsx", sheet_name=5)


question_pack = dict()
keys = list(data.keys())
print(f"Sectors:",keys, f": {len(keys)} total sectors added to API")




all_questions = []
question_bank = dict()
num_questions_needed = 3
for key in tqdm(data.keys()):
    question_bank['sector'] = str(key).strip()
    question_bank['data'] = []
    
    for i in range(data[key].shape[0]):
        question = data[key]['Question Statement'].iloc[i].strip()
        question_difficulty = data[key]['Difficulty level'].iloc[i]
        options = dict()
        options['option1'] = str(data[key]['Option 1'].iloc[i]).strip()
        options['option2'] = str(data[key]['Option 2'].iloc[i]).strip()
        options['option3'] = str(data[key]['Option 3'].iloc[i]).strip()
        options['option4'] = str(data[key]['Option 4'].iloc[i]).strip()
        correct_option = data[key]['Correct Answer'].iloc[i]
        prepared_question = prepare_question(key,i,question,['MCQ',4,question_difficulty],list(options.values()), correct_option)
        question_bank['data'].append(prepared_question.copy())
    random.shuffle(question_bank['data'])
    question_bank['data'] = random.sample(question_bank['data'], num_questions_needed)
    all_questions.append(question_bank.copy())
    





def prepare_question(sector, qn_number, question_statement, question_params, options_list, correct_option_value):
    question=dict()
    question['question'] = dict()
    question['question']['id'] = 'Q/'+str(qn_number)+'/ID'+str(time.time()).split(".")[0] 
    question['question']['statement'] = question_statement
    question['question']['params'] = dict()
    question['question']['params']['type'] = question_params[0]
    question['question']['params']['num_options'] = question_params[1]
    question['question']['params']['difficulty'] = question_params[2]
    question['question']['correct_option'] = dict()
    random.shuffle(options_list)
    question['question']['options'] = []
    
    for i in range(len(options_list)):
        opt = dict()
        opt['id'] = 'O/'+str(i)+'/ID'+str(time.time()).split(".")[0]+str(i)
        opt['statement'] = options_list[i]
        question['question']['options'].append(opt)
        
        if str(correct_option_value).upper().strip() == str(options_list[i]).upper().strip():
            question['question']['correct_option']['id'] = opt['id']
            question['question']['correct_option']['statement'] = correct_option_value
    return question
    



# from random import sample
# def prepare_question_old(sector, qn_number, question_statement, question_params, options_list, correct_option_value):
#     question=dict()
#     question['question'] = dict()
#     question['question']['id'] = 'Q/'+str(qn_number)+'/ID'+str(time.time()).split(".")[0] 
#     question['question']['statement'] = question_statement
#     question['question']['params'] = dict()
#     question['question']['params']['type'] = question_params[0]
#     question['question']['params']['num_options'] = question_params[1]
#     question['question']['params']['difficulty'] = question_params[2]
  
#     question['question']['options'] = dict()
#     question['question']['options']['correct_option'] = dict()
    
#     random.shuffle(options_list)
    
#     for i in range(len(options_list)):
#         question['question']['options']['option'+str(i+1)] = dict()
#         question['question']['options']['option'+str(i+1)]['id'] = 'O/'+str(i)+'/ID'+str(time.time()).split(".")[0]+str(i)
#         question['question']['options']['option'+str(i+1)]['statement'] = options_list[i]
        
#         #print(str(correct_option_value).upper()==str(options_list[i]).upper() )
        
#         if str(correct_option_value).upper().strip() == str(options_list[i]).upper().strip():
#             question['question']['options']['correct_option']['id'] =question['question']['options']['option'+str(i+1)]['id'] 
#             question['question']['options']['correct_option']['statement'] = correct_option_value
#     return question
    


# In[ ]:





# In[ ]:





# In[ ]:




