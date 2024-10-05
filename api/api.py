#FLASK PART
from flask import Flask, jsonify, request, render_template
from flask_cors import cross_origin, CORS
import json
app = Flask(__name__)
CORS(app)

#PANDAS NUMPY database
import pandas as pd
import psycopg2

#TQDM, AND UTILS
import time
from tqdm import tqdm
import random




#BERT PART
from transformers import BertTokenizer, BertModel
import torch
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
model.eval()







#********************************************************
# GENERAL 
# ******************************************************
#get saved embeddings of all sectors
def get_embedding_vector_all_available_sectors(embedding_metadata_path):
    ALL_AVAILABLE_SECTOR_NAMES = []
    ALL_AVAILABLE_SECTOR_EMBEDDINGS = dict()
    Available_sectors = pd.read_csv(embedding_metadata_path)
    for i in range(Available_sectors.shape[0]):
        s_name = Available_sectors['SECTOR_NAME'].iloc[i]
        emb_path = Available_sectors['EMBEDDING_PATH'].iloc[i]
        embedding_tensor = torch.load(emb_path)
        ALL_AVAILABLE_SECTOR_NAMES.append(s_name)
        ALL_AVAILABLE_SECTOR_EMBEDDINGS[s_name] = embedding_tensor
    return ALL_AVAILABLE_SECTOR_NAMES, ALL_AVAILABLE_SECTOR_EMBEDDINGS

NSDC_sectors_embeddings_path = "./utils/embeddings/NSDC_sectors/NSDC_sectors_metadata.csv"
NSDC_ALL_SECTOR_NAMES, NSDC_ALL_SECTORS_EMBEDDINGS = get_embedding_vector_all_available_sectors(NSDC_sectors_embeddings_path)


def nearest_match_Available_sector(key, SECTORS):
    print("finding match")
    query_embedding = get_bert_embedding(key)
    closest_key = find_closest_key(query_embedding, SECTORS)
    return closest_key

class POSTGRESQL:
    def __init__(self, host, db, user, password, port):
        self.conn = psycopg2.connect(host=host,database=db,user=user,password=password,port=port)
    def command(self, query):
        cur = self.conn.cursor()
        cur.execute(query)
        results =cur.fetchall()
        cur.close()
        del cur
        return results
    def close(self):
        self.conn.close()

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












# **********************************************************
#PSYCHOMETRIC TEST PART
# **********************************************************
Psychometry_sectors_embeddings_path = "./utils/embeddings/Psychometry_sectors/Psychometry_sectors_metadata.csv"
PSYCHOMERY_ALL_SECTOR_NAMES, PSYCHOMETRY_ALL_SECTORS_EMBEDDINGS = get_embedding_vector_all_available_sectors(Psychometry_sectors_embeddings_path)
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
print(f"Sectors:",psychometry_sectors_available, f": {len(psychometry_sectors_available)} total sectors added to Psychometry part of API")






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







# **********************************************************
# SECTOR SKILL VIDEOS PART
# *********************************************************
## Self Learning COURSES PARAMTERS
SL_sectors_embeddings_path = "./utils/embeddings/SL_sectors/SL_sectors_metadata.csv"
SL_ALL_SECTOR_NAMES, SL_ALL_SECTORS_EMBEDDINGS = get_embedding_vector_all_available_sectors(SL_sectors_embeddings_path)

SL_sector_column_name = "sector"
SL_course_column_name = "name of course"
SL_video_title_column_name = "Video Title"
SL_video_link_column_name ="video_link_to_embed"
SL_course_rating_column_name = "Rate this course out of 5 (where 1 is least and 5 is highest)"
SL_basic_advanced_column_name = "Is this course a basic/ intermediate or advanced course?"
SL_link_playing_column_name = "Is link playing?(Yes/No)"
SL_video_relevance_column_name = "Is the video relevant to the course?(Yes/No)"
SL_courses_table_name = "SectorSkillVideo"



def getData_SL_courses(how='postgresql'):
    columns = [SL_sector_column_name, SL_course_column_name, SL_video_title_column_name, SL_video_link_column_name, SL_course_rating_column_name, SL_basic_advanced_column_name, SL_link_playing_column_name, SL_video_relevance_column_name]
    if how == 'postgresql':
        host="13.51.139.148"
        database="jksdm"
        user="umaid"
        password="wordpass"
        port=5432
        table_name= SL_courses_table_name
        postgresql_obj = POSTGRESQL(host,database,user,password,port)
        # # Fetch all table and column names
        # table_columns = postgresql_obj.command("""SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = 'public' ORDER BY table_name, ordinal_position;""")


        # # Display table and column names
        # print("Tables and their columns:")
        # current_table = None
        # for table, column in table_columns:
        #     if table != current_table:
        #         print(f"\nTable: {table}")
        #         current_table = table
        #     print(f" - Column: {column}")
        # postgresql_obj.close()
        string = ""
        for c in columns:
            string += "\""+c+"\","
        #print(string[0:-1])
        #column_names = '"sector", "name of course", "Video Title", "video_link_to_embed", "Rate this course out of 5 (where 1 is least and 5 is highest)", "Is this course a basic/ intermediate or advanced course?", "Is link playing?(Yes/No)", "Is the video relevant to the course?(Yes/No)"'
        column_names = string[0:-1]       
        query = "SELECT " + column_names + " FROM " + '"'+table_name+'"'
        results = postgresql_obj.command(query)
        data_SL_courses = pd.DataFrame(results, columns = columns)
        postgresql_obj.close()
        return data_SL_courses
    else:
        file_path_to_load_SL_courses = "../db/UAT-SectorSkillVideosMerged.csv"
        data_from_csv = pd.read_csv(file_path_to_load_SL_courses)
        data_SL_courses = data_from_csv[columns]
        return data_SL_courses

def get_sector_wise_basic_advanced_SL_courses(SL_courses_df):
    SL_courses_df_filtered = SL_courses_df[SL_courses_df[SL_basic_advanced_column_name]!=''] #non-empty Basic/Advanced Property
    sectors = list(SL_courses_df_filtered[SL_sector_column_name].unique())       
    print('STRUCTURING THE COURSES INTO BASIC AND ADVANCED TYPES')
    SL_BASIC_ADVANCED_MAPPING = dict()
    for sector in sectors:
        SL_BASIC_ADVANCED_MAPPING[sector]= {'BASIC':[], 'ADVANCED':[]}
        SL_sectored_videos = SL_courses_df_filtered[SL_courses_df_filtered[SL_sector_column_name]== sector]
        SL_courses_names_in_a_sector = list(SL_sectored_videos[SL_course_column_name].unique())
        for course in SL_courses_names_in_a_sector:
            SL_coursed_videos = SL_sectored_videos[SL_sectored_videos[SL_course_column_name]== course]
            all_videos_in_the_SL_course = SL_coursed_videos[[SL_video_title_column_name,SL_video_link_column_name]].values.tolist()
            
            basic_or_advanced_value_of_the_course = SL_coursed_videos[SL_basic_advanced_column_name].sample(1).iloc[0]
            #print(course,basic_or_advanced_value_of_the_course)
            
            
            
            if str(basic_or_advanced_value_of_the_course).lower() == 'basic':
                SL_BASIC_ADVANCED_MAPPING[sector]['BASIC'].append({'SL_course_title':course, 'SL_videos_in_course':all_videos_in_the_SL_course})
            if str(basic_or_advanced_value_of_the_course).lower() == 'advanced' or str(basic_or_advanced_value_of_the_course).lower() == 'intermediate':
                SL_BASIC_ADVANCED_MAPPING[sector]['ADVANCED'].append({'SL_course_title':course, 'SL_videos_in_course':all_videos_in_the_SL_course})
    
    #AI rated courses
    with open("../db/AI_UAT_SL_courses.json", "r") as file:
        SL_BASIC_ADVANCED_MAPPING.update(json.load(file))      
#     for s in SL_BASIC_ADVANCED_MAPPING.keys():
#         print('#######\nSectorName:- ',s, '; Basic.Courses:-',len(SL_BASIC_ADVANCED_MAPPING[s]['BASIC']) , '; Advanced.Courses:-',len(SL_BASIC_ADVANCED_MAPPING[s]['ADVANCED']),end='')
        
#         summa = 0
#         for c_idx in range(len(SL_BASIC_ADVANCED_MAPPING[s]['BASIC'])):
#             summa += len(SL_BASIC_ADVANCED_MAPPING[s]['BASIC'][c_idx]['SL_videos_in_course'])
#         print('; Basic.Videos:-', summa, end='')
#         summa = 0
#         for c_idx in range(len(SL_BASIC_ADVANCED_MAPPING[s]['ADVANCED'])):
#             summa += len(SL_BASIC_ADVANCED_MAPPING[s]['ADVANCED'][c_idx]['SL_videos_in_course'])
#         print('; Advanced.Videos:-', summa, end='')
        
       
    return SL_BASIC_ADVANCED_MAPPING



data_SL_courses = getData_SL_courses(how='csv')
#The following can be used to filter the available links and relevant links ONLY
data_SL_courses = data_SL_courses[(data_SL_courses[SL_link_playing_column_name] =='Yes')&(data_SL_courses[SL_video_relevance_column_name] =='Yes')]


#GET THE BASIC ADVANCED MAPPING
SL_BASIC_ADVANCED_MAPPING = get_sector_wise_basic_advanced_SL_courses(data_SL_courses)





#**********************************************
### CERTIFIED COURSES PART
#**********************************************
CC_sectors_embeddings_path = "./utils/embeddings/CC_sectors/CC_sectors_metadata.csv"
CC_ALL_SECTOR_NAMES, CC_ALL_SECTORS_EMBEDDINGS = get_embedding_vector_all_available_sectors(CC_sectors_embeddings_path)


CC_sector_column_name = "Sector"
CC_course_column_name = "Name Of Course"
CC_description = "Required Description"
CC_link = "For Certification Advanced Module"
CC_courses_table_name = "CertifiedCourses"

def getData_Certified_courses(how='postgresql'):
    columns = [CC_sector_column_name, CC_course_column_name, CC_description, CC_link]
    if how == 'postgresql':
        host="13.51.139.148"
        database="jksdm"
        user="umaid"
        password="wordpass"
        port=5432
        table_name= CC_courses_table_name
        postgresql_obj = POSTGRESQL(host,database,user,password,port)
        string = ""
        for c in columns:
            string += "\""+c+"\","
        column_names = string[0:-1]       
        query = "SELECT " + column_names + " FROM " + '"'+table_name+'"'
        results = postgresql_obj.command(query)
        data_CC_courses = pd.DataFrame(results, columns = columns)
        postgresql_obj.close()
        return data_CC_courses
    else:
        file_path_to_load_CC_courses = "../db/CertifiedCourses.csv"
        data_from_csv = pd.read_csv(file_path_to_load_CC_courses)
        data_CC_courses = data_from_csv[columns]
        return data_CC_courses

data_CC_courses = getData_Certified_courses(how='csv')



def get_sector_wise_Certified_courses(CC_courses_df):
    print('STRUCTURING THE CERTIFIED COURSES')
    CC_COURSES_MAPPING = dict()
    for s in list(CC_courses_df[CC_sector_column_name].unique()):
        CC_COURSES_MAPPING[s] = []

    for i in range(data_CC_courses.shape[0]):
        sector_name = data_CC_courses[CC_sector_column_name].iloc[i]
        course_name = data_CC_courses[CC_course_column_name].iloc[i]
        course_description = data_CC_courses[CC_description].iloc[i]
        course_link = data_CC_courses[CC_link].iloc[i]
        CC_COURSES_MAPPING[sector_name].append({'CC_course_title':course_name, 'CC_course_description':course_description, 'CC_course_link':course_link})
    return CC_COURSES_MAPPING
    
CC_COURSES_MAPPING = get_sector_wise_Certified_courses(data_CC_courses)


#************************************
######## DPR PART
#*************************************


#**********************************************
### CERTIFIED COURSES PART
#**********************************************
DPR_sectors_embeddings_path = "./utils/embeddings/DPR_sectors/DPR_sectors_metadata.csv"
DPR_ALL_SECTOR_NAMES, DPR_ALL_SECTORS_EMBEDDINGS = get_embedding_vector_all_available_sectors(DPR_sectors_embeddings_path)


DPR_sector_column_name = "Sector"
DPR_title_column_name = "Project Name"
DPR_description = "Required Description"
DPR_link = "View Profile"
DPR_table_name = "DPRTable"

def getData_DPR(how='postgresql'):
    columns = [DPR_sector_column_name, DPR_title_column_name, DPR_link]
    if how == 'postgresql':
        host="13.51.139.148"
        database="jksdm"
        user="umaid"
        password="wordpass"
        port=5432
        table_name= DPR_table_name
        postgresql_obj = POSTGRESQL(host,database,user,password,port)
        string = ""
        for c in columns:
            string += "\""+c+"\","
        column_names = string[0:-1]       
        query = "SELECT " + column_names + " FROM " + '"'+table_name+'"'
        results = postgresql_obj.command(query)
        data_DPR_courses = pd.DataFrame(results, columns = columns)
        postgresql_obj.close()
        return data_DPR_courses
    else:
        file_path_to_load_DPR_courses = "../db/DPRs-distinct.csv"
        data_from_csv = pd.read_csv(file_path_to_load_DPR_courses)
        data_DPR_courses = data_from_csv[columns]
        return data_DPR_courses

data_DPR_courses = getData_DPR(how='csv')



def get_sector_wise_DPR(DPR_courses_df):
    print('STRUCTURING THE DPRs')
    DPR_MAPPING = dict()
    for s in list(DPR_courses_df[DPR_sector_column_name].unique()):
        DPR_MAPPING[s] = []

    for i in range(data_DPR_courses.shape[0]):
        dpr_sector_name = data_DPR_courses[DPR_sector_column_name].iloc[i]
        dpr_name = data_DPR_courses[DPR_title_column_name].iloc[i]
        dpr_link = data_DPR_courses[DPR_link].iloc[i]
        DPR_MAPPING[dpr_sector_name].append({'DPR_title':dpr_name, 'DPR_link':dpr_link})
    return DPR_MAPPING
    
DPR_MAPPING = get_sector_wise_DPR(data_DPR_courses)


# Route for the root URL
@app.route("/ap1/v1",methods=["GET"])
@cross_origin()
def homeAPI():
    return f"<h2>Welcome to the JKYSE API for Psychometry!<h3> To Fetch Question Bank (/GET)</h3> Sample CURL: http://127.0.0.1:5000/api/v1/questionBank?sectors=[\"IT-ITes\", \"Automotive\", \"AI\"]&numQuestionsInEachSector=2"



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
            key = nearest_match_Available_sector(key, PSYCHOMETRY_ALL_SECTORS_EMBEDDINGS)
            


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





@app.route("/api/v1/RecommendSelfLearningCoursesAfterPsychometry", methods=["POST"])
@cross_origin()
def recommendSLCoursesAfterPsychometry():
    #sectors_and_marks =  json.loads(request.args.get("sectors", "[\"IT-ITes\":\"0.5\"]"))
    sectors_and_marks = request.get_json()
    #sort the keys
    sorted_sectors = sorted(sectors_and_marks, key=sectors_and_marks.get, reverse=True)
    #mapping_sector_to_type_of_course = dict()
    RESULTANT_COURSES = []
    HOW_MANY_COURSES_TO_RECOMMEND_IN_EACH_SECTOR = 5
    for s in sorted_sectors:
        marks_in_sector = sectors_and_marks[s]
        recommend_for = 'BASIC'
        if marks_in_sector >=0.5:
            print('advanced recommended')
            recommend_for = 'ADVANCED'
        else:
            print('basic recommened')
            recommend_for = 'BASIC'
        

        #for (sector_name, marks) in sectors_and_marks.items():
        sector_name = s
        if sector_name not in list(SL_BASIC_ADVANCED_MAPPING.keys()):
            sector_name = nearest_match_Available_sector(sector_name, SL_ALL_SECTORS_EMBEDDINGS)
        
        if len(SL_BASIC_ADVANCED_MAPPING[sector_name][recommend_for]) < HOW_MANY_COURSES_TO_RECOMMEND_IN_EACH_SECTOR:
            HOW_MANY_COURSES_TO_RECOMMEND_IN_EACH_SECTOR = len(SL_BASIC_ADVANCED_MAPPING[sector_name][recommend_for]) 
        
        #FIND CLOSEST MATCH TO SECTOR sector_name CALL IT sector_name2 AND USE sector_name2 BELOW
        #

        #print(sector_name)
        #print(SL_BASIC_ADVANCED_MAPPING[sector_name], recommend_for)
       
        RESULTANT_COURSES.append([SL_BASIC_ADVANCED_MAPPING[sector_name][recommend_for][:HOW_MANY_COURSES_TO_RECOMMEND_IN_EACH_SECTOR]])
        #print(sectors_and_marks, type(sectors_and_marks))
    #print(RESULTANT_COURSES)
    return RESULTANT_COURSES




@app.route("/api/v1/RecommendCertifiedCoursesAfterPsychometry", methods=["POST"])
@cross_origin()
def recommendCertifiedCoursesAfterPsychometry():   
    #sectors_and_marks =  json.loads(request.args.get("sectors", "[\"IT-ITes\":\"0.5\"]"))
    sectors_and_marks = request.get_json()
    print(sectors_and_marks)
    #sort the keys
    sorted_sectors = sorted(sectors_and_marks, key=sectors_and_marks.get, reverse=True)
    #mapping_sector_to_type_of_course = dict()
    RESULTANT_COURSES = []
    HOW_MANY_COURSES_TO_RECOMMEND_IN_EACH_SECTOR = 5
    
    
    for s in sorted_sectors:
        #marks_in_sector = sectors_and_marks[s]
        #for (sector_name, marks) in sectors_and_marks.items():
        sector_name = s
        if sector_name not in list(CC_COURSES_MAPPING.keys()):
            sector_name = nearest_match_Available_sector(sector_name, CC_ALL_SECTORS_EMBEDDINGS)

        if len(CC_COURSES_MAPPING[sector_name]) < HOW_MANY_COURSES_TO_RECOMMEND_IN_EACH_SECTOR:
            HOW_MANY_COURSES_TO_RECOMMEND_IN_EACH_SECTOR = len(CC_COURSES_MAPPING[sector_name])
        
        print(HOW_MANY_COURSES_TO_RECOMMEND_IN_EACH_SECTOR)
        RESULTANT_COURSES.append({'Sector':sector_name, 'Course Details': random.sample(CC_COURSES_MAPPING[sector_name],HOW_MANY_COURSES_TO_RECOMMEND_IN_EACH_SECTOR)})
        #print(sectors_and_marks, type(sectors_and_marks))
    #print(RESULTANT_COURSES)
    
    return RESULTANT_COURSES




@app.route("/api/v1/RecommendDPRAfterPsychometry", methods=["POST"])
@cross_origin()
def recommendDPRsAfterPsychometry():   
    #sectors_and_marks =  json.loads(request.args.get("sectors", "[\"IT-ITes\":\"0.5\"]"))
    sectors_and_marks = request.get_json()
    print(sectors_and_marks)
    #sort the keys
    sorted_sectors = sorted(sectors_and_marks, key=sectors_and_marks.get, reverse=True)
    #mapping_sector_to_type_of_course = dict()
    RESULTANT_DPR = []
    HOW_MANY_DPR_TO_RECOMMEND_IN_EACH_SECTOR = 5
    
    
    for s in sorted_sectors:
        #marks_in_sector = sectors_and_marks[s]
        #for (sector_name, marks) in sectors_and_marks.items():
        sector_name = s
        if sector_name not in list(DPR_MAPPING.keys()):
            sector_name = nearest_match_Available_sector(sector_name, DPR_ALL_SECTORS_EMBEDDINGS)

        if len(DPR_MAPPING[sector_name]) < HOW_MANY_DPR_TO_RECOMMEND_IN_EACH_SECTOR:
            HOW_MANY_DPR_TO_RECOMMEND_IN_EACH_SECTOR = len(DPR_MAPPING[sector_name])
        
        print(HOW_MANY_DPR_TO_RECOMMEND_IN_EACH_SECTOR)
        RESULTANT_DPR.append({'Sector':sector_name, 'DPR Details': random.sample(DPR_MAPPING[sector_name],HOW_MANY_DPR_TO_RECOMMEND_IN_EACH_SECTOR)})
        #print(sectors_and_marks, type(sectors_and_marks))
    #print(RESULTANT_COURSES)
    
    return RESULTANT_DPR




@app.route("/api/v1/RecommendFLAfterPsychometry", methods=["POST"])
@cross_origin()
def recommendFLAfterPsychometry():   
    #sectors_and_marks =  json.loads(request.args.get("sectors", "[\"IT-ITes\":\"0.5\"]"))
    sectors_and_marks = request.get_json()
    print(sectors_and_marks)
    #sort the keys
    sorted_sectors = sorted(sectors_and_marks, key=sectors_and_marks.get, reverse=True)
    #mapping_sector_to_type_of_course = dict()
    RESULTANT_DPR = []
    HOW_MANY_DPR_TO_RECOMMEND_IN_EACH_SECTOR = 5
    
    
    for s in sorted_sectors:
        #marks_in_sector = sectors_and_marks[s]
        #for (sector_name, marks) in sectors_and_marks.items():
        sector_name = s
        if sector_name not in list(DPR_MAPPING.keys()):
            sector_name = nearest_match_Available_sector(sector_name, DPR_ALL_SECTORS_EMBEDDINGS)

        if len(DPR_MAPPING[sector_name]) < HOW_MANY_DPR_TO_RECOMMEND_IN_EACH_SECTOR:
            HOW_MANY_DPR_TO_RECOMMEND_IN_EACH_SECTOR = len(DPR_MAPPING[sector_name])
        
        print(HOW_MANY_DPR_TO_RECOMMEND_IN_EACH_SECTOR)
        RESULTANT_DPR.append({'Sector':sector_name, 'DPR Details': random.sample(DPR_MAPPING[sector_name],HOW_MANY_DPR_TO_RECOMMEND_IN_EACH_SECTOR)})
        #print(sectors_and_marks, type(sectors_and_marks))
    #print(RESULTANT_COURSES)
    
    return RESULTANT_DPR






@app.route("/")
def home():
    # Render the index.html file
    return render_template('index_with_params.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)

