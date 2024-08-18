from flask import Flask, jsonify, request
import json
import pandas as pd
import time
import random
from tqdm import tqdm
from random import sample
from flask_cors import cross_origin
import urllib.parse

app = Flask(__name__)



#LOAD DATA
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




# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)
