from flask import Flask, jsonify, request
import json
import pandas as pd
import time
import random
from flask_cors import cross_origin
from tqdm import tqdm
app = Flask(__name__)




#LOAD DATA
print("Loading Questions for Psychometry")
#PSYCHOMETRIC TEST
psychometry_data_location= "../db/Sample question_38 courses.xlsx"
psychometry_data = dict()
psychometry_data["IT-ITeS"] = pd.read_excel(psychometry_data_location, sheet_name=0)
psychometry_data["Power and Electrical"] = pd.read_excel(psychometry_data_location, sheet_name=1)
psychometry_data["Rubber, Chemical and Petrochemical"] = pd.read_excel(psychometry_data_location, sheet_name=3)
psychometry_data["Apparel, Made-Ups & Home Furnishing"] = pd.read_excel(psychometry_data_location, sheet_name=29)
psychometry_data["Beauty & Wellness"] = pd.read_excel(psychometry_data_location, sheet_name=30)
psychometry_data["Capital Goods"] = pd.read_excel(psychometry_data_location, sheet_name=31)
psychometry_data["Construction"] = pd.read_excel(psychometry_data_location, sheet_name=32)
psychometry_data["BFSI"] = pd.read_excel(psychometry_data_location, sheet_name=27)
psychometry_data["HealthCare"] = pd.read_excel(psychometry_data_location, sheet_name=24)
psychometry_data["Automotive"] = pd.read_excel(psychometry_data_location, sheet_name=22)
psychometry_data["Green Jobs"] = pd.read_excel(psychometry_data_location, sheet_name=21)
psychometry_data["Furniture & Fittings"] = pd.read_excel(psychometry_data_location, sheet_name=18)
psychometry_data["Multimedia"] = pd.read_excel(psychometry_data_location, sheet_name=17)
psychometry_data["Media and Journalism"] = pd.read_excel(psychometry_data_location, sheet_name=13)
psychometry_data["Tourism and Hospitality"] = pd.read_excel(psychometry_data_location, sheet_name=10)
psychometry_data["Logistics"] = pd.read_excel(psychometry_data_location, sheet_name=8)
psychometry_data["Life Sciences"] = pd.read_excel(psychometry_data_location, sheet_name=7)

psychometry_sectors_available = list(psychometry_data.keys())
print(f"Sectors:",psychometry_sectors_available, f": {len(psychometry_sectors_available)} total sectors added to API")






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
    return f"<h2>Welcome to the JKYSE API for Psychometry!</h2><br>Total sectors added to API: {len(psychometry_sectors_available)}<br> Sectors added to API: {psychometry_sectors_available}<br><br><h3> To Fetch Question Bank (/GET)</h3> Sample CURL: http://127.0.0.1:5000/api/v1/questionBank?sectors=[\"IT-ITes\", \"Automotive\", \"AI\"]&numQuestionsInEachSector=2"



# Route for a questionBank endpoint
@app.route("/api/v1/questionBank", methods=["GET"])
@cross_origin()
def returnQuestionBank():
    #print("Received Sectors:" + str(request.args.get("sectors")))
    sectors =  json.loads(request.args.get("sectors", "[\"IT-ITeS\"]"))
    num_questions_needed =  int(request.args.get("numQuestionsInEachSector", 1))
    for s in sectors:
        if not s in psychometry_sectors_available:
            return json.dumps({"status":"fail", "message": f"Error - One or more sector not found intgerated with API:>, {s}!"})


    all_questions = []
    question_bank = dict()

    for key_num, key in tqdm(enumerate(sectors)):
        question_bank["sector"] = str(key).strip()
        question_bank["data"] = []

        for i in range(psychometry_data[key].shape[0]):
            if num_questions_needed > psychometry_data[key].shape[0]:
                num_questions_needed = psychometry_data[key].shape[0]
            question = psychometry_data[key]["Question Statement"].iloc[i].strip()
            question_difficulty = psychometry_data[key]["Difficulty level"].iloc[i]
            options = dict()

            #add foreign langs sheet here
            options["option1"] = str(psychometry_data[key]["Option 1"].iloc[i]).strip()
            options["option2"] = str(psychometry_data[key]["Option 2"].iloc[i]).strip()
            options["option3"] = str(psychometry_data[key]["Option 3"].iloc[i]).strip()
            options["option4"] = str(psychometry_data[key]["Option 4"].iloc[i]).strip()
            correct_option = psychometry_data[key]["Correct Answer"].iloc[i]
            prepared_question = prepare_question(key,i+1,question,["MCQ",4,question_difficulty],list(options.values()), correct_option)
            question_bank["data"].append(prepared_question.copy())
        random.shuffle(question_bank["data"])
        question_bank["data"] = random.sample(question_bank["data"], num_questions_needed)


        all_questions.append((question_bank.copy()))
        return_value = dict()
    return_value["status"] = "success"
    return_value["message"] = all_questions
    return json.dumps(return_value, indent=4)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)

