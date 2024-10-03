


#PANDAS NUMPY
import pandas as pd

#TQDM, AND UTILS
import time
from tqdm import tqdm
import random


#FLASK PART
from flask import Flask, jsonify, request
from flask_cors import cross_origin
import json
app = Flask(__name__)


#BERT PART
from transformers import BertTokenizer, BertModel
import torch
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
model.eval()


#get saved embeddings of all sectors
def get_embedding_vector_all_NSDC_sectors(NSDC_sectors_embeddings_path):
    NSDC_ALL_SECTOR_NAMES = []
    NSDC_ALL_SECTORS_EMBEDDINGS = dict()
    NSDC_sectors = pd.read_csv(NSDC_sectors_embeddings_path)
    for i in range(NSDC_sectors.shape[0]):
        s_name = NSDC_sectors['SECTOR_NAME'].iloc[i]
        emb_path = NSDC_sectors['EMBEDDING_PATH'].iloc[i]
        embedding_tensor = torch.load(emb_path)
        NSDC_ALL_SECTOR_NAMES.append(s_name)
        NSDC_ALL_SECTORS_EMBEDDINGS[s_name] = embedding_tensor
    return NSDC_ALL_SECTOR_NAMES, NSDC_ALL_SECTORS_EMBEDDINGS
NSDC_sectors_embeddings_path = "./utils/embeddings/NSDC_sectors/NSDC_sectors_metadata.csv"
NSDC_ALL_SECTOR_NAMES, NSDC_ALL_SECTORS_EMBEDDINGS = get_embedding_vector_all_NSDC_sectors(NSDC_sectors_embeddings_path)





#PSYCHOMETRIC TEST related
#LOAD DATA
print("Loading Questions for Psychometry")
psychometry_SECTORS_MAPPING = dict()
psychometry_SECTORS_MAPPING = dict()
psychometry_SECTORS_MAPPING['Aerospace & Aviation'] = 39
psychometry_SECTORS_MAPPING['Agriculture'] = 38
psychometry_SECTORS_MAPPING['Apparel, Made-Ups & Home Furnishing'] = 29
psychometry_SECTORS_MAPPING['Automotive'] = 22
psychometry_SECTORS_MAPPING['Beauty & Wellness'] = 30
psychometry_SECTORS_MAPPING['BFSI'] = 27
psychometry_SECTORS_MAPPING['Capital Goods'] = 31
psychometry_SECTORS_MAPPING['Construction'] = 32
psychometry_SECTORS_MAPPING['Domestic Works'] = 33
psychometry_SECTORS_MAPPING['Electronics'] = 23
psychometry_SECTORS_MAPPING['Food Processing'] = 25
psychometry_SECTORS_MAPPING['Furniture & Fittings'] = 18
psychometry_SECTORS_MAPPING['Green Jobs'] = 21
psychometry_SECTORS_MAPPING['Gem & Jewellery'] = 19
psychometry_SECTORS_MAPPING['Handicrafts and Carpet'] = 20
psychometry_SECTORS_MAPPING['Hydrocarbons'] = 3
psychometry_SECTORS_MAPPING['HealthCare'] = 24
psychometry_SECTORS_MAPPING['Iron and Steel'] = 35
psychometry_SECTORS_MAPPING['Infrastructure Equipment'] = 34
psychometry_SECTORS_MAPPING['Instrumentation Automation Surveillance & Communication'] = 22
psychometry_SECTORS_MAPPING['IT-ITeS'] = 0
psychometry_SECTORS_MAPPING['Leather'] = 36
psychometry_SECTORS_MAPPING['Life Sciences'] = 7
psychometry_SECTORS_MAPPING['Logistics'] = 8
psychometry_SECTORS_MAPPING['Management & Entrepreneurship and Professional Skills'] = 14
psychometry_SECTORS_MAPPING['Media and Journalism'] = 13
psychometry_SECTORS_MAPPING['Mining'] = 9
psychometry_SECTORS_MAPPING['Power and Electrical'] = 1
psychometry_SECTORS_MAPPING['Persons with Disability'] = 5
psychometry_SECTORS_MAPPING['Retail'] = 2
psychometry_SECTORS_MAPPING['Rubber, Chemical and Petrochemical'] = 3
psychometry_SECTORS_MAPPING['Sports, Physical Education, Fitness & Leisure'] = 4
psychometry_SECTORS_MAPPING['Telecom'] = 6
psychometry_SECTORS_MAPPING['Textile'] = 11
psychometry_SECTORS_MAPPING['Tourism and Hospitality'] = 10
psychometry_SECTORS_MAPPING['Water Management and Plumbing'] = 12

psychometry_data_location= "../db/Sample question_ALL_courses.xlsx"
psychometry_data = dict()
for sn, sv in psychometry_SECTORS_MAPPING.items():
    if not sv == -1:
        psychometry_data[sn] = pd.read_excel(psychometry_data_location, sheet_name=sv)

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

def get_bert_embedding(text):
    # Tokenize input text and convert to PyTorch tensors
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    # Get the embeddings for the [CLS] token
    embeddings = outputs.last_hidden_state[:, 0, :].squeeze()
    return embeddings


def find_closest_key(query_embedding, embeddings):
    max_similarity = -1  # Initialize to a low value
    closest_key = None

    for key, embedding in embeddings.items():
        # Calculate cosine similarity
        similarity = torch.nn.functional.cosine_similarity(query_embedding.unsqueeze(0), embedding.unsqueeze(0))
        
        # Update closest key if the current similarity is greater
        if similarity > max_similarity:
            max_similarity = similarity
            closest_key = key

    return closest_key

def nearest_match_NSDC_sector(key):
    query_embedding = get_bert_embedding(key)
    closest_key = find_closest_key(query_embedding, NSDC_ALL_SECTORS_EMBEDDINGS)
    return closest_key





# Route for the root URL
@app.route("/",methods=["GET"])
@cross_origin()
def home():
    return f"<h2>Welcome to the JKYSE API for Psychometry!</h2><br>Total sectors added to API: {len(psychometry_sectors_available)}<br> Sectors added to API: {psychometry_sectors_available}<br><br><h3> To Fetch Question Bank (/GET)</h3> Sample CURL: http://127.0.0.1:5000/api/v1/questionBank?sectors=[\"IT-ITes\", \"Automotive\", \"AI\"]&numQuestionsInEachSector=2"



# Route for a questionBank endpoint
@app.route("/api/v1/questionBank", methods=["POST"])
@cross_origin()
def returnQuestionBank():
    #print("Received Sectors:" + str(request.args.get("sectors")))
    data = request.get_json()
    sectors = data['sectors']
    num_questions_needed = int(data['numQuestionsInEachSector'])
    #sectors =  json.loads(request.args.get("sectors", "[\"IT-ITeS\"]"))
    #num_questions_needed =  int(request.args.get("numQuestionsInEachSector", 1))
    #for s in sectors:
    #    if not s in psychometry_sectors_available:
    #        return json.dumps({"status":"fail", "message": f"Error - One or more sector not found intgerated with API:>, {s}!"})


    all_questions = []
    question_bank = dict()

    for key_num, key in tqdm(enumerate(sectors)):
        question_bank["sector"] = str(key).strip()
        question_bank["data"] = []

        #IF key:SECTOR IS NOT IN list(psychometry_SECTORS_MAPPING.keys()):
            #FIND THE EMBEDDING OF KEY
            #GET NEASREST MATCH OF KEY, CALL THAT KEY
        if str(key).strip() not in list(psychometry_SECTORS_MAPPING.keys()):
            key = nearest_match_NSDC_sector(key)


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

