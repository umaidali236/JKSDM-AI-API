from flask import Flask, jsonify, request
import json
import pandas as pd
import time
import random
from tqdm import tqdm
from random import sample
from flask_cors import cross_origin
import urllib.parse
import xml.etree.ElementTree as ET
import unicodedata
from transformers import BertTokenizer, BertModel
import torch
import os
from tqdm import tqdm





tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
model.eval()



def get_bert_embedding(text):
    # Tokenize input text and convert to PyTorch tensors
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    # Get the embeddings for the [CLS] token
    embeddings = outputs.last_hidden_state[:, 0, :].squeeze()
    return embeddings


# def remove_diacritics(input_str):
#     # Normalize the string to separate the base characters and diacritics
#     nfkd_form = unicodedata.normalize('NFKD', input_str)
#     # Join characters that are not diacritical marks
#     return ''.join([char for char in nfkd_form if not unicodedata.combining(char)])







app = Flask(__name__)



#LOAD DATA

#PSYCHOMETRIC TEST
data = dict()
X = pd.ExcelFile("./db/Sample questions SET 2.xlsx")
print(f"Sheets present: {X.sheet_names} : Number of sheets in API: {len(X.sheet_names)}")
data["IT-ITes"] = pd.read_excel("./db/Sample question.xlsx", sheet_name=1)
data["Automotive"] = pd.read_excel("./db/Sample question.xlsx", sheet_name=3)
data["Banking and Insurance"] = pd.read_excel("./db/Sample question.xlsx", sheet_name=4)
data["AI"] = pd.read_excel("./db/Sample question.xlsx", sheet_name=5)
question_pack = dict()
keys = list(data.keys())
print(f"Sectors:",keys, f": {len(keys)} total sectors added to API")





## CAREER OPTIONS
courses = dict()
root = ET.parse('./db/all_courses.xml')
for i, item in enumerate(root.findall('course')):
    courses[i] = dict()
    if item.tag == "course": 
        for node in item:
            courses[i]['course_id'] = node.find('id').text
            courses[i]['course_level'] = node.find('level').text       
            courses[i]['course_name'] = node.find('name').text            
            courses[i]['description']= node.find('description').text
            courses[i]['parent'] = node.find('parent').text

            if not int(courses[i]['course_level'][1:]) == 100:  #non-leaf node
                #print(node.find('name').text)
                courses[i]['node_placement'] = 'non-leaf'
                courses[i]['children'] = dict()
                children = node.find('children')
                for j, child in enumerate(children.findall('child')):
                    child_type = child.find('child_type').text
                    #print(child_type)
                    child_name = child.find('child_name').text
                    courses[i]['children'][j] = {'child_type':child_type, 'child_name':child_name}
                #print(courses[i]['children'])

            if int(courses[i]['course_level'][1:]) == 100:  #leaf node

                courses[i]['node_placement'] = 'leaf'
                courses[i]['duration'] =  node.find('duration').text
                courses[i]['sector'] =  node.find('sector').text
                colleges = node.find('offline')
                courses[i]['offline'] = []
                for col in colleges.findall('college'):
                    courses[i]['offline'].append(col.text)


## NCS CAREER OPTIONS            
NCS_CAREER_PATHS = pd.read_excel('./db/CAREERS_500.xlsx')
Y_FILLED_SECTORS = NCS_CAREER_PATHS['Sector'].fillna(method='ffill', axis=0)
Y_FILLED_SECTOR_DESC = NCS_CAREER_PATHS['Sector Description'].fillna(method='ffill', axis=0)
ncs_sector_names = list(Y_FILLED_SECTORS.unique())
NCS_CAREER_PATHS['Sector'] = Y_FILLED_SECTORS
NCS_CAREER_PATHS['Sector Description'] = Y_FILLED_SECTOR_DESC
ncs_career_names = list(NCS_CAREER_PATHS['Career Name'].unique())
ncscourses = dict()
for i, ncs_sector_name in enumerate(ncs_sector_names):
    ncscourses[i] = dict()
    ncscourses[i]['course_id'] = 'C'+"".join(ncs_sector_name.split(" ")).strip()   
    ncscourses[i]['course_level'] = "D3"
    ncscourses[i]['course_name'] = ncs_sector_name
    ncscourses[i]['description']= str(NCS_CAREER_PATHS[NCS_CAREER_PATHS['Sector'] == ncs_sector_name]['Sector Description'].tolist()[0])
    ncscourses[i]['parent'] = "Intermediate (11th/12th)"
    ncscourses[i]['node_placement'] = 'non-leaf'
    if str(ncs_sector_name) == "nan":
        continue

    courses_in_ncs_sector = NCS_CAREER_PATHS[NCS_CAREER_PATHS['Sector'] == ncs_sector_name]['Career Name'].tolist().copy()
    ncscourses[i]['children'] = dict()
    for jx, cx in enumerate(courses_in_ncs_sector):
        ncscourses[i]['children'][jx] = {'child_type':'ncscourse', 'child_name':", ".join(cx.split("/"))}



for k in range(i+1, NCS_CAREER_PATHS.shape[0]+(i+1)):
    ncscourses[k] = dict()
    ncscourses[k]['course_id'] = 'C_NCS_ENDPOINT'+str(k)  
    ncscourses[k]['course_level'] = "D100"
    ncscourses[k]['course_name'] = ", ".join(NCS_CAREER_PATHS['Career Name'].iloc[k-i-1].split("/"))
    ncscourses[k]['description']= NCS_CAREER_PATHS['Career Description'].iloc[k-i-1]
    ncscourses[k]['parent'] = NCS_CAREER_PATHS['Sector'].iloc[k-i-1]
    ncscourses[k]['node_placement'] = 'leaf'
    ncscourses[k]['sector'] =  NCS_CAREER_PATHS['Sector'].iloc[k-i-1]
    ncscourses[k]['offline'] = str(NCS_CAREER_PATHS['Where will you study?'].iloc[k-i-1])
    ncscourses[k]['duration'] = ''
    ncscourses[k]['details'] = {'personalCompetencies': str(NCS_CAREER_PATHS['Personal Competencies'].iloc[k-i-1]), 
                                'whereToWork': str(NCS_CAREER_PATHS['Where will you work?'].iloc[k-i-1]),
                                'expectedGrowthPath': str(NCS_CAREER_PATHS['Expected Growth Path'].iloc[k-i-1]),
                                'fees': str(NCS_CAREER_PATHS['Fees'].iloc[k-i-1]),
                                'scholarshipsAndLoans': str(NCS_CAREER_PATHS['Scholarships & Loans'].iloc[k-i-1]),
                                'expectedIncome': str(NCS_CAREER_PATHS['Expected Income'].iloc[k-i-1]),
                                'externalLink': str(NCS_CAREER_PATHS['NCS Link'].iloc[k-i-1]).lower()

                               }


## FOREIGN LANGUAGES

####
#SELF LEARNING COURSES RECOMMENDATION
self_learning_path = "./db/CONTENT/Self-learningNEWandOLD"
self_learning_courses = dict()
for self_learning_sector_name in tqdm(os.listdir(self_learning_path)):
    self_learning_courses[self_learning_sector_name] = dict()
    
    self_learning_courses[self_learning_sector_name]['courses'] = list()
    
    self_learning_courses[self_learning_sector_name]['sector_embedding'] = get_bert_embedding(self_learning_sector_name)
    for self_learning_course_in_a_sector in os.listdir(self_learning_path+"/"+self_learning_sector_name):
        self_learning_courses[self_learning_sector_name]['courses'].append({'course_name':self_learning_course_in_a_sector, 'course_embedding':get_bert_embedding(self_learning_course_in_a_sector)})
        
        






def prepare_question(sector, qn_number, question_statement, question_params, options_list, correct_option_value):
    question=dict()
    question["question"] = dict()
    question["question"]["id"] = "Q/"+str(qn_number)+"/ID"+"".join(str(time.time()).split(".")[0:])+str(random.randint(10,99))
    question["question"]["statement"] = question_statement
    question["question"]["params"] = dict()
    question["question"]["params"]["type"] = question_params[0]
    question["question"]["params"]["num_options"] = question_params[1]
    question["question"]["params"]["difficulty"] = question_params[2]
    question["question"]["correct_option"] = dict()
    random.shuffle(options_list)
    question["question"]["options"] = []

    for i in range(len(options_list)):
        opt = dict()
        opt["id"] = "O/"+str(i+1)+"/ID"+"".join(str(time.time()).split(".")[0:])+str(i)+str(random.randint(10,99))
        opt["statement"] = options_list[i]
        question["question"]["options"].append(opt)

        if str(correct_option_value).upper().strip() == str(options_list[i]).upper().strip():
            question["question"]["correct_option"]["id"] = opt["id"]
            question["question"]["correct_option"]["statement"] = correct_option_value
    return question



# Route for the root URL
@app.route("/")
@cross_origin()
def home():
    return f"<h2>Welcome to the JKYSE API!</h2><br>Total sectors added to API: {len(keys)}<br> Sectors added to API: {keys}<br><br><h3> To Fetch Question Bank (/GET)</h3> Sample CURL: http://127.0.0.1:5000/api/v1/questionBank?sectors=[\"IT-ITes\", \"Automotive\", \"AI\"]&numQuestionsInEachSector=2"





# Route for a questionBank endpoint
@app.route("/api/v1/questionBank", methods=["GET"])
@cross_origin()
def returnQuestionBank():
    #print("Received Sectors:" + str(request.args.get("sectors")))
    sectors =  json.loads(request.args.get("sectors", "[\"IT-ITes\"]"))
    num_questions_needed =  int(request.args.get("numQuestionsInEachSector", 1))
    for s in sectors:
        if not s in keys:
            return json.dumps({"status":"fail", "message": f"Error - One or more sector not found intgerated with API:>, {s}!"})


    all_questions = []
    question_bank = dict()

    for key_num, key in tqdm(enumerate(sectors)):
        question_bank["sector"] = str(key).strip()
        question_bank["data"] = []

        for i in range(data[key].shape[0]):
            if num_questions_needed > data[key].shape[0]:
                num_questions_needed = data[key].shape[0]
            question = data[key]["Question Statement"].iloc[i].strip()
            question_difficulty = data[key]["Difficulty level"].iloc[i]
            options = dict()

            #add foreign langs sheet here
            options["option1"] = str(data[key]["Option 1"].iloc[i]).strip()
            options["option2"] = str(data[key]["Option 2"].iloc[i]).strip()
            options["option3"] = str(data[key]["Option 3"].iloc[i]).strip()
            options["option4"] = str(data[key]["Option 4"].iloc[i]).strip()
            correct_option = data[key]["Correct Answer"].iloc[i]
            prepared_question = prepare_question(key,i+1,question,["MCQ",4,question_difficulty],list(options.values()), correct_option)
            question_bank["data"].append(prepared_question.copy())
        random.shuffle(question_bank["data"])
        question_bank["data"] = random.sample(question_bank["data"], num_questions_needed)


        all_questions.append((question_bank.copy()))
        return_value = dict()
    return_value["status"] = "success"
    return_value["message"] = all_questions
    return json.dumps(return_value, indent=4)







# Route for a prepareReport endpoint
@app.route("/api/v1/prepareReport", methods=["GET"])
def report():
    x = 1
    return jsonify({"status":"success","message": f"{x}!"})




@app.route('/api/v1/ExploreCareerOptions', methods=['GET'])
@cross_origin()
def return_CareerOptions():
     # Get the 'id' query parameter from the request
    qualification = request.args.get('qualification', '10th')
    course_type = request.args.get('course_type', 'course')
    course_id = request.args.get('course_id', 'C10')
    if course_type == "course":
        for c in courses.keys():
            if courses[c]['course_name'] == qualification:
                print(courses[c]['course_name'])
                courses[c]['course_type'] = 'course'
                returnValue = {'status':'success', 'message':courses[c]}
                return jsonify(returnValue) 
    elif course_type == "ncscourse":
        for c in ncscourses.keys():
            if ncscourses[c]['course_name'] == qualification:
                print(ncscourses[c]['course_name'])
                ncscourses[c]['course_type'] ='ncscourse'
                print(ncscourses[c])
                returnValue = {'status':'success', 'message':ncscourses[c]}
                return jsonify(returnValue)
    return jsonify({'status':'fail', 'message':'Error EXC100- Course not found. Try again'})




@app.route('/api/v1/RecommendCoursesBasedOnCareerChosen', methods=['GET'])
@cross_origin()
def recommendCoursesOnCareer():
    # Get the 'id' query parameter from the request
    career_name = request.args.get('career_name', 'Computer Engineering')
    sector_name = request.args.get('sector_name', 'Information Technology') 
    cosine_similarity_with_sectors = dict()
    embedding_of_sector_name = get_bert_embedding(sector_name)
    embedding_of_career_name = get_bert_embedding(career_name)


    for self_learning_sector_name in list(self_learning_courses.keys()):
        cosine_similarity_with_sectors[self_learning_sector_name] = torch.nn.functional.cosine_similarity(embedding_of_sector_name, self_learning_courses[self_learning_sector_name]['sector_embedding'], dim=0)

    max_cosine_similarity_sector = -2
    sector_name_with_max_cosine_similarity = 'Information Technology'

    for (key, val) in cosine_similarity_with_sectors.items():
        #print(key,val)
        if val >= max_cosine_similarity_sector:
            sector_name_with_min_cosine_similarity = key
            max_cosine_similarity_sector = val
    





    #interactive courses if any
    #self learning corses if any
    # professional courses if any      
    return jsonify({'status':'success', 'sector_recommended': sector_name_with_min_cosine_similarity})





@app.route('/api/v1/RecommendDPRsBasedOnSectorChosen', methods=['GET'])
@cross_origin()
def recommend_DPRs():
     # Get the 'id' query parameter from the request
    sector = request.args.get('sector', 'IT')         
    return jsonify({'status':'under-development'})




@app.route('/api/v1/RecommendForeignLanguagesBasedOnPsychometry', methods=['GET'])
@cross_origin()
def recommend_foreign():
     # Get the 'id' query parameter from the request
    language = request.args.get('language', 'Arabic')         
    return jsonify({'status':'under-development'})



if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)


